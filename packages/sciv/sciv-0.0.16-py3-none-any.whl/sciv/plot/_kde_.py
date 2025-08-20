# -*- coding: UTF-8 -*-

from typing import Literal

import numpy as np
from anndata import AnnData
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
from tqdm import tqdm

from .. import util as ul
from ..util import path, down_sampling_data, check_adata_get

__name__: str = "plot_kde"


def kde(
    adata: AnnData,
    layer: str = None,
    title: str = None,
    width: float = 4,
    height: float = 2,
    axis: Literal[-1, 0, 1] = -1,
    sample_number: int = 1000000,
    is_legend: bool = True,
    output: path = None,
    show: bool = True
) -> None:
    if output is None and not show:
        ul.log(__name__).info(f"At least one of the `output` and `show` parameters is required")
    else:
        ul.log(__name__).info("Start plotting the Kernel density estimation chart")
        fig, ax = plt.subplots(figsize=(width, height))
        fig.subplots_adjust(bottom=0.3)

        data = check_adata_get(adata, layer=layer, is_dense=True, is_matrix=False)

        if title is not None:
            plt.title(title)

        sns.set_theme(style="whitegrid")

        # Random sampling
        if axis == -1:
            matrix = down_sampling_data(data.X, sample_number)
            sns.kdeplot(matrix, shade=True, fill=True)
        elif axis == 0:
            col_number = data.shape[1]
            if data.shape[0] * data.shape[1] > sample_number:
                row_number: int = sample_number // col_number

                for i in tqdm(range(col_number)):
                    _vector_ = down_sampling_data(data.X[:, i], row_number)
                    sns.kdeplot(np.array(_vector_).flatten(), shade=True, fill=True)
            else:
                for i in tqdm(range(col_number)):
                    sns.kdeplot(np.array(data.X[:, i]).flatten(), shade=True, fill=True)

            if is_legend:
                ax.legend(list(adata.var.index))

        elif axis == 1:
            row_number = data.shape[0]
            if data.shape[0] * data.shape[1] > sample_number:
                col_number: int = sample_number // row_number

                for i in tqdm(range(row_number)):
                    _vector_ = down_sampling_data(data.X[i, :], col_number)
                    sns.kdeplot(np.array(_vector_).flatten(), shade=True, fill=True)
            else:
                for i in tqdm(range(row_number)):
                    sns.kdeplot(np.array(data.X[i, :]).flatten(), shade=True, fill=True)

            if is_legend:
                ax.legend(list(adata.obs.index))

        if output is not None:
            output_pdf = output if output.endswith(".pdf") else f"{output}.pdf"
            # plt.savefig(output_pdf, dpi=300)
            with PdfPages(output_pdf) as pdf:
                pdf.savefig(fig)

        if show:
            plt.show()

        plt.close()
