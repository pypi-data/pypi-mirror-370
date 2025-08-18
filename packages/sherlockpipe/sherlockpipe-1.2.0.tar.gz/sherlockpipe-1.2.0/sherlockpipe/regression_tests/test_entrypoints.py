import os
import shutil
import time
import types
import unittest
import pkg_resources
import pytest
from astropy.time import Time

from sherlockpipe.observation_plan.run import run_plan
from sherlockpipe.search.run import run_search
from sherlockpipe.system_stability.run import run_stability
from sherlockpipe.vetting.run import run_vet


@pytest.fixture(autouse=True)
def delay_between_tests():
    print("Sleeping for 1 second before next test")
    time.sleep(10)


class TestsEntrypoints(unittest.TestCase):
    def test_vetting(self):
        object_dir = TestsEntrypoints.get_path('test_endpoints_data/')
        vetting_dir = object_dir + '/vet_1'
        try:
            run_vet(object_dir, 1, None, cpus=4, run_iatson=False)
            self.assertEquals(7, len(os.listdir(vetting_dir)))
            shutil.rmtree(vetting_dir, ignore_errors=True)
            run_vet(object_dir, 1, None, cpus=4, run_iatson=True)
            self.assertEquals(12, len(os.listdir(vetting_dir)))
        finally:
            shutil.rmtree(vetting_dir, ignore_errors=True)

    def test_stability(self):
        object_dir = TestsEntrypoints.get_path('test_endpoints_data/')
        properties_dir = TestsEntrypoints.get_path("test_endpoints_data/stability.yaml")
        args = types.SimpleNamespace()
        args.object_dir = object_dir
        args.properties = properties_dir
        args.cpus = 4
        args.star_mass_bins = 1
        args.period_bins = 1
        args.free_params = None
        args.use_spock = False
        args.years = 50
        args.dt = 0.001
        args.repetitions = 1
        try:
            run_stability(args)
            self.assertEquals(2, len(os.listdir(object_dir + '/stability_stability')))
        finally:
            shutil.rmtree(object_dir + '/stability_stability', ignore_errors=True)

    def test_search(self):
        properties_dir = TestsEntrypoints.get_path("search.yaml")
        results_dir = TestsEntrypoints.get_path("/")
        search_dir = results_dir + "TIC305048087_[2]"
        try:
            run_search(properties_dir, False, results_dir, 4)
            self.assertEquals(18, len(os.listdir(search_dir)))
        finally:
            shutil.rmtree(search_dir, ignore_errors=True)

    #@unittest.skip("Allesfitter is failing loading data: https://github.com/MNGuenther/allesfitter/issues/57")
    def test_plan(self):
        object_dir = TestsEntrypoints.get_path('test_endpoints_data/fit_1/')
        plan_dir = object_dir + 'plan/'
        args = types.SimpleNamespace()
        args.object_dir = object_dir
        args.cpus = 4
        args.observatories = object_dir + 'observatories.csv'
        args.since = Time('2022-10-01', scale='utc')
        args.error_sigma = 1
        args.time_unit = None
        args.tz = 0
        args.lat = None
        args.lon = None
        args.alt = None
        args.max_days = 30
        args.min_altitude = 25
        args.moon_min_dist = 20
        args.moon_max_dist = 40
        args.transit_fraction = 0.5
        args.no_error_alert = True
        args.baseline = 1
        try:
            run_plan(args)
            self.assertEquals(2, len(os.listdir(plan_dir)))
            with open(plan_dir + "observation_plan.csv", 'r') as fp:
                self.assertEquals(8, len(fp.readlines()))
        finally:
            shutil.rmtree(plan_dir, ignore_errors=True)


    @staticmethod
    def get_path(path):
        """
        Gets right path for tests environment
        :param path:
        :return: the real path of the test resource
        """
        return pkg_resources.resource_filename(__name__, path)


if __name__ == '__main__':
    unittest.main()
