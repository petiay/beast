import numpy as np
import matplotlib.pyplot as plt
import argparse

from beast.physicsmodel.grid import SEDGrid
import beast.observationmodel.noisemodel.generic_noisemodel as noisemodel

__all__ = ["plot_noisemodel"]


def plot_noisemodel(
    sed_file,
    noise_file_list,
    plot_file,
    samp=100,
    color=["black", "red", "gold", "lime", "xkcd:azure"],
    label=None,
):
    """
    Make a plot of the noise model: for each of the bandsm make plots of bias
    and uncertainty as a function of flux

    If there are multiple files in noise_file_list, each of them will be
    overplotted in each panel.

    Parameters
    ----------
    sed_file : string
        path+name of the SED grid file

    noise_file_list : list of strings
        path+name of the noise model file(s)

    plot_file : string
        name of the file to save the plot

    samp : int (default=100)
        plotting all of the SED points takes a long time for a viewer to load,
        so set this to plot every Nth point

    color : list of strings (default=['black','red','gold','lime','xkcd:azure'])
        colors to cycle through when making plots

    label : list of strings (default=None)
        if set, use these labels in a legend for each item in noise_file_list
    """

    # read in the SED grid
    print("* reading SED grid file")
    sed_object = SEDGrid(sed_file)
    if hasattr(sed_object.seds, "read"):
        sed_grid = sed_object.seds.read()
    else:
        sed_grid = sed_object.seds
    filter_list = sed_object.filters
    n_filter = len(filter_list)

    # figure
    fig, ax = plt.subplots(nrows=3, ncols=n_filter, figsize=(25, 15))

    # setup the plots
    fontsize = 12
    font = {"size": fontsize}

    plt.rc("font", **font)

    plt.rc("lines", linewidth=2)
    plt.rc("axes", linewidth=2)
    plt.rc("xtick.major", width=2)
    plt.rc("ytick.major", width=2)

    # go through noise files
    for n, nfile in enumerate(np.atleast_1d(noise_file_list)):

        print("* reading " + nfile)

        # read in the values
        noisemodel_vals = noisemodel.get_noisemodelcat(nfile)

        # extract error and bias
        noise_err = noisemodel_vals["error"]
        noise_bias = noisemodel_vals["bias"]
        noise_compl = noisemodel_vals["completeness"]

        # plot things
        for f, filt in enumerate(filter_list):

            # error is negative where it's been extrapolated -> trim those
            good_err = np.where(noise_err[:, f] > 0)[0]
            plot_sed = sed_grid[good_err, f][::samp]
            plot_err = noise_err[good_err, f][::samp]
            plot_bias = noise_bias[good_err, f][::samp]
            plot_compl = noise_compl[good_err, f][::samp]

            # bias
            bax = ax[0, f]
            bax.plot(
                np.log10(plot_sed),
                plot_bias / plot_sed,
                marker="o",
                linestyle="none",
                mew=0,
                ms=2,
                color=color[n % len(color)],
                alpha=0.1,
            )
            if label is not None:
                bax.set_label(label[n])

            bax.tick_params(axis="both", which="major")
            # ax.set_xlim(ax.get_xlim()[::-1])
            bax.set_xlabel("log " + filt)
            bax.set_ylabel(r"Bias ($\mu$/F)")

            # error
            eax = ax[1, f]
            eax.plot(
                np.log10(plot_sed),
                plot_err / plot_sed,
                marker="o",
                linestyle="none",
                mew=0,
                ms=2,
                color=color[n % len(color)],
                alpha=0.1,
            )
            if label is not None:
                eax.set_label(label[n])

            eax.tick_params(axis="both", which="major")
            # ax.set_xlim(ax.get_xlim()[::-1])
            eax.set_xlabel("log " + filt)
            eax.set_ylabel(r"Error ($\sigma$/F)")

            # completeness
            cax = ax[2, f]
            cax.plot(
                np.log10(plot_sed),
                plot_compl,
                marker="o",
                linestyle="none",
                mew=0,
                ms=2,
                color=color[n % len(color)],
                alpha=0.1,
            )
            if label is not None:
                cax.set_label(label[n])

            cax.tick_params(axis="both", which="major")
            # ax.set_xlim(ax.get_xlim()[::-1])
            cax.set_xlabel("log " + filt)
            cax.set_ylabel(r"Completeness")

            # do a legend if this is
            # (a) the leftmost panel
            # (b) the last line to be added
            # (c) there are labels set
            if (f == 0) and (n == len(noise_file_list) - 1) and (label is not None):
                leg = bax.legend(fontsize=12)
                for lh in leg.legendHandles:
                    lh._legmarker.set_alpha(1)
                leg = eax.legend(fontsize=12)
                for lh in leg.legendHandles:
                    lh._legmarker.set_alpha(1)

    plt.tight_layout()

    fig.savefig(plot_file)
    plt.close(fig)


if __name__ == "__main__":  # pragma: no cover

    # commandline parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "sed_file", type=str, help="path+name of the sed grid file",
    )
    parser.add_argument(
        "noise_file_list",
        type=str,
        nargs="+",
        help="path+name of the noise model file(s)",
    )
    parser.add_argument(
        "plot_file", type=str, help="name of the file to save the plot",
    )
    parser.add_argument(
        "--samp", type=int, default=100, help="plot every Nth point",
    )
    parser.add_argument(
        "--color",
        type=str,
        nargs="+",
        default=["black", "red", "gold", "lime", "xkcd:azure"],
        help="colors to cycle through when making plots",
    )
    parser.add_argument(
        "--label",
        type=str,
        nargs="+",
        default=None,
        help="if set, use these labels in a legend for each item in noise_file_list",
    )

    args = parser.parse_args()

    plot_noisemodel(
        args.sed_file,
        args.noise_file_list,
        args.plot_file,
        samp=args.samp,
        color=args.color,
        label=args.label,
    )

    # print help if no arguments
    if not any(vars(args).values()):
        parser.print_help()
