# -*- coding: UTF-8 -*-

import os
from typing import Union

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from pandas import DataFrame

from .. import util as ul
from ..util import path, collection, get_real_predict_label, type_20_colors, type_50_colors

__name__: str = "plot_pie"


def base_pie(
    values: list,
    labels: list,
    width: float = 2,
    height: float = 2,
    pct_distance: float = 0.6,
    label_distance: float = 1.1,
    colors: list = None,
    title: str = None,
    autopct: str = '%1.2f%%',
    output: path = None,
    show: bool = True
) -> None:
    if output is None and not show:
        ul.log(__name__).info(f"At least one of the `output` and `show` parameters is required")
    else:
        fig = plt.figure(figsize=(width, height))

        if title is not None:
            plt.title(title)

        size = len(values)

        if size is not len(labels):
            ul.log(__name__).error(f"The parameter lengths of `values`({size}) and `labels`({len(labels)}) must be equal.")
            raise ValueError(f"The parameter lengths of `values`({size}) and `labels`({len(labels)}) must be equal.")

        if colors is None:
            colors = type_20_colors[:len(labels)] if size <= 20 else type_50_colors[:len(labels)]

        ax1 = fig.add_subplot()

        ax1.set_axis_off()

        ax1.pie(
            values,
            labels=labels,
            colors=colors,
            autopct=autopct,
            labeldistance=label_distance,
            pctdistance=pct_distance
        )

        ax1.axis('off')

        if output is not None:
            output_pdf = output if output.endswith(".pdf") else f"{output}.pdf"
            # plt.savefig(output_pdf, dpi=300)
            with PdfPages(output_pdf) as pdf:
                pdf.savefig(fig)

        if show:
            plt.show()

        plt.close()


def pie_label(
    df: DataFrame,
    map_cluster: Union[str, collection],
    value: str = "value",
    clusters: str = "clusters",
    width: float = 2,
    height: float = 2,
    radius: float = 0.6,
    fontsize: float = 17,
    pct_distance: float = 0.6,
    label_distance: float = 1.1,
    colors: list = None,
    title: str = None,
    output: path = None,
    show: bool = True
) -> None:
    if output is None and not show:
        ul.log(__name__).info(f"At least one of the `output` and `show` parameters is required")
    else:
        # judge
        df_columns = list(df.columns)

        if value not in df_columns:
            ul.log(__name__).error(f"The `value` ({value}) parameter must be in the `df` parameter data column name ({df_columns})")
            raise ValueError(
                f"The `value` ({value}) parameter must be in the `df` parameter data column name ({df_columns})"
            )

        df_sort, cluster_size, cluster_list = get_real_predict_label(
            df=df,
            map_cluster=map_cluster,
            clusters=clusters,
            value=value
        )

        # top value
        top_predict_cluster = list(df_sort["true_label"])[:cluster_size]
        top_x = [top_predict_cluster.count(1), top_predict_cluster.count(0)]

        fig = plt.figure(figsize=(width, height))

        if title is not None:
            plt.title(title)

        if colors is None:
            colors = type_20_colors[:2]

        ax1 = fig.add_subplot()

        top_sum = np.array(top_x).sum()

        ax1.set_axis_off()
        ax1.pie(
            top_x,
            labels=[", ".join(cluster_list), "Other"],
            colors=colors,
            startangle=90,
            labeldistance=label_distance,
            pctdistance=pct_distance
        )
        ax1.pie(
            [np.array(top_x).sum()],
            colors=['white'],
            radius=radius,
            startangle=90,
            wedgeprops=dict(width=radius, edgecolor='w')
        )
        ax1.text(0, 0, "{:.2f}%".format(top_x[0] / top_sum * 100), ha='center', va='center', fontsize=fontsize)
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


def pie_trait(
    trait_df: DataFrame,
    trait_cluster_map: dict,
    trait_name: str = "All",
    clusters: str = "clusters",
    trait_column_name: str = "id",
    value: str = "value",
    width: float = 2,
    height: float = 2,
    radius: float = 0.6,
    fontsize: float = 17,
    pct_distance: float = 0.6,
    label_distance: float = 1.1,
    colors: list = None,
    title: str = None,
    output: path = None,
    show: bool = True
) -> None:
    """
    Violin plot of cell scores for traits/diseases
    :param fontsize:
    :param radius:
    :param colors:
    :param label_distance:
    :param pct_distance:
    :param height:
    :param width:
    :param clusters:
    :param trait_cluster_map:
    :param title:
    :param value:
    :param trait_column_name:
    :param trait_df: data
    :param trait_name: trait/disease name or All, 'All' show all traits/diseases
    :param output: Image output path
    :param show: Whether to display pictures
    :return: None
    """
    trait_cluster_map_key_list = list(trait_cluster_map.keys())

    data: DataFrame = trait_df.copy()

    def trait_plot(trait_: str, atac_cell_df_: DataFrame) -> None:
        """
        show plot
        :param trait_: trait name
        :param atac_cell_df_:
        :return: None
        """
        if trait_ not in trait_cluster_map_key_list:
            ul.log(__name__).error(f"The key in `trait_cluster_map` does not contain the `{trait_}` trait and needs to be added")
            raise ValueError(
                f"The key in `trait_cluster_map` does not contain the `{trait_}` trait and needs to be added"
            )

        ul.log(__name__).info("Plotting pie {}".format(trait_))
        # get gene score
        trait_score = atac_cell_df_[atac_cell_df_[trait_column_name] == trait_]
        # Sort gene scores from small to large
        pie_label(
            df=trait_score[[trait_column_name, clusters, value]],
            map_cluster=trait_cluster_map[trait_],
            value=value,
            clusters=clusters,
            width=width,
            height=height,
            radius=radius,
            fontsize=fontsize,
            pct_distance=pct_distance,
            label_distance=label_distance,
            colors=colors,
            title=f"{title} {trait_}" if title is not None else title,
            output=os.path.join(output, f"cell_{trait_}_score_pie.pdf") if output is not None else None,
            show=show
        )

    # noinspection DuplicatedCode
    trait_list = list(set(data[trait_column_name]))
    # judge trait
    if trait_name != "All" and trait_name not in trait_list:
        ul.log(__name__).error(f"The {trait_name} trait/disease is not in the trait/disease list {trait_list}.")
        raise ValueError(f"The {trait_name} trait/disease is not in the trait/disease list {trait_list}.")

    # plot
    if trait_name == "All":
        for trait in trait_list:
            trait_plot(trait, trait_df)
    else:
        trait_plot(trait_name, trait_df)
