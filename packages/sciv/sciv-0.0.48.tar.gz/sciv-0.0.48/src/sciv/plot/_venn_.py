# -*- coding: UTF-8 -*-

from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib_venn import venn3, venn3_circles, venn2, venn2_circles

from .. import util as ul
from ..util import path, collection, type_set_colors

__name__: str = "plot_venn"


def three_venn(
    set1: collection,
    set2: collection,
    set3: collection,
    name1: str = "Set1",
    name2: str = "Set2",
    name3: str = "Set3",
    width: float = 2,
    height: float = 2,
    colors: list = None,
    title: str = None,
    output: path = None,
    show: bool = True
) -> None:
    if output is None and not show:
        ul.log(__name__).info(f"At least one of the `output` and `show` parameters is required")
    else:
        fig = plt.figure(figsize=(width, height))

        if title is not None:
            plt.title(title)

        if colors is None:
            colors = type_set_colors[:3]

        if len(colors) < 3:
            ul.log(__name__).info(f"The value of colors requires three elements.")
            raise ValueError(f"The value of colors requires three elements.")
        elif len(colors) > 3:
            colors = colors[:3]

        ax1 = fig.add_subplot()

        set1 = set(set1)
        set2 = set(set2)
        set3 = set(set3)

        subsets = (set1, set2, set3)

        venn3(subsets=subsets, set_labels=(name1, name2, name3), ax=ax1, set_colors=colors)

        # noinspection PyTypeChecker
        venn3_circles(subsets=subsets, linestyle='dashed', linewidth=1, color="grey", ax=ax1)

        ax1.legend(loc='upper right')

        ax1.axis('off')

        if output is not None:
            output_pdf = output if output.endswith(".pdf") else f"{output}.pdf"
            # plt.savefig(output_pdf, dpi=300)
            with PdfPages(output_pdf) as pdf:
                pdf.savefig(fig)

        if show:
            plt.show()

        plt.close()


def two_venn(
    set1: collection,
    set2: collection,
    name1: str = "Set1",
    name2: str = "Set2",
    width: float = 2,
    height: float = 2,
    colors: list = None,
    title: str = None,
    output: path = None,
    show: bool = True
) -> None:
    if output is None and not show:
        ul.log(__name__).info(f"At least one of the `output` and `show` parameters is required")
    else:
        fig = plt.figure(figsize=(width, height))

        if title is not None:
            plt.title(title)

        if colors is None:
            colors = type_set_colors[:2]

        if len(colors) < 2:
            ul.log(__name__).info(f"The value of colors requires three elements.")
            raise ValueError(f"The value of colors requires three elements.")
        elif len(colors) > 2:
            colors = colors[:2]

        ax1 = fig.add_subplot()

        set1 = set(set1)
        set2 = set(set2)

        venn2((set1, set2), set_labels=(name1, name2), ax=ax1, set_colors=colors)

        # noinspection PyTypeChecker
        venn2_circles(subsets=(set1, set2), linestyle='dashed', linewidth=1, color="grey", ax=ax1)

        ax1.legend(loc='upper right')

        ax1.axis('off')

        if output is not None:
            output_pdf = output if output.endswith(".pdf") else f"{output}.pdf"
            # plt.savefig(output_pdf, dpi=300)
            with PdfPages(output_pdf) as pdf:
                pdf.savefig(fig)

        if show:
            plt.show()

        plt.close()

