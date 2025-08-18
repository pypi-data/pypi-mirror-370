"""The classes to run the plan task"""
import logging
from multiprocessing import Pool

from astroplan import moon_illumination, Constraint
import os
import shutil
import astroplan
import matplotlib
from astroplan.plots import plot_airmass
from astropy.coordinates import SkyCoord, get_body
import astropy.units as u
from astroplan import EclipsingSystem
import pandas as pd
import numpy as np
from astroplan import (Observer, FixedTarget, AtNightConstraint, AltitudeConstraint)
import matplotlib.pyplot as plt

from astropy.time import Time, TimeDelta
from timezonefinder import TimezoneFinder
from pytz import timezone, utc


class MoonIlluminationSeparationConstraint(Constraint):
    """
    Constrain the distance between the Earth's moon and some targets.
    """

    def __init__(self, min_dist, max_dist):
        """
        Parameters
        ----------
        min_dist : `~astropy.units.Quantity`
            Minimum moon distance when moon illumination is 0
        max_dist : `~astropy.units.Quantity`
            Maximum moon distance when moon illumination is 1
        """
        self.min_dist = min_dist
        self.max_dist = max_dist

    def compute_constraint(self, times, observer, targets):
        """
        Computes the observability of the moon given a minimum distance to the moon between self.min_dist (for
        illumination = 0) and self.max_dist (for illumination = 1) by interpolating an intermediate distance from those
        two values following a linear regression.

        :param times: the times to compute the constraint for
        :param observer: the observer to compute the constraint for
        :param targets: the list of targets to compute the constraint for
        :return: the positive mask for target being observable for the given times and observer given the constraint is matched
        """
        # removed the location argument here, which causes small <1 deg
        # inaccuracies, but it is needed until astropy PR #5897 is released
        # which should be astropy 1.3.2
        moon = get_body("moon", times)
        # note to future editors - the order matters here
        # moon.separation(targets) is NOT the same as targets.separation(moon)
        # the former calculates the separation in the frame of the moon coord
        # which is GCRS, and that is what we want.
        moon_separation = moon.separation(targets)
        illumination = moon_illumination(times)
        min_dist = self.min_dist.value + (self.max_dist.value - self.min_dist.value) * illumination
        mask = min_dist <= moon_separation.degree
        return mask


class PlannerInput:
    def __init__(self, observatory_row, midtransit_time, observer_site, midtransit_times, ingress_egress_times,
                 constraints, moon_for_midtransit_times, moon_dist_midtransit_times, moon_phase_midtransit_times,
                 transits_since_epoch, midtransit_time_low_err, midtransit_time_up_err, low_err_delta,
                 up_err_delta, i, plan_dir, target, min_altitude, transit_fraction, baseline,
                 error_alert) -> None:
        self.observatory_row = observatory_row
        self.midtransit_time = midtransit_time
        self.observer_site = observer_site
        self.midtransit_times = midtransit_times
        self.ingress_egress_times = ingress_egress_times
        self.constraints = constraints
        self.moon_for_midtransit_times = moon_for_midtransit_times
        self.moon_dist_midtransit_times = moon_dist_midtransit_times
        self.moon_phase_midtransit_times = moon_phase_midtransit_times
        self.transits_since_epoch = transits_since_epoch
        self.midtransit_time_low_err = midtransit_time_low_err
        self.midtransit_time_up_err = midtransit_time_up_err
        self.low_err_delta = low_err_delta
        self.up_err_delta = up_err_delta
        self.i = i
        self.plan_dir = plan_dir
        self.target = target
        self.min_altitude = min_altitude
        self.transit_fraction = transit_fraction
        self.baseline = baseline
        self.error_alert = error_alert


class Planner:
    """
    Class containing the main method to generate the observation plan events.
    """

    @staticmethod
    def create_observation_observables(object_id, object_dir, ra, dec, since, name, epoch, epoch_low_err, epoch_up_err,
                                       period, period_low_err, period_up_err, duration,
                                       observatories_file, timezone, latitude, longitude, altitude,
                                       max_days, min_altitude, moon_min_dist, moon_max_dist, transit_fraction, baseline,
                                       error_alert=True, time_unit='jd', cpus=os.cpu_count() - 1):
        """
        Computes the observation windows for the given target parameters.

        :param object_id: the candidate id
        :param object_dir: the candidate directory
        :param ra: right ascension of the target
        :param dec: declination of the target
        :param since: starting plan date
        :param name: the name given to the candidate
        :param epoch: the candidate epoch
        :param epoch_low_err: the candidate epoch's lower error
        :param epoch_up_err: the candidate epoch's upper error
        :param period: the candidate period
        :param period_low_err: the candidate period's lower error
        :param period_up_err: the candidate period's upper error
        :param duration: the candidate duration
        :param observatories_file: the file containing the observatories file (csv format)
        :param timezone: the timezone of the observatory (if observatories_file=None)
        :param latitude: the latitude of the observatory (if observatories_file=None)
        :param longitude: the longitude of the observatory (if observatories_file=None)
        :param altitude: the altitude of the observatory (if observatories_file=None)
        :param max_days: the maximum number of days to compute the observables
        :param min_altitude: the minimum altitude of the target above the horizon
        :param moon_min_dist: the minimum moon distance for moon illumination = 0
        :param moon_max_dist: the minimum moon distance for moon illumination = 1
        :param transit_fraction: the minimum transit observability (0.25 for at least ingress/egress, 0.5 for ingress/egress + midtime, 1 for ingress, egress and midtime).
        :param baseline: the required baseline in hours.
        :param error_alert: whether to create the alert date to signal imprecise observations
        :param time_unit: the unit of the light curve data
        :return: the generated data and target folders observatories_df, observables_df, alert_date, plan_dir, images_dir
        :return: observatories_df containing the observatories used for the computation
        :return: observables_df containing all the observation windows that passed the plan
        :return: alert_date in case the plan reached a date where the observation uncertainty was too high
        :return: images_dir the directory where images are stored
        """
        if observatories_file is not None:
            observatories_df = pd.read_csv(observatories_file, comment='#')
        else:
            observatories_df = pd.DataFrame(columns=['name', 'tz', 'lat', 'long', 'alt'])
            observatories_df = observatories_df.append("Obs-1", timezone, latitude, longitude, altitude)
        # TODO probably convert epoch to proper JD
        primary_eclipse_time = Time(epoch, format=time_unit, scale="tdb")
        target = FixedTarget(SkyCoord(str(ra) + ' ' + str(dec), unit=(u.deg, u.deg)))
        n_transits = int(max_days // period)
        system = EclipsingSystem(primary_eclipse_time=primary_eclipse_time, orbital_period=u.Quantity(period, unit="d"),
                                 duration=u.Quantity(duration, unit="h"), name=name)
        observables_df = pd.DataFrame(columns=['observatory', 'timezone', 'start_obs', 'end_obs', 'ingress', 'egress',
                                               'midtime', "midtime_up_err_h", "midtime_low_err_h", 'twilight_evening',
                                               'twilight_morning', 'observable', 'moon_phase', 'moon_dist'])
        plan_dir = object_dir + "/plan"
        images_dir = plan_dir + "/images"
        if not os.path.exists(plan_dir):
            os.mkdir(plan_dir)
        if os.path.exists(images_dir):
            shutil.rmtree(images_dir, ignore_errors=True)
        os.mkdir(images_dir)
        alert_date = None
        planner_inputs = []
        for index, observatory_row in observatories_df.iterrows():
            if observatory_row['lat'] is None or observatory_row['lat'] == '' or np.isnan(observatory_row['lat']) or \
                (observatory_row['lon'] is None or observatory_row['lon'] == '' or np.isnan(observatory_row['lon']) or \
                 observatory_row['alt'] is None or observatory_row['alt'] == '') or np.isnan(observatory_row['alt']):
                observer_site = None
                constraints = []
            else:
                observer_site = Observer(latitude=observatory_row["lat"], longitude=observatory_row["lon"],
                                         elevation=u.Quantity(observatory_row["alt"], unit="m"))
                constraints = [AtNightConstraint.twilight_nautical(), AltitudeConstraint(min=min_altitude * u.deg)]
            constraints = constraints + [MoonIlluminationSeparationConstraint(min_dist=moon_min_dist * u.deg,
                                                                max_dist=moon_max_dist * u.deg)]
            midtransit_times = system.next_primary_eclipse_time(since, n_eclipses=n_transits)
            ingress_egress_times = system.next_primary_ingress_egress_time(since, n_eclipses=n_transits)
            moon_for_midtransit_times = get_body("moon", midtransit_times)
            moon_dist_midtransit_times = moon_for_midtransit_times.separation(SkyCoord(ra, dec, unit="deg"))
            moon_phase_midtransit_times = np.round(astroplan.moon_illumination(midtransit_times), 2)
            transits_since_epoch = np.round((midtransit_times - primary_eclipse_time).jd / period)
            midtransit_time_low_err = np.round(
                (((transits_since_epoch * period_low_err) ** 2 + epoch_low_err ** 2) ** (1 / 2)) * 24, 2)
            midtransit_time_up_err = np.round(
                (((transits_since_epoch * period_up_err) ** 2 + epoch_up_err ** 2) ** (1 / 2)) * 24, 2)
            low_err_delta = TimeDelta(midtransit_time_low_err * 3600, format='sec')
            up_err_delta = TimeDelta(midtransit_time_up_err * 3600, format='sec')
            i = 0
            for midtransit_time in midtransit_times:
                planner_inputs = planner_inputs + [
                    PlannerInput(observatory_row, midtransit_time, observer_site, midtransit_times,
                                 ingress_egress_times,
                                 constraints, moon_for_midtransit_times, moon_dist_midtransit_times,
                                 moon_phase_midtransit_times,
                                 transits_since_epoch, midtransit_time_low_err, midtransit_time_up_err, low_err_delta,
                                 up_err_delta, i, plan_dir, target, min_altitude, transit_fraction, baseline,
                                 error_alert)]
                i = i + 1
        with Pool(processes=cpus) as pool:
            alert_dates_and_observables = pool.map(Planner.plan_event, planner_inputs)
        alert_dates = [item[0] for item in alert_dates_and_observables]
        alert_date = alert_dates[0] if len(alert_dates) > 0 else None
        for each_alert_date in alert_dates:
            if each_alert_date is not None and each_alert_date < alert_date:
                alert_date = each_alert_date
        observables = [item[1] for item in alert_dates_and_observables]
        for observable in observables:
            if observable is not None:
                observables_df = pd.concat([observables_df, pd.DataFrame([observable])], ignore_index=True)

        observables_df = observables_df.sort_values(["midtime", "observatory"], ascending=True)
        observables_df.to_csv(plan_dir + "/observation_plan.csv", index=False)
        print("Observation plan created in directory: " + object_dir)
        return observatories_df, observables_df, alert_date, plan_dir, images_dir

    @staticmethod
    def plan_event(planner_input: PlannerInput):
        try:
            twilight_evening = None
            twilight_morning = None
            if planner_input.observer_site is not None:
                twilight_evening = planner_input.observer_site.twilight_evening_nautical(planner_input.midtransit_time)
                twilight_morning = planner_input.observer_site.twilight_morning_nautical(planner_input.midtransit_time)
            ingress = planner_input.ingress_egress_times[planner_input.i][0]
            egress = planner_input.ingress_egress_times[planner_input.i][1]
            lowest_ingress = ingress - planner_input.low_err_delta[planner_input.i]
            highest_egress = egress + planner_input.up_err_delta[planner_input.i]
            if planner_input.error_alert and (highest_egress - lowest_ingress).jd > 0.33:
                return (planner_input.midtransit_time , None)
            else:
                baseline_low = lowest_ingress - planner_input.baseline * u.hour
                baseline_up = highest_egress + planner_input.baseline * u.hour
                transit_times = baseline_low + (baseline_up - baseline_low) * np.linspace(0, 1, 100)
                if planner_input.observer_site is None:
                    observable_transit_times = np.full(transit_times.shape, True)
                else:
                    observable_transit_times = astroplan.is_event_observable(planner_input.constraints,
                                                                             planner_input.observer_site,
                                                                             planner_input.target,
                                                                             times=transit_times)[0]
                observable_transit_times_true = np.argwhere(observable_transit_times)
                observable = len(observable_transit_times_true) / 100
                if observable < planner_input.transit_fraction:
                    return (None, None)
                start_obs = transit_times[observable_transit_times_true[0]][0]
                end_obs = transit_times[observable_transit_times_true[len(observable_transit_times_true) - 1]][0]
                start_plot = baseline_low
                end_plot = baseline_up
                # TODO check whether twilight evening happens before twilight morning, if not, the check is different
                if planner_input.observer_site is not None:
                    if twilight_evening > start_obs:
                        start_obs = twilight_evening
                    if twilight_morning < end_obs:
                        end_obs = twilight_morning
            moon_dist = round(planner_input.moon_dist_midtransit_times[planner_input.i].degree)
            moon_phase = planner_input.moon_phase_midtransit_times[planner_input.i]
            # TODO get is_event_observable for several parts of the transit (ideally each 5 mins) to get the proper observable percent. Also with baseline
            if planner_input.observatory_row["tz"] is not None and not np.isnan(planner_input.observatory_row["tz"]):
                observer_timezone = planner_input.observatory_row["tz"]
            else:
                observer_timezone = Planner.get_offset(planner_input.observatory_row["lat"], planner_input.observatory_row["lon"],
                                                       planner_input.midtransit_time.datetime)
            observable_dict = {"observatory": planner_input.observatory_row["name"],
                                                    "timezone": observer_timezone, "ingress": ingress.isot,
                                                    "start_obs": start_obs.isot, "end_obs": end_obs.isot,
                                                    "egress": egress.isot, "midtime": planner_input.midtransit_time.isot,
                                                    "midtime_up_err_h":
                                                        str(int(planner_input.midtransit_time_up_err[planner_input.i] // 1)) + ":" +
                                                        str(int(planner_input.midtransit_time_up_err[planner_input.i] % 1 * 60)).zfill(2),
                                                    "midtime_low_err_h":
                                                        str(int(planner_input.midtransit_time_low_err[planner_input.i] // 1)) + ":" +
                                                        str(int(planner_input.midtransit_time_low_err[planner_input.i] % 1 * 60)).zfill(2),
                                                    "twilight_evening": twilight_evening.isot if twilight_evening is not None else None,
                                                    "twilight_morning": twilight_morning.isot if twilight_morning is not None else None,
                                                    "observable": observable, "moon_phase": moon_phase,
                                                    "moon_dist": moon_dist}
            if planner_input.observer_site is not None:
                plot_time = start_plot + (end_plot - start_plot) * np.linspace(0, 1, 100)
                plt.tick_params(labelsize=6)
                airmass_ax = plot_airmass(planner_input.target, planner_input.observer_site, plot_time, brightness_shading=False,
                                          altitude_yaxis=True)
                airmass_ax.axvspan(twilight_morning.plot_date, end_plot.plot_date, color='white')
                airmass_ax.axvspan(start_plot.plot_date, twilight_evening.plot_date, color='white')
                airmass_ax.axvspan(twilight_evening.plot_date, twilight_morning.plot_date, color='gray')
                airmass_ax.axhspan(1. / np.cos(np.radians(90 - planner_input.min_altitude)), 5.0, color='green')
                airmass_ax.get_figure().gca().set_title("")
                airmass_ax.get_figure().gca().set_xlabel("")
                airmass_ax.get_figure().gca().set_ylabel("")
                airmass_ax.set_xlabel("")
                airmass_ax.set_ylabel("")
                xticks = []
                xticks_labels = []
                xticks.append(start_obs.plot_date)
                hour_min_sec_arr = start_obs.isot.split("T")[1].split(":")
                xticks_labels.append("T1_" + hour_min_sec_arr[0] + ":" + hour_min_sec_arr[1])
                plt.axvline(x=start_obs.plot_date, color="violet")
                xticks.append(end_obs.plot_date)
                hour_min_sec_arr = end_obs.isot.split("T")[1].split(":")
                xticks_labels.append("T1_" + hour_min_sec_arr[0] + ":" + hour_min_sec_arr[1])
                plt.axvline(x=end_obs.plot_date, color="violet")
                if start_plot < lowest_ingress < end_plot:
                    xticks.append(lowest_ingress.plot_date)
                    hour_min_sec_arr = lowest_ingress.isot.split("T")[1].split(":")
                    xticks_labels.append("T1_" + hour_min_sec_arr[0] + ":" + hour_min_sec_arr[1])
                    plt.axvline(x=lowest_ingress.plot_date, color="red")
                if start_plot < ingress < end_plot:
                    xticks.append(ingress.plot_date)
                    hour_min_sec_arr = ingress.isot.split("T")[1].split(":")
                    xticks_labels.append("T1_" + hour_min_sec_arr[0] + ":" + hour_min_sec_arr[1])
                    plt.axvline(x=ingress.plot_date, color="orange")
                if start_plot < planner_input.midtransit_time < end_plot:
                    xticks.append(planner_input.midtransit_time.plot_date)
                    hour_min_sec_arr = planner_input.midtransit_time.isot.split("T")[1].split(":")
                    xticks_labels.append("T0_" + hour_min_sec_arr[0] + ":" + hour_min_sec_arr[1])
                    plt.axvline(x=planner_input.midtransit_time.plot_date, color="black")
                if start_plot < egress < end_plot:
                    xticks.append(egress.plot_date)
                    hour_min_sec_arr = egress.isot.split("T")[1].split(":")
                    xticks_labels.append("T4_" + hour_min_sec_arr[0] + ":" + hour_min_sec_arr[1])
                    plt.axvline(x=egress.plot_date, color="orange")
                if start_plot < highest_egress < end_plot:
                    xticks.append(highest_egress.plot_date)
                    hour_min_sec_arr = highest_egress.isot.split("T")[1].split(":")
                    xticks_labels.append("T4_" + hour_min_sec_arr[0] + ":" + hour_min_sec_arr[1])
                    plt.axvline(x=highest_egress.plot_date, color="red")
                airmass_ax.xaxis.set_tick_params(labelsize=5)
                airmass_ax.set_xticks([])
                airmass_ax.set_xticklabels([])
                degrees_ax = Planner.get_twin(airmass_ax)
                degrees_ax.yaxis.set_tick_params(labelsize=6)
                degrees_ax.set_yticks([1., 1.55572383, 2.])
                degrees_ax.set_yticklabels([90, 50, 30])
                fig = matplotlib.pyplot.gcf()
                fig.set_size_inches(1.25, 0.75)
                plt.savefig(
                    planner_input.plan_dir + "/images/" + planner_input.observatory_row["name"] + "_" +
                    str(planner_input.midtransit_time.isot)[:-4] + ".png",
                    bbox_inches='tight')
                plt.close()
            return (None, observable_dict)
        except Exception as e:
            logging.exception("Error when planning one observation event.")

    @staticmethod
    def get_twin(ax):
        """
        Retrieves a twin Y axis for a given matplotlib axis. This is useful when we have two axes one placed at each side
        of the plot.

        :param ax: the known matplotlib axis.
        :return: the twin axis.
        """
        for other_ax in ax.figure.axes:
            if other_ax is ax:
                continue
            if other_ax.bbox.bounds == ax.bbox.bounds:
                return other_ax
        return None

    @staticmethod
    def get_offset(lat, lng, datetime):
        """
        Returns a location's time zone offset from UTC in minutes.

        :param lat: geographical latitude
        :param lng: geographical longitude
        :param datetime: the UTC time
        """
        tf = TimezoneFinder()
        tz_target = timezone(tf.certain_timezone_at(lng=lng, lat=lat))
        if tz_target is None:
            return None
        today_target = tz_target.localize(datetime)
        today_utc = utc.localize(datetime)
        return (today_utc - today_target).total_seconds() / 3600
