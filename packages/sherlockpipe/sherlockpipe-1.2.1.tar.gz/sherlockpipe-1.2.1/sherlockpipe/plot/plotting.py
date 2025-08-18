import matplotlib.pyplot as plt
import numpy as np
from lcbuilder.star.starinfo import StarInfo
from matplotlib.colors import LinearSegmentedColormap
from scipy import stats
import pandas as pd
from sherlockpipe.search.transitresult import TransitResult


def save_transit_plot(object_id: str, title: str, plot_dir: str, file: str, time, lc, transit_result: TransitResult,
                      cadence, run_no: int, plot_harmonics: bool = False):
    """
    Stores the search results plot with: 1) The entire curve with the transit model 2)The folded curve and the transit
    model 3) The power spectrum of the TLS search 4) Only if the flag is enabled, the TLS search harmonics power
    spectrum.

    :param str object_id: the target id
    :param str title: title for the plot
    :param str plot_dir: directory where the plot should be stored
    :param str file: the file name of the plot
    :param time: the time array of the light curve
    :param lc: the flux value of the light curve
    :param TransitResult transit_result: the TransitResult object containing the search results
    :param cadence: the cadence of the curve in days
    :param int run_no: the SHERLOCK run of the results
    :param bool plot_harmonics: whether the harmonics power spectrum should be plotted
    """
    # start the plotting
    rows = 3 if not plot_harmonics else 4
    figsize = 10 if not plot_harmonics else 14
    fig, axs = plt.subplots(nrows=rows, ncols=1, figsize=(10, figsize), constrained_layout=True)
    fig.suptitle(title)
    # 1-Plot all the transits
    in_transit = transit_result.in_transit
    tls_results = transit_result.results
    axs[0].scatter(time[in_transit], lc[in_transit], color='red', s=2, zorder=0)
    axs[0].scatter(time[~in_transit], lc[~in_transit], color='black', alpha=0.05, s=2, zorder=0)
    axs[0].plot(tls_results.model_lightcurve_time, tls_results.model_lightcurve_model, alpha=1, color='red', zorder=1)
    # plt.scatter(time_n, flux_new_n, color='orange', alpha=0.3, s=20, zorder=3)
    plt.xlim(time.min(), time.max())
    # plt.xlim(1362.0,1364.0)
    axs[0].set(xlabel='Time (days)', ylabel='Relative flux')
    # phase folded plus binning
    bins_per_transit = 8
    half_duration_phase = transit_result.duration / 2 / transit_result.period
    if np.isnan(transit_result.period) or np.isnan(transit_result.duration):
        bins = 200
        folded_plot_range = 0.05
    else:
        bins = transit_result.period / transit_result.duration * bins_per_transit
        folded_plot_range = half_duration_phase * 10
    binning_enabled = True
    axs[1].plot(tls_results.model_folded_phase, tls_results.model_folded_model, color='red')
    scatter_measurements_alpha = 0.05 if binning_enabled else 0.8
    axs[1].scatter(tls_results.folded_phase, tls_results.folded_y, color='black', s=10,
                alpha=scatter_measurements_alpha, zorder=2)
    lower_x_limit = 0.5 - folded_plot_range
    upper_x_limit = 0.5 + folded_plot_range
    axs[1].set_xlim(lower_x_limit, upper_x_limit)
    axs[1].set(xlabel='Phase', ylabel='Relative flux')
    folded_phase_zoom_mask = np.argwhere((tls_results.folded_phase > lower_x_limit) &
                                         (tls_results.folded_phase < upper_x_limit)).flatten()
    if isinstance(tls_results.folded_phase, (list, np.ndarray)):
        folded_phase = tls_results.folded_phase[folded_phase_zoom_mask]
        folded_y = tls_results.folded_y[folded_phase_zoom_mask]
        if len(folded_y) > 1 and len(tls_results.model_folded_model) > 1:
            axs[1].set_ylim(np.min([np.min(folded_y), np.min(tls_results.model_folded_model)]),
                     np.max([np.max(folded_y), np.max(tls_results.model_folded_model)]))
        plt.ticklabel_format(useOffset=False)
        bins = 80
        if binning_enabled and tls_results.SDE != 0 and bins < len(folded_phase):
            bin_means, bin_edges, binnumber = stats.binned_statistic(folded_phase, folded_y, statistic='mean',
                                                                     bins=bins)
            bin_stds, _, _ = stats.binned_statistic(folded_phase, folded_y, statistic='std', bins=bins)
            bin_width = (bin_edges[1] - bin_edges[0])
            bin_centers = bin_edges[1:] - bin_width / 2
            bin_size = int(folded_plot_range * 2 / bins * transit_result.period * 24 * 60)
            bin_means_data_mask = np.isnan(bin_means)
            axs[1].errorbar(bin_centers[~bin_means_data_mask], bin_means[~bin_means_data_mask],
                         yerr=bin_stds[~bin_means_data_mask] / 2, xerr=bin_width / 2, marker='o', markersize=4,
                         color='darkorange', alpha=1, linestyle='none', label='Bin size: ' + str(bin_size) + "m")
            axs[1].legend(loc="upper right")
    axs[2].axvline(transit_result.period, alpha=0.4, lw=3)
    axs[2].set_xlim(np.min(tls_results.periods), np.max(tls_results.periods))
    for n in range(2, 10):
        axs[2].axvline(n * tls_results.period, alpha=0.4, lw=1, linestyle="dashed")
        axs[2].axvline(tls_results.period / n, alpha=0.4, lw=1, linestyle="dashed")
    axs[2].set(xlabel='Period (days)', ylabel='SDE')
    axs[2].plot(tls_results.periods, tls_results.power, color='black', lw=0.5)
    if plot_harmonics:
        max_harmonic_power_index = np.argmax(transit_result.harmonic_spectrum)
        harmonics = [1 / 4, 1 / 3, 1 / 2, 1, 2, 3, 4]
        for harmonic in harmonics:
            axs[3].axvline(harmonic * tls_results.periods[max_harmonic_power_index], alpha=0.4, lw=1, linestyle="dashed")
        axs[3].axvline(tls_results.periods[max_harmonic_power_index], alpha=0.4, lw=3)
        axs[3].set_xlim(np.min(tls_results.periods), np.max(tls_results.periods))
        axs[3].set(xlabel='Period (days)', ylabel='Harmonics Power')
        axs[3].plot(tls_results.periods, transit_result.harmonic_spectrum, color='black', lw=0.5)
    plt.savefig(plot_dir + file, bbox_inches='tight', dpi=200)
    fig.clf()
    plt.close(fig)


def plot_system_architecture(sistemas, temperaturas_estrellas, tamaños_estrellas, periodos_orbitales, tamaños_planetas, candidatos, save_dir) -> None:
    sistemas_info = list(zip(sistemas, periodos_orbitales, tamaños_planetas, temperaturas_estrellas, tamaños_estrellas))
    sistemas_info.sort(key=lambda x: x[3])
    sistemas_ordenados, periodos_orbitales_ordenados, tamaños_planetas_ordenados, temperaturas_estrellas_ordenadas, tamaños_estrellas_ordenados = zip(*sistemas_info)
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor('xkcd:white')
    separacion = 1.1
    ylim_superior = len(sistemas_ordenados) * separacion + 0.5
    def color_planeta(tamaño):
        if tamaño < 2:
            return 'brown'
        elif 2 <= tamaño <= 5:
            return 'green'
        else:
            return 'blue'
    colors = [(1, 0, 0), (1, 1, 0)]  # R -> Y
    n_bins = 100  # Número de divisiones en el colormap
    cmap_name = 'my_list'
    cm = LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bins)
    ax.set_ylim(-0.5, ylim_superior)
    ax.set_yticks(np.arange(len(sistemas_ordenados)) * separacion)
    ax.set_yticklabels(sistemas_ordenados)
    ax.set_xlabel('Orbital Period (day)', fontsize=14)
    # ax.set_ylabel('Planetary System')
    ax.tick_params(axis='x', labelsize=12)  # Ajusta el tamaño de los ticks del eje X
    ax.tick_params(axis='y', labelsize=12)  # Ajusta el tamaño de los ticks del eje Y
    max_periodo_confirmados = max([max(periodos) for periodos in periodos_orbitales])
    periodos_candidatos = [item for sublist in [c['periodos'] for c in candidatos.values()] for item in sublist]
    max_periodo_candidatos = max(periodos_candidatos) if periodos_candidatos else 0
    max_periodo_general = max(max_periodo_confirmados, max_periodo_candidatos)
    ticks_x = np.arange(1, max_periodo_general + 1, 2)
    ax.set_xticks(ticks_x)
    # Ajustar los límites del eje X para asegurarse de que todos los ticks sean visibles
    ax.set_xlim(-1.5, max_periodo_general + 1)
    ax.grid(True, axis='y', linestyle='--', linewidth=0.5,zorder=1)
    ax.grid(False, axis='x')
    norm = plt.Normalize(3900, 6000)
    for i, sistema in enumerate(sistemas_ordenados):
        y = i * separacion  # Ajustar la separación entre sistemas
        for j, periodo in enumerate(periodos_orbitales_ordenados[i]):
            tamaño_planeta = tamaños_planetas_ordenados[i][j]
            color = color_planeta(tamaño_planeta)
            ax.scatter(periodo, y, s=tamaño_planeta*35, c=color, marker='o', alpha=1.0, zorder=2)  # Sin transparencia para confirmados
        tamaño_estrella = tamaños_estrellas_ordenados[i] * 20 * 100  # Escala de tamaño de estrella\n",
        #norm = plt.Normalize(3900, 6000)
        color_estrella = cm(norm(temperaturas_estrellas_ordenadas[i]))
        ax.scatter(-0.25, y, s=tamaño_estrella, c=color_estrella, marker='o', alpha=1.0,zorder=2)  # Sin transparencia para estrellas
        # Planetas candidatos (rellenos con borde negro y transparencia)
        if sistema in candidatos:
            for k, periodo_candidato in enumerate(candidatos[sistema]['periodos']):
                tamaño_candidato = candidatos[sistema]['radios'][k]
                color_candidato = color_planeta(tamaño_candidato)
                ax.scatter(periodo_candidato, y, s=tamaño_candidato*35, c=color_candidato, edgecolors='black', marker='o', alpha=0.5, linewidth=2,zorder=2)  # Añadir transparencia
    # Crear colorbar para las temperaturas de las estrellas con el colormap personalizado
    sm = plt.cm.ScalarMappable(cmap=cm, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax,pad=0.02)
    cbar.set_label('Stellar Temperature (K)', fontsize=14)
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='brown', markersize=10, label=r'≤ 2.0 R$_{\\oplus}$'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10, label=r'> 2.0 and ≤ 5.0 R$_{\\oplus}$'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10, label=r'> 5.0 R$_{\\oplus}$')
    ]
    ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.87, 0.98), ncol=1)
    plt.tight_layout()
    plt.savefig(save_dir, 'sistemas_planetarios.png', dpi=200)


def plot_stability(masses, eccentricities, megnos, save_dir):
    unique_masses = np.unique(masses)
    unique_eccs = np.unique(eccentricities)
    results = np.full((len(unique_masses), len(unique_eccs)), 10.0)
    for index, mass in enumerate(masses):
        mass_index = np.argwhere(unique_masses == mass).flatten()[0]
        ecc = eccentricities[index]
        ecc_index = np.argwhere(unique_eccs == ecc).flatten()[0]
        results[mass_index, ecc_index] = megnos[index]
    ecc_index = np.argwhere(unique_eccs == ecc).flatten()[0]
    results = np.nan_to_num(results)
    n = len(results)
    pixels = len(results[1])
    Ngrid = len(np.unique(masses))
    ecc1max = max(eccentricities)
    ecc1min = min(eccentricities)
    par_m1 = np.linspace(ecc1min, ecc1max, Ngrid)
    m2max = max(masses)
    m2min = min(masses)
    par_m2 = np.linspace(m2min, m2max, Ngrid)
    ax = plt.subplot(111)
    extent = [min(par_m2), max(par_m2), min(par_m1), max(par_m1)] #x,y
    ax.set_xlim(extent[0], extent[1])
    ax.set_xlabel("Mass $M_\\oplus$")
    ax.set_ylim(extent[2], extent[3])
    ax.set_ylabel("Eccentricity")
    im = ax.imshow(np.transpose(results), interpolation="none", vmin=1., vmax=5, cmap="plasma", origin="lower", aspect='auto', extent=extent)
    cb = plt.colorbar(im, ax=ax, ticks=[1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0])
    cb.ax.set_yticklabels(["1.5", "2.0", "2.5", "3.0", "3.5", "4.0", "4.5", "5.0"])
    cb.set_label("MEGNO $\\langle Y \\rangle$")
    ecc = np.linspace(0, 0.356, 50)
    ebb = 0.27 - (1.50*ecc)
    plt.plot(ecc, ebb, '-', color="black")
    plt.savefig(save_dir + '/stability_megno.png', bbox_inches='tight', dpi=200)

# megno_df = pd.read_csv("/home/martin/Downloads/sherlock/sherlock_confusion_matrix/cps/done/TIC461239485_all/stability_stability/stability_megno.csv")
# megno_df[['mass1', 'mass2']] = megno_df['masses'].str.split(',', expand=True)
# megno_df['mass2'] = megno_df['mass2'].astype(float)
# megno_df[['ecc1', 'ecc2']] = megno_df['eccentricities'].str.split(',', expand=True)
# megno_df['ecc2'] = megno_df['ecc2'].astype(float)
# megno_df['ecc1'] = megno_df['ecc1'].astype(float)
# megno_df = megno_df.groupby(['mass2', 'ecc2'])['megno'].mean().reset_index()
# megno_df.sort_values(by=['mass2', 'ecc2'], ascending=True, inplace=True)
# plot_stability(megno_df['mass2'].to_numpy(), megno_df['ecc2'].to_numpy(), megno_df['megno'].to_numpy(),'./')

# sistemas = ['TOI-2441', 'WASP-16', 'HAT-P-26', 'HAT-P-27']
# periodos_orbitales = [[0.8], [3.2], [4.2], [3.03]]
# tamaños_planetas = [[1.7], [11.8], [7.1], [11]]
# temperaturas_estrellas = [4099, 5717, 5062, 5316]
# tamaños_estrellas = [0.72, 1.07, 0.86, 0.86]
# candidatos = {
#     'TOI-2441': {'radios': [3.0], 'periodos': [18.7]},
#     'WASP-16': {'radios': [2.0], 'periodos': [10.4]},
#     'HAT-P-26': {'radios': [2.1], 'periodos': [6.6]},
#     'HAT-P-27': {'radios': [3.03], 'periodos': [1.2]}
# }
# plot_system_architecture(sistemas, temperaturas_estrellas, tamaños_estrellas, periodos_orbitales, tamaños_planetas, candidatos, './')


