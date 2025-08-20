# -*- coding: UTF-8 -*-

import math
import random
from typing import Optional, Literal, Union

import matplotlib
import networkx as nx
import numpy as np
from anndata import AnnData
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import pyplot as plt, gridspec

from .. import util as ul
from ..util import (
    matrix_data,
    collection,
    path,
    list_index,
    to_dense,
    type_20_colors,
    type_50_colors,
    check_adata_get
)

__name__: str = "plot_graph"

_LayoutType = Optional[Literal['spring', 'kamada_kawai', 'circular', 'shell', 'circular_type1', 'circular_type2', 'square_type1', 'square_type2']]


def graph(
    data: matrix_data,
    labels: collection = None,
    node_size: int = 50,
    width: float = 2,
    height: float = 2,
    is_font: bool = False,
    output: path = None,
    show: bool = True
) -> None:
    """
    plot graph from adjacency matrix
    :param data: input data
    :param labels: Label of data node
    :param node_size: Size of data node
    :param width:
    :param height:
    :param is_font: Is there a word on the data node
    :param output: Image output path
    :param show: Whether to display pictures
    :return: None
    """
    if output is None and not show:
        ul.log(__name__).info(f"At least one of the `output` and `show` parameters is required")
    else:
        plt.figure(figsize=(width, height), dpi=150)

        # Determine whether it is a square array
        if data.shape[0] != data.shape[1]:
            ul.log(__name__).error("The input data must be a square matrix.")
            raise ValueError("The input data must be a square matrix.")

        # set labels
        labels_dict = {}

        if labels is not None:

            if data.shape[0] != np.asarray(labels).size:
                ul.log(__name__).error(
                    f"The number of input data nodes {data.shape[0]} and the number of "
                    f"labels {np.asarray(labels).size} must be consistent"
                )
                raise ValueError(
                    f"The number of input data nodes {data.shape[0]} and the number of "
                    f"labels {np.asarray(labels).size} must be consistent"
                )

            labels_dict: dict = dict(zip(range(len(labels)), labels))

        rows, cols = np.where(data == 1)
        edges = zip(rows.tolist(), cols.tolist())
        gr = nx.Graph(name="Cell-cell graph")
        gr.add_edges_from(edges)
        pos = nx.spring_layout(gr, k=0.15, iterations=35, seed=2023)

        options: dict = {
            "node_color": "black",
            "node_size": node_size,
            "linewidths": 0,
            "width": 0.1
        }

        if is_font:
            if labels is not None:
                nx.draw(gr, pos=pos, labels=labels_dict, **options)
            else:
                nx.draw(gr, pos=pos, **options)
        else:
            nx.draw(gr, pos=pos, labels={}, **options)

        if show:
            plt.show()

        if output is not None:
            plt.savefig(output if output.endswith(".pdf") else f"{output}.pdf")

        plt.close()


def communities_graph(
    adata: AnnData,
    labels: collection,
    layer: str = None,
    clusters: str = "clusters",
    width: float = 2,
    height: float = 2,
    title: str = None,
    node_size: float = 2.0,
    line_widths: float = 0.001,
    start_color_index: int = 0,
    color_step_size: int = 0,
    output: path = None,
    show: bool = True
):
    if output is None and not show:
        ul.log(__name__).info(f"At least one of the `output` and `show` parameters is required")
    else:
        ul.log(__name__).info("Start cell-cell network diagram")

        new_data = check_adata_get(adata=adata, layer=layer)

        # adjust matrix
        adj_matrix = to_dense(new_data.X)
        communities, node_labels = list_index(labels)

        df = new_data.obs.copy()

        __hue_order__ = list(np.sort(list(set(df[clusters]))))

        type_colors = type_20_colors if len(__hue_order__) <= 20 else type_50_colors

        ul.log(__name__).info("Get position")
        color_index = 0
        g = nx.from_numpy_array(adj_matrix)
        partition = [0 for _ in range(g.number_of_nodes())]
        for c_i, nodes in enumerate(communities):
            for i in nodes:
                partition[i] = type_colors[start_color_index + color_index * color_step_size + c_i]
            color_index += 1

        pos = nx.spring_layout(g)

        pos1 = [p[0] for p in pos.values()]
        pos2 = [p[1] for p in pos.values()]
        new_data.obs["pos1"] = pos1
        new_data.obs["pos2"] = pos2

        fig = plt.figure(figsize=(width, height))

        if title is not None:
            plt.title(title)

        plt.axis("off")

        nx.draw_networkx_nodes(
            g,
            pos=pos,
            node_size=node_size,
            node_color=partition,
            linewidths=line_widths
        )
        # nodes.set_edgecolor("b")
        nx.draw_networkx_edges(
            g,
            pos=pos,
            node_size=node_size,
            edge_color=(0, 0, 0, 0.3),
            width=line_widths
        )

        # noinspection DuplicatedCode
        if output is not None:
            output_pdf = output if output.endswith(".pdf") else f"{output}.pdf"
            # plt.savefig(output_pdf, dpi=300)
            with PdfPages(output_pdf) as pdf:
                pdf.savefig(fig)

        if show:
            plt.grid(True)
            plt.show()

        plt.close()


def network_two_types(
    data_pairs: list,
    type1_scores: dict,
    type2_scores: dict,
    type1_node_size: Optional[Union[dict, list, float]] = 50,
    type2_node_size: Optional[Union[dict, list, float]] = 50,
    label_nodes: Optional[list] = None,
    width: float = 4,
    height: float = 3,
    k: Optional[float] = None,
    iterations: int = 50,
    scale: float = 1,
    radius: float = 0.35,
    type1_node_shape: str = 'o',
    type2_node_shape: str = 's',
    type1_bar_label: str = 'Score',
    type2_bar_label: str = 'Score',
    type1_cmap_str: str = "winter",
    type2_cmap_str: str = "YlOrRd",
    node_alpha: float = 0.8,
    edge_alpha: float = 0.8,
    is_fluctuate: bool = True,
    layout_type: str = 'spring',
    output: path = None,
    show: bool = True
):

    if output is None and not show:
        ul.log(__name__).info(f"At least one of the `output` and `show` parameters is required")
    else:
        # 创建基因和变异的节点列表
        type1_nodes = []
        type2_nodes = []

        type1_keys = type1_scores.keys()
        type2_keys = type2_scores.keys()

        for type1_node, type2_node in data_pairs:

            if type1_node not in type1_keys:
                raise Exception(f"Node `{type1_node}` not in `type1_scores`.")

            if type2_node not in type2_keys:
                raise Exception(f"Node `{type2_node}` not in `type2_scores`.")

            if type1_node not in type1_nodes:
                type1_nodes.append(type1_node)

            if type2_node not in type2_nodes:
                type2_nodes.append(type2_node)

        # 创建图形和网格
        fig = plt.figure(figsize=(width, height))
        gs = gridspec.GridSpec(
            2, 2,
            width_ratios=[7, 1],
            height_ratios=[4, 4],
            hspace=0.1,
            wspace=0.1
        )

        # 主轴用于绘制网络图
        ax_network = fig.add_subplot(gs[0:2, 0:1])

        # 创建有向图
        G = nx.Graph()
        G.add_edges_from(data_pairs)

        # 绘制图形
        if layout_type == 'spring':
            pos = nx.spring_layout(G, k=k, iterations=iterations)
        elif layout_type == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(G, scale=scale)
        elif layout_type == 'circular':
            pos = nx.circular_layout(G, scale=scale)
        elif layout_type == 'shell':
            shells = [type1_nodes, type2_nodes]
            pos = nx.shell_layout(G, shells, scale=scale)
        else:
            if layout_type == 'circular_type1':
                is_type1 = True
                type1_positions = nx.circular_layout(G.subgraph(type1_nodes), scale=scale)
                pos = {**type1_positions}
            elif layout_type == 'circular_type2':
                is_type1 = False
                type2_positions = nx.circular_layout(G.subgraph(type2_nodes), scale=scale)
                pos = {**type2_positions}
            else:
                if layout_type == 'square_type1':
                    is_type1 = True
                elif layout_type == 'square_type2':
                    is_type1 = False
                else:
                    raise ValueError("The `layout_type` parameter must be one of the following string values {'spring','kamada_kawai','circular','shell','circular_type1','circular_type2','square_type1','square_type2'}")

                # 调整为正方形坐标
                pos = {}
                side_length = int(np.sqrt(len(type1_nodes if is_type1 else type2_nodes)))
                for i, key in enumerate(type1_nodes if is_type1 else type2_nodes):
                    pos[key] = (i % side_length, i // side_length)

            for i, _node_ in enumerate(type1_nodes if is_type1 else type2_nodes):
                type_other = []
                for k, v in data_pairs:
                    if is_type1:
                        if k == _node_:
                            type_other.append(v)
                    else:
                        if v == _node_:
                            type_other.append(k)

                angle_step = 360 / len(type_other)
                for j, _type_node_ in enumerate(type_other):
                    angle = math.radians(j * angle_step) + (random.random() / 2 if is_fluctuate else 0)
                    x = pos[_node_][0] + np.power(-1, int(random.random() * 10) if is_fluctuate else 0) * (radius + (random.random() / 10 if is_fluctuate else 0)) * math.cos(angle)
                    y = pos[_node_][1] + np.power(-1, int(random.random() * 10) if is_fluctuate else 0) * (radius + (random.random() / 10 if is_fluctuate else 0)) * math.sin(angle)
                    pos[_type_node_] = (x, y)

        type1_cmap = matplotlib.colormaps[type1_cmap_str]
        type2_cmap = matplotlib.colormaps[type2_cmap_str]

        # 确保颜色映射的归一化范围与基因分数的值范围相匹配
        type1_norm = plt.Normalize(vmin=min(type1_scores.values()), vmax=max(type1_scores.values()))
        type2_norm = plt.Normalize(vmin=min(type2_scores.values()), vmax=max(type2_scores.values()))

        type1_node_colors = [type1_cmap(type1_norm(type1_scores[node])) for node in type1_nodes]
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=type1_nodes,
            node_size=[type1_node_size[node] for node in type1_nodes] if isinstance(type1_node_size, dict) else type1_node_size,
            node_color=type1_node_colors,
            edgecolors='#333333',
            node_shape=type1_node_shape,
            alpha=node_alpha,
            ax=ax_network
        )

        type2_node_colors = [type2_cmap(type2_norm(type2_scores[node])) for node in type2_nodes]
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=type2_nodes,
            node_size=[type2_node_size[node] for node in type2_nodes] if isinstance(type2_node_size, dict) else type2_node_size,
            node_color=type2_node_colors,
            edgecolors='#333333',
            node_shape=type2_node_shape,
            alpha=node_alpha,
            ax=ax_network
        )

        if label_nodes is not None:
            labels = {node: node for node in label_nodes}

            # 绘制节点标签
            nx.draw_networkx_labels(
                G,
                pos,
                labels,
                font_size=10,
                ax=ax_network,
                verticalalignment='center',
                horizontalalignment='center'
            )

        # 边的颜色和宽度
        edge_colors = ['gray' for _ in data_pairs]
        edge_widths = [1.0 for _ in data_pairs]

        # 绘制边
        nx.draw_networkx_edges(
            G,
            pos,
            edge_color=edge_colors,
            width=edge_widths,
            alpha=edge_alpha,
            arrows=False,
            ax=ax_network,
            style='solid'
        )

        # 设置背景颜色
        ax_network.set_facecolor('white')
        ax_network.spines['top'].set_visible(False)
        ax_network.spines['right'].set_visible(False)

        # 颜色条轴
        ax_cbar1 = fig.add_subplot(gs[0:1, 1:2])
        ax_cbar1.set_axis_off()
        # 创建颜色条
        sm1 = plt.cm.ScalarMappable(cmap=type1_cmap, norm=type1_norm)
        cbar1 = plt.colorbar(sm1, ax=ax_cbar1, location='right', pad=0.2)
        cbar1.set_label(type1_bar_label)

        ax_cbar2 = fig.add_subplot(gs[1:2, 1:2])
        ax_cbar2.set_axis_off()
        sm2 = plt.cm.ScalarMappable(cmap=type2_cmap, norm=type2_norm)
        cbar2 = plt.colorbar(sm2, ax=ax_cbar2, location='right', pad=0.2)
        cbar2.set_label(type2_bar_label)

        # 显示图形
        plt.axis('off')

        # noinspection DuplicatedCode
        if output is not None:
            output_pdf = output if output.endswith(".pdf") else f"{output}.pdf"
            # plt.savefig(output_pdf, dpi=300)
            with PdfPages(output_pdf) as pdf:
                pdf.savefig(fig)

        if show:
            plt.grid(True)
            plt.show()

        plt.close()
