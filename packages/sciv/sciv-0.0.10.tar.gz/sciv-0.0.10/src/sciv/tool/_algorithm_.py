# -*- coding: UTF-8 -*-

import math
import random
from typing import Union, Tuple, Literal, Optional

from scipy import sparse
from scipy.stats import norm
from tqdm import tqdm

import numpy as np
from anndata import AnnData
import pandas as pd
from pandas import DataFrame

from .. import util as ul
from ..util import (
    matrix_data,
    to_sparse,
    to_dense,
    sparse_matrix,
    dense_data,
    number,
    collection,
    get_index,
    check_adata_get,
    matrix_dot_block_storage,
    vector_multiply_block_storage,
    matrix_division_block_storage,
    matrix_multiply_block_storage,
    enrichment_optional,
    difference_peak_optional
)

__name__: str = "tool_algorithm"


def sigmoid(data: Union[collection, matrix_data]) -> Union[collection, matrix_data]:
    return 1 / (1 + np.exp(-data))


def z_score_normalize(
    data: matrix_data,
    with_mean: bool = True,
    ri_sparse: bool | None = None,
    is_sklearn: bool = False
) -> Union[dense_data, sparse_matrix]:
    """
    Matrix standardization (z-score)
    :param data: Standardized data matrix required.
    :param with_mean: If True, center the data before scaling.
    :param ri_sparse: (return_is_sparse) Whether to return sparse matrix.
    :param is_sklearn: This parameter represents whether to use the sklearn package.
    :return: Standardized matrix.
    """
    ul.log(__name__).info("Matrix z-score standardization")

    if is_sklearn:
        from sklearn.preprocessing import StandardScaler

        scaler = StandardScaler(with_mean=with_mean)

        if with_mean:
            dense_data_ = to_dense(data, is_array=True)
        else:
            dense_data_ = data

        data = scaler.fit_transform(np.array(dense_data_))
    else:

        if sparse.issparse(data):
            _data_: sparse_matrix = data
            __mean__ = np.mean(_data_.data)
            __std__ = np.std(_data_.data)
            data.data = (_data_.data - __mean__) / (1 if __std__ == 0 else __std__)
            del _data_, __mean__, __std__
        else:
            __mean__ = np.mean(data)
            __std__ = np.std(data)
            data = (data - __mean__) / (1 if __std__ == 0 else __std__)

    return data if ri_sparse is None else (to_sparse(data) if ri_sparse else to_dense(data))


def z_score_marginal(matrix: matrix_data, axis: Literal[0, 1] = 0) -> Tuple[matrix_data, matrix_data]:
    """
    Matrix standardization (z-score, marginal)
    :param matrix: Standardized data matrix required.
    :param axis: Standardize according to which dimension.
    :return: Standardized matrix.
    """
    ul.log(__name__).info("Start marginal z-score")
    matrix = np.matrix(to_dense(matrix))
    # Separate z-score for each element
    __mean__ = np.mean(matrix, axis=axis)
    __std__ = np.std(matrix, axis=axis)
    # Control denominator is not zero
    __std__[__std__ == 0] = 1
    _z_score_ = (matrix - __mean__) / __std__
    ul.log(__name__).info("End marginal z-score")
    return _z_score_, __mean__


def z_score_to_p_value(z_score: matrix_data):
    return 2 * (1 - norm.cdf(abs(z_score)))


def marginal_normalize(matrix: matrix_data, axis: Literal[0, 1] = 0, default: float = 1e-50) -> matrix_data:
    """
    Marginal standardization
    :param matrix: Standardized data matrix required;
    :param axis: Standardize according to which dimension;
    :param default: To prevent division by 0, this value needs to be added to the denominator.
    :return: Standardized data.
    """
    matrix = np.matrix(to_dense(matrix))
    __sum__ = np.sum(matrix, axis=axis)
    return matrix / (__sum__ + default)


def min_max_norm(data: matrix_data, axis: Literal[0, 1, -1] = -1) -> matrix_data:
    """
    Calculate min max standardized data
    :param data: input data;
    :param axis: Standardize according to which dimension.
    :return: Standardized data.
    """
    data = to_dense(data, is_array=True)

    # Judgment dimension
    if axis == -1:
        data_extremum = data.max() - data.min()
        if data_extremum == 0:
            data_extremum = 1
        new_data = (data - data.min()) / data_extremum
    elif axis == 0:
        data_extremum = np.array(data.max(axis=axis) - data.min(axis=axis)).flatten()
        data_extremum[data_extremum == 0] = 1
        new_data = (data - data.min(axis=axis).flatten()) / data_extremum
    elif axis == 1:
        data_extremum = np.array(data.max(axis=axis) - data.min(axis=axis)).flatten()
        data_extremum[data_extremum == 0] = 1
        new_data = (data - data.min(axis=axis).flatten()[:, np.newaxis]) / data_extremum[:, np.newaxis]
    else:
        ul.log(__name__).error(
            "The `axis` parameter supports only -1, 0, and 1, while other values will make the `scale` parameter value "
            "equal to 1."
        )
        raise ValueError("The `axis` parameter supports only -1, 0, and 1")

    return new_data


def symmetric_scale(
    data: matrix_data,
    scale: Union[number, collection] = 2.0,
    axis: Literal[0, 1, -1] = -1,
    is_verbose: bool = True
) -> matrix_data:
    """
    Symmetric scale Function
    :param data: input data;
    :param axis: Standardize according to which dimension;
    :param scale: scaling factor.
    :param is_verbose: log information.
    :return: Standardized data
    """

    from scipy import special

    if is_verbose:
        ul.log(__name__).info("Start symmetric scale function")

    # Judgment dimension
    if axis == -1:
        scale = 1 if scale == 0 else scale
        x_data = to_dense(data) / scale
    elif axis == 0:
        scale = to_dense(scale, is_array=True).flatten()
        scale[scale == 0] = 1
        x_data = to_dense(data) / scale
    elif axis == 1:
        scale = to_dense(scale, is_array=True).flatten()
        scale[scale == 0] = 1
        x_data = to_dense(data) / scale[:, np.newaxis]
    else:
        ul.log(__name__).warning("The `axis` parameter supports only -1, 0, and 1, while other values will make the `scale` parameter value equal to 1.")
        x_data = to_dense(data)

    # Record symbol information
    symbol = to_dense(x_data).copy()
    symbol[symbol > 0] = 1
    symbol[symbol < 0] = -1

    # Log1p standardized data
    y_data = np.multiply(x_data, symbol)
    y_data = special.log1p(y_data)
    del x_data

    # Return symbols and make changes and sigmoid mapped data
    z_data = np.multiply(y_data, symbol)

    if is_verbose:
        ul.log(__name__).info("End symmetric scale function")
    return z_data


def mean_symmetric_scale(data: matrix_data, axis: Literal[0, 1, -1] = -1, is_verbose: bool = True) -> matrix_data:
    """
    Calculate the mean symmetric
    :param data: input data;
    :param axis: Standardize according to which dimension.
    :param is_verbose: log information.
    :return: Standardized data after average symmetry.
    """

    # Judgment dimension
    if axis == -1:
        return symmetric_scale(data, np.abs(data).mean(), axis=-1, is_verbose=is_verbose)
    elif axis == 0:
        return symmetric_scale(data, np.abs(data).mean(axis=0), axis=0, is_verbose=is_verbose)
    elif axis == 1:
        return symmetric_scale(data, np.abs(data).mean(axis=1), axis=1, is_verbose=is_verbose)
    else:
        ul.log(__name__).warning("The `axis` parameter supports only -1, 0, and 1")
        raise ValueError("The `axis` parameter supports only -1, 0, and 1")


def coefficient_of_variation(matrix: matrix_data, axis: Literal[0, 1, -1] = 0, default: float = 0) -> Union[float, collection]:

    if axis == -1:
        _std_ = np.array(np.std(matrix))
        _mean_ = np.array(np.mean(matrix))

        if _mean_ == 0:
            return default
        else:
            factor = _std_ / _mean_

            if factor == 0:
                return default

            return factor
    else:
        _std_ = np.array(np.std(matrix, axis=axis))
        _mean_ = np.array(np.mean(matrix, axis=axis))
        _mean_[_mean_ == 0] = 1 if default == 0 else default
        # coefficient of variation
        factor = _std_ / _mean_
        factor[_std_ == 0] = default
        return factor


def is_asc_sort(positions_list: list) -> bool:
    """
    Judge whether the site is in ascending order
    :param positions_list: positions list.
    :return: True for ascending order, otherwise False.
    """
    length: int = len(positions_list)

    if length <= 1:
        return True

    tmp = positions_list[0]

    for i in range(1, length):
        if positions_list[i] < tmp:
            return False
        tmp = positions_list[i]

    return True


def lsi(data: matrix_data, n_components: int = 50) -> dense_data:
    """
    SVD LSI
    :param data: input cell feature data;
    :param n_components: Dimensions that need to be reduced to.
    :return: Reduced dimensional data (SVD LSI model).
    """

    from sklearn.decomposition import TruncatedSVD

    if data.shape[1] <= n_components:
        ul.log(__name__).info("The features of the data are less than or equal to the `n_components` parameter, ignoring LSI")
        return to_dense(data, is_array=True)
    else:
        ul.log(__name__).info("Start LSI")
        svd = TruncatedSVD(n_components=n_components)
        svd_data = svd.fit_transform(to_dense(data, is_array=True))
        ul.log(__name__).info("End LSI")
        return svd_data


def pca(data: matrix_data, n_components: int = 50) -> dense_data:
    """
    PCA
    :param data: input cell feature data;
    :param n_components: Dimensions that need to be reduced to.
    :return: Reduced dimensional data.
    """
    from sklearn.decomposition import PCA

    if data.shape[1] <= n_components:
        ul.log(__name__).info("The features of the data are less than or equal to the `n_components` parameter, ignoring PCA")
        return to_dense(data, is_array=True)
    else:
        ul.log(__name__).info("Start PCA")
        data = to_dense(data, is_array=True)
        pca_n = PCA(n_components=n_components)
        pca_n.fit_transform(data)
        pca_data = pca_n.transform(data)
        ul.log(__name__).info("End PCA")
        return pca_data


# noinspection SpellCheckingInspection
def laplacian_eigenmaps(data: matrix_data, n_components: int = 2) -> dense_data:
    """
    Laplacian Eigenmaps
    :param data: input cell feature data;
    :param n_components: Dimensions that need to be reduced to.
    :return: Reduced dimensional data.
    """
    from sklearn.manifold import SpectralEmbedding

    if data.shape[1] <= n_components:
        ul.log(__name__).info(
            "The features of the data are less than or equal to the `n_components` parameter, ignoring Laplacian "
            "Eigenmaps"
        )
        return to_dense(data, is_array=True)
    else:
        ul.log(__name__).info("Start Laplacian Eigenmaps")
        data = to_dense(data, is_array=True)
        se = SpectralEmbedding(n_components=n_components)
        se_data = se.fit_transform(data)
        ul.log(__name__).info("End Laplacian Eigenmaps")
        return se_data


def semi_mutual_knn_weight(
    data: matrix_data,
    neighbors: int = 30,
    or_neighbors: int = 1,
    weight: float = 0.1,
    is_mknn_fully_connected: bool = True
) -> Tuple[matrix_data, matrix_data]:
    """
    Mutual KNN with weight
    :param data: Input data matrix;
    :param neighbors: The number of nearest neighbors;
    :param or_neighbors: The number of or nearest neighbors;
    :param weight: The weight of interactions or operations;
    :param is_mknn_fully_connected: Is the network of MKNN an all connected graph?
        If the value is True, it ensures that a node is connected to at least the node that is not closest to itself.
        This parameter does not affect the result of SM-KNN (the first result), but only affects the result of traditional M-KNN (the second result).
    :return: Adjacency weight matrix
    """
    ul.log(__name__).info("Start semi-mutual KNN")

    if weight < 0 or weight > 1:
        ul.log(__name__).error("The `and_weight` parameter must be between 0 and 1.")
        raise ValueError("The `and_weight` parameter must be between 0 and 1.")

    new_data: matrix_data = to_dense(data).copy()

    for j in range(new_data.shape[0]):
        new_data[j, j] = 0

    def _knn_(_data_: matrix_data, _neighbors_: int) -> matrix_data:
        _cell_cell_knn_: matrix_data = _data_.copy()
        del _data_
        _cell_cell_knn_copy_: matrix_data = _cell_cell_knn_.copy()

        # Obtain numerical values for constructing a k-neighbor network
        cell_cell_affinity_sort = np.sort(_cell_cell_knn_, axis=1)
        cell_cell_value = cell_cell_affinity_sort[:, -(_neighbors_ + 1)]
        del cell_cell_affinity_sort
        _cell_cell_knn_[_cell_cell_knn_copy_ >= np.array(cell_cell_value).flatten()[:, np.newaxis]] = 1
        _cell_cell_knn_[_cell_cell_knn_copy_ < np.array(cell_cell_value).flatten()[:, np.newaxis]] = 0
        return _cell_cell_knn_

    cell_cell_knn = _knn_(new_data, neighbors)

    if neighbors == or_neighbors:
        cell_cell_knn_or = cell_cell_knn.copy()
    else:
        cell_cell_knn_or = _knn_(new_data, or_neighbors)

    # Obtain symmetric adjacency matrix, using mutual kNN algorithm
    adjacency_and_matrix = np.minimum(cell_cell_knn, cell_cell_knn.T)
    del cell_cell_knn
    adjacency_or_matrix = np.maximum(cell_cell_knn_or, cell_cell_knn_or.T)
    del cell_cell_knn_or
    adjacency_weight_matrix = (1 - weight) * adjacency_and_matrix + weight * adjacency_or_matrix
    del adjacency_or_matrix

    if is_mknn_fully_connected:
        cell_cell_knn = _knn_(new_data, 1)
        adjacency_and_matrix = np.maximum(adjacency_and_matrix, cell_cell_knn)

    ul.log(__name__).info("End semi-mutual KNN")
    return adjacency_weight_matrix, adjacency_and_matrix


def k_means(data: matrix_data, n_clusters: int = 2):
    """
    Perform k-means clustering on data
    :param data: Input data matrix;
    :param n_clusters: The number of clusters to form as well as the number of centroids to generate.
    :return: Tags after k-means clustering.
    """
    ul.log(__name__).info("Start K-means cluster")
    from sklearn.cluster import KMeans

    model = KMeans(n_clusters=n_clusters, n_init="auto")
    model.fit(to_dense(data, is_array=True))
    labels = model.labels_
    ul.log(__name__).info("End K-means cluster")
    return labels


def spectral_clustering(data: matrix_data, n_clusters: int = 2) -> collection:
    """
    Spectral clustering
    :param data: Input data matrix;
    :param n_clusters: The dimension of the projection subspace.
    :return: Tags after spectral clustering.
    """
    ul.log(__name__).info("Start spectral clustering")

    from sklearn.cluster import SpectralClustering

    data = to_dense(data, is_array=True)
    model = SpectralClustering(n_clusters=n_clusters)
    clusters_types = model.fit_predict(data)
    ul.log(__name__).info("End spectral clustering")
    return clusters_types


def tsne(data: matrix_data, n_components: int = 2) -> matrix_data:
    """
    T-SNE dimensionality reduction
    :param data: Data matrix that requires dimensionality reduction;
    :param n_components: Dimension of the embedded space.
    :return: Reduced dimensional data matrix
    """
    from sklearn.manifold import TSNE

    data = to_dense(data, is_array=True)
    _tsne_ = TSNE(n_components=n_components)
    _tsne_.fit(data)
    data_tsne = _tsne_.fit_transform(data)
    return data_tsne


def umap(data: matrix_data, n_neighbors: float = 15, n_components: int = 2, min_dist: float = 0.15) -> matrix_data:
    """
    UMAP dimensionality reduction
    :param data: Data matrix that requires dimensionality reduction;
    :param n_neighbors: float (optional, default 15)
        The size of local neighborhood (in terms of number of neighboring
        sample points) used for manifold approximation. Larger values
        result in more global views of the manifold, while smaller
        values result in more local data being preserved. In general
        values should be in the range 2 to 100;
    :param n_components: The dimension of the space to embed into. This defaults to 2 to
        provide easy visualization, but can reasonably be set to any
        integer value in the range 2 to 100.
    :param min_dist: The effective minimum distance between embedded points. Smaller values
        will result in a more clustered/clumped embedding where nearby points
        on the manifold are drawn closer together, while larger values will
        result on a more even dispersal of points. The value should be set
        relative to the ``spread`` value, which determines the scale at which
        embedded points will be spread out.
    :return: Reduced dimensional data matrix
    """
    import umap as umap_
    data = to_dense(data, is_array=True)
    embedding = umap_.UMAP(n_neighbors=n_neighbors, n_components=n_components, min_dist=min_dist).fit_transform(data)
    return embedding


def kl_divergence(data1: matrix_data, data2: matrix_data) -> float:
    """
    Calculate KL divergence for two data
    :param data1: First data;
    :param data2: Second data.
    :return: KL divergence score
    """
    from scipy import stats

    data1 = to_dense(data1, is_array=True).flatten()
    data2 = to_dense(data2, is_array=True).flatten()
    return stats.entropy(data1, data2)


def calinski_harabasz(data: matrix_data, labels: collection) -> float:
    """
    The Calinski-Harabasz index is also one of the indicators used to evaluate the quality of clustering models.
    It measures the compactness within the cluster and the separation between clusters in the clustering results. The
    larger the value, the better the clustering effect
    :param data: First data;
    :param labels: Predicted labels for each sample.
    :return:
    """
    from sklearn.metrics import calinski_harabasz_score
    return calinski_harabasz_score(to_dense(data, is_array=True), labels)


def silhouette(data: matrix_data, labels: collection) -> float:
    """
    silhouette
    :param data: An array of pairwise distances between samples, or a feature array;
    :param labels: Predicted labels for each sample.
    :return: index
    """
    from sklearn.metrics import silhouette_score
    return silhouette_score(to_dense(data, is_array=True), labels)


def davies_bouldin(data: matrix_data, labels: collection) -> float:
    """
    Davies-Bouldin index (DBI)
    :param data: A list of ``n_features``-dimensional data points. Each row corresponds to a single data point;
    :param labels: Predicted labels for each sample.
    :return: index
    """
    from sklearn.metrics import davies_bouldin_score
    return davies_bouldin_score(to_dense(data, is_array=True), labels)


def ari(labels_pred: collection, labels_true: collection) -> float:
    """
    ARI (-1, 1)
    :param labels_pred: Predictive labels for clustering;
    :param labels_true: Real labels for clustering.
    :return: index
    """
    from sklearn.metrics import adjusted_rand_score
    return adjusted_rand_score(labels_true, labels_pred)


def ami(labels_pred: collection, labels_true: collection) -> float:
    """
    AMI (0, 1)
    :param labels_pred: Predictive labels for clustering;
    :param labels_true: Real labels for clustering.
    :return: index
    """
    from sklearn.metrics import adjusted_mutual_info_score
    return adjusted_mutual_info_score(labels_true, labels_pred)


def binary_indicator(labels_true: collection, labels_pred: collection) -> Tuple[float, float, float, float, float, float, float]:
    """
    Accuracy, Recall, F1, FPR, TPR, AUROC, AUPRC
    :param labels_true: Real labels for clustering;
    :param labels_pred: Predictive labels for clustering.
    :return: Indicators
    """
    from sklearn.metrics import accuracy_score, recall_score, f1_score, roc_curve, roc_auc_score, average_precision_score
    acc_s = accuracy_score(labels_true, labels_pred)
    rec_s = recall_score(labels_true, labels_pred)
    f1_s = f1_score(labels_true, labels_pred)
    fpr, tpr, thresholds = roc_curve(labels_true, labels_pred)
    auroc_s = roc_auc_score(labels_true, labels_pred)
    auprc_s = average_precision_score(labels_true, labels_pred)
    return acc_s, rec_s, f1_s, fpr, tpr, auroc_s, auprc_s


class RandomWalk:
    """
    Random walk
    """

    def __init__(
        self,
        cc_adata: AnnData,
        init_status: AnnData,
        epsilon: float = 1e-05,
        gamma: float = 0.05,
        enrichment_gamma: float = 0.05,
        p: int = 2,
        min_seed_cell_rate: float = 0.01,
        max_seed_cell_rate: float = 0.05,
        credible_threshold: float = 0,
        enrichment_threshold: Union[enrichment_optional, float] = 'golden',
        benchmark_count: int = 10,
        is_ablation: bool = False,
        is_simple: bool = True
    ):
        """
        Perform random walk steps
        :param cc_adata: Cell features;
        :param init_status: For cell scores under each trait;
        :param epsilon: conditions for stopping in random walk;
        :param gamma: reset weight for random walk;
        :param enrichment_gamma: reset weight for random walk for enrichment;
        :param p: Distance used for loss {1: Manhattan distance, 2: Euclidean distance};
        :param min_seed_cell_rate: The minimum percentage of seed cells in all cells;
        :param max_seed_cell_rate: The maximum percentage of seed cells in all cells.
        :param credible_threshold: The threshold for determining the credibility of enriched cells in the context of
            enrichment, i.e. the threshold for judging enriched cells;
        :param enrichment_threshold: Only by setting a threshold for the standardized output TRS can a portion of the enrichment
            results be obtained. Parameters support string types {'golden', 'half', 'e', 'pi', 'none'}, or valid floating-point types
            within the range of (0, log1p(1)).
        :param is_ablation: True represents obtaining the results of the ablation experiment. This parameter is limited by
            the `is_simple` parameter, and its effectiveness requires setting `is_simple` to `False`;
        :param is_simple: True represents not adding unnecessary intermediate variables, only adding the final result.
            It is worth noting that when set to `True`, the `is_ablation` parameter will become invalid, and when set to
            `False`, `is_ablation` will only take effect;
        :return: Stable distribution score.
        """
        ul.log(__name__).info("Random walk.")
        # judge length
        if cc_adata.shape[0] != init_status.shape[0]:
            ul.log(__name__).error(
                f"The number of rows {cc_adata.shape[0]} in the data is not equal to the initialization state length "
                f"{np.array(init_status).size}"
            )
            raise ValueError(
                f"The number of rows {cc_adata.shape[0]} in the data is not equal to the initialization state length "
                f"{np.array(init_status).size}"
            )

        if p <= 0:
            ul.log(__name__).error(
                "The value of `p` must be greater than zero. Distance used for loss {1: Manhattan distance, "
                "2: Euclidean distance}"
            )
            raise ValueError(
                "The value of `p` must be greater than zero. Distance used for loss {1: Manhattan distance, "
                "2: Euclidean distance}"
            )
        elif p > 3:
            ul.log(__name__).warning("Suggested value for `p` is 1 or 2.")

        if epsilon > 0.1:
            ul.log(__name__).warning(
                f"Excessive value of parameter `epsilon`=({epsilon}) can lead to incorrect iteration and poor "
                f"enrichment effect."
            )
        elif epsilon <= 0:
            ul.log(__name__).error("The parameter of `epsilon` must be greater than zero.")
            raise ValueError("The parameter of `epsilon` must be greater than zero.")

        if "clusters" not in init_status.obs.columns:
            ul.log(__name__).error("Unsupervised clustering information must be included in column `clusters` of `init_datus.obs`.")
            raise ValueError("Unsupervised clustering information must be included in column `clusters` of `init_datus.obs`.")

        init_status.obs["clusters"] = init_status.obs["clusters"].astype(str)

        self.cc_adata = cc_adata
        self.epsilon = epsilon
        self.gamma = gamma
        self.enrichment_gamma = enrichment_gamma
        self.p = p
        self.min_seed_cell_rate = min_seed_cell_rate
        self.max_seed_cell_rate = max_seed_cell_rate
        self.credible_threshold = credible_threshold
        self.is_simple = is_simple
        self.is_ablation = is_ablation
        self.benchmark_count = benchmark_count
        self._enrichment_seed_cell_min_count_ = 3

        if not is_simple and self.is_ablation:
            if "cell_mutual_knn" not in cc_adata.layers:
                ul.log(__name__).error("The ablation requires `cell_mutual_knn` to be in `cc_adata.layers`.")
                raise ValueError("The ablation requires `cell_mutual_knn` to be in `cc_adata.layers`.")

        if isinstance(enrichment_threshold, float):

            if enrichment_threshold <= 0 or enrichment_threshold >= np.log1p(1):
                ul.log(__name__).warning("The `enrichment_threshold` parameter is not set within the range of (0, log1p(1)), this parameter will become invalid.")
                ul.log(__name__).warning("It is recommended to set the `enrichment_threshold` parameter to the 'golden' value.")

            self.enrichment_threshold = enrichment_threshold
        elif enrichment_threshold == "golden":
            golden_ratio = (1 + math.sqrt(5)) / 2
            self.enrichment_threshold = np.log1p(1) / (1 + 1 / golden_ratio)
        elif enrichment_threshold == "half":
            self.enrichment_threshold = np.log1p(1) / 2
        elif enrichment_threshold == "e":
            self.enrichment_threshold = np.log1p(1) / np.e
        elif enrichment_threshold == "pi":
            self.enrichment_threshold = np.log1p(1) / np.pi
        elif enrichment_threshold == "none":
            self.enrichment_threshold = np.log1p(1)
        else:
            raise ValueError(
                f"Invalid enrichment settings. The string type in the `enrichment_threshold` parameter only supports the following parameter "
                f"'golden', 'half', 'e', 'pi',  Alternatively, input a floating-point type value within the range of (0, log1p(1))"
            )

        # Enrichment judgment
        self.is_run_core = False
        self.is_run_ablation_m_knn = False
        self.is_run_ablation_ncw = False
        self.is_run_ablation_nsw = False
        self.is_run_ablation_ncsw = False

        self.is_run_enrichment = False
        self.is_run_en_ablation_m_knn = False
        self.is_run_en_ablation_ncw = False
        self.is_run_en_ablation_nsw = False
        self.is_run_en_ablation_ncsw = False

        self.is_benchmark = False
        self.cluster_size_factor = {}

        self.cell_affinity = to_dense(cc_adata.layers["cell_affinity"])

        self.init_status: AnnData = init_status
        self.trait_info: list = list(init_status.var["id"])

        self.trs_adata: AnnData = AnnData(np.zeros(init_status.shape), obs=init_status.obs, var=init_status.var)
        self.trs_adata.uns = init_status.uns
        self.trs_adata.layers["init_trs"] = to_sparse(init_status.X)

        self.cell_anno = self.trs_adata.obs

        if not is_simple:
            for _layer_ in init_status.layers:
                self.trs_adata.layers[_layer_] = to_sparse(init_status.layers[_layer_])

        self.cell_size: int = self.trs_adata.shape[0]

        # trait
        self.trait_list: list = list(self.trs_adata.var_names)
        self.trait_range = range(len(self.trait_list))

        self.trs_source = np.zeros(init_status.shape)
        self.trs_source_positive = np.zeros(init_status.shape)
        self.trs_source_negative = np.zeros(init_status.shape)

        if not is_simple and self.is_ablation:
            self.trs_m_knn_source = np.zeros(init_status.shape)
            self.trs_ncw_source = np.zeros(init_status.shape)
            self.trs_nsw_source = np.zeros(init_status.shape)
            self.trs_ncsw_source = np.zeros(init_status.shape)
            self.random_seed_cell = np.zeros(init_status.shape)

        # Transition Probability Matrix
        self.weight = self._get_weight_(self.cc_adata.X)

        if not is_simple and self.is_ablation:
            self.weight_m_knn = self._get_weight_(self.cc_adata.layers["cell_mutual_knn"])

        self.cluster_types, self.init_seed_cell_size = self._get_cluster_info_()

        (
            self.seed_cell_count,
            self.seed_cell_threshold,
            self.seed_cell_weight_nsw,
            self.seed_cell_weight,
            self.seed_cell_index,
            self.seed_cell_weight_en_nsw,
            self.seed_cell_weight_en
        ) = self._get_seed_cell_()

        if not is_simple and self.is_ablation:
            init_status_no_weight = check_adata_get(init_status, "init_trs_ncw")
            (
                self.seed_cell_count_nw,
                self.seed_cell_threshold_nw,
                self.seed_cell_weight_ncsw,
                self.seed_cell_weight_ncw,
                _,
                self.seed_cell_weight_en_ncsw,
                self.seed_cell_weight_en_ncw
            ) = self._get_seed_cell_(init_data=init_status_no_weight, info="ablation")

    def _random_walk_(self, seed_cell_vector: collection, weight: matrix_data = None, gamma: float = 0.05) -> matrix_data:
        """
        Perform a random walk
        :param seed_cell_vector: seed cells;
        :param weight: weight matrix;
        :param gamma: reset weight.
        :return: The value after random walk.
        """

        if weight is None:
            w = to_dense(self.weight).copy()
        else:
            w = to_dense(weight).copy()

        # Random walk
        p0 = seed_cell_vector.copy()[:, np.newaxis]
        pt: matrix_data = seed_cell_vector.copy()[:, np.newaxis]
        k = 0
        delta = 1

        # iteration
        while delta > self.epsilon:
            p1 = (1 - gamma) * np.dot(w, pt) + gamma * p0

            # 1 and 2, It would be faster alone
            if self.p == 1:
                delta = np.abs(pt - p1).sum()
            elif self.p == 2:
                delta = np.sqrt(np.square(np.abs(pt - p1)).sum())
            else:
                delta = np.float_power(np.float_power(np.abs(pt - p1), self.p).sum(), 1.0 / self.p)

            pt = p1
            k += 1

        return pt.flatten()

    def _random_walk_core_(self, seed_cell_vector: collection, weight: matrix_data = None) -> matrix_data:
        """
        Perform a random walk
        :param seed_cell_vector: seed cells;
        :param weight: weight matrix.
        :return: The value after random walk.
        """
        return self._random_walk_(seed_cell_vector, weight, self.gamma)

    @staticmethod
    def _get_weight_(cell_cell_matrix: matrix_data) -> matrix_data:
        """
        Obtain weights in random walk
        :param cell_cell_matrix: Cell to cell connectivity matrix
        :return: weight matrix
            1. The weights used in the iteration of random walk.
            2. Assign different weight matrices to seed cells.
        """
        data_weight = to_dense(cell_cell_matrix, is_array=True)
        cell_sum_weight = data_weight.sum(axis=1)[:, np.newaxis]
        cell_sum_weight[cell_sum_weight == 0] = 1
        return data_weight / cell_sum_weight

    def _get_cell_weight_(self, seed_cell_size: int) -> matrix_data:
        _cell_cell_knn_: matrix_data = self.cell_affinity.copy()

        # Obtain numerical values for constructing a k-neighbor network
        cell_cell_affinity_sort = np.sort(_cell_cell_knn_, axis=1)
        cell_cell_value = cell_cell_affinity_sort[:, -(seed_cell_size + 1)]
        del cell_cell_affinity_sort
        _cell_cell_knn_[self.cell_affinity < np.array(cell_cell_value).flatten()[:, np.newaxis]] = 0
        return _cell_cell_knn_

    def _get_seed_cell_size_(self, cell_size: int) -> int:
        seed_cell_size: int = self.init_seed_cell_size if self.init_seed_cell_size < cell_size else cell_size

        # Control the number of seeds
        if (seed_cell_size / self.cell_size) < self.min_seed_cell_rate:
            seed_cell_size = np.ceil(self.min_seed_cell_rate * self.cell_size).astype(int)
        elif (seed_cell_size / self.cell_size) > self.max_seed_cell_rate:
            seed_cell_size = np.ceil(self.max_seed_cell_rate * self.cell_size).astype(int)

        if seed_cell_size == 0:
            seed_cell_size = 3
        elif seed_cell_size > cell_size:
            seed_cell_size = cell_size

        return seed_cell_size

    def _get_cluster_info_(self) -> Tuple[list, int]:
        # cluster size/count
        cluster_types = list(set(self.trs_adata.obs["clusters"]))
        cluster_types.sort()

        clusters = list(self.trs_adata.obs["clusters"])

        for cluster in cluster_types:
            count = clusters.count(cluster)
            self.cluster_size_factor.update({str(cluster): count})

        seed_cell_size = min(self.cluster_size_factor.values())

        self.trs_adata.uns["cluster_info"] = {
            "cluster_size_factor": self.cluster_size_factor,
            "min_seed_cell_rate": self.min_seed_cell_rate,
            "max_seed_cell_rate": self.max_seed_cell_rate,
            "init_seed_cell_size": seed_cell_size
        }
        return cluster_types, seed_cell_size

    def _get_seed_cell_clustering_weight_(self, seed_cell_index: collection) -> Tuple[collection, dict]:
        """
        This function is used to obtain the percentage of seed cells that occupy this cell type, i.e., the seed cell clustering weight.
        The purpose of this weight is to provide fair enrichment opportunities for those with fewer cell numbers in cell clustering types.
        :param seed_cell_index: Index of seed cells.
        :return: The seed cell clustering weight, equity factor.
        """
        cell_anno: DataFrame = self.cell_anno.copy()
        cell_clusters = cell_anno["clusters"].values
        seed_cell_cell_anno: DataFrame = cell_anno.iloc[seed_cell_index]

        seed_cell_cell_clusters: list = cell_clusters[seed_cell_index].tolist()
        seed_cell_cell_cluster_rate = {}

        for _k_, _v_ in self.cluster_size_factor.items():
            seed_cell_cell_cluster_rate.update({_k_: seed_cell_cell_clusters.count(_k_) / _v_})

        seed_cell_cluster_weight = seed_cell_cell_anno["clusters"].map(seed_cell_cell_cluster_rate).values
        return mean_symmetric_scale(seed_cell_cluster_weight, is_verbose=False), seed_cell_cell_cluster_rate

    def _get_seed_cell_weight_(
        self,
        seed_cell_index: collection,
        value: collection,
        seed_cell_index_enrichment: collection = None
    ) -> collection:

        if seed_cell_index_enrichment is None:
            seed_cell_index_enrichment = seed_cell_index

        # Calculate the degree of seed cells in the seed cell network
        seed_cell_mutual_knn = np.array(self.cell_affinity[seed_cell_index, :][:, seed_cell_index])
        seed_weight_degree: collection = seed_cell_mutual_knn.sum(axis=0)
        seed_weight_degree_weight = mean_symmetric_scale(seed_weight_degree, is_verbose=False)

        # Calculate the initialization score weight
        seed_cell_value = value[seed_cell_index_enrichment]
        seed_cell_value_weight = mean_symmetric_scale(seed_cell_value, is_verbose=False)

        # Percentage weight of seed cells in cell type clustering
        seed_cell_clustering_weight = self._get_seed_cell_clustering_weight_(seed_cell_index)[0]
        seed_weight_value = seed_weight_degree_weight * seed_cell_value_weight * seed_cell_clustering_weight

        # Calculate weight
        seed_weight_value = seed_weight_value / (1 if np.sum(seed_weight_value) == 0 else np.sum(seed_weight_value))
        return seed_weight_value

    def _get_seed_cell_(
        self,
        init_data: AnnData = None,
        info: str = None
    ) -> Tuple[collection, collection, matrix_data, matrix_data, matrix_data, matrix_data, matrix_data]:
        """
        Obtain information related to seed cells
        :param init_data: Initial TRS data
        :param info: Log information about seed cells
        :return:
            1. Set seed cell thresholds for each trait or disease.
            2. Seed cell weights obtained for each trait or disease based on the `init_data` parameter, with each seed cell assigned the same weight.
                Note that this only takes effect when `is_simple` is true.
            3. Seed cell weights obtained for each trait or disease based on the init_data parameter, and the weight of each seed cell will be assigned based on the similarity between cells.
            4. Seed cell index, which will be used for later knockout or knockdown prediction.
            5. Based on the init_data parameter, a reference seed cell weight is obtained for enrichment analysis assistance for each trait or disease, and each seed cell is assigned the same weight.
                Note that this only takes effect when `is_simple` is true.
            6. Reference seed cell weights for auxiliary enrichment analysis of each trait or disease based on the init_data parameter,
                and the weight of each seed cell will be assigned based on the similarity between cells.
        """

        if init_data is None:
            init_data = self.init_status

        # seed cell threshold
        seed_cell_count: collection = np.zeros(len(self.trait_list)).astype(int)
        seed_cell_threshold: collection = np.zeros(len(self.trait_list))
        seed_cell_weight: matrix_data = np.zeros(self.trs_adata.shape)
        seed_cell_index: matrix_data = np.zeros(self.trs_adata.shape)
        seed_cell_weight_en: matrix_data = np.zeros(self.trs_adata.shape)

        if not self.is_simple:
            seed_cell_matrix: matrix_data = np.zeros(self.trs_adata.shape)
            seed_cell_matrix_en: matrix_data = np.zeros(self.trs_adata.shape)
        else:
            seed_cell_matrix: matrix_data = np.zeros((1, 1))
            seed_cell_matrix_en: matrix_data = np.zeros((1, 1))

        ul.log(__name__).info(f"Calculate {len(self.trait_list)} traits/diseases for seed cells information.{f' ({info})' if info is not None else ''}")
        for i in tqdm(self.trait_range):

            # Obtain all cell score values in a trait
            trait_adata: AnnData = init_data[:, i]
            trait_value: collection = to_dense(trait_adata.X, is_array=True).flatten()

            # Obtain the maximum initial score
            trait_value_max = np.max(trait_value)
            trait_value_min = np.min(trait_value)

            if trait_value_min != trait_value_max:

                # Obtain a cell count greater than zero
                trait_value_sort_index = np.argsort(trait_value).astype(int)
                trait_value_sort_index = trait_value_sort_index[::-1]
                _gto_cell_index_ = trait_value > 0
                _gt0_cell_size_ = trait_value[_gto_cell_index_].size

                _seed_cell_size_ = self._get_seed_cell_size_(_gt0_cell_size_)

                seed_cell_count[i] = _seed_cell_size_
                seed_cell_threshold[i] = trait_value[trait_value_sort_index[_seed_cell_size_]]

                # Set seed cell weights (reduce noise seed cell weights)
                _seed_cell_index_ = trait_value_sort_index[0:_seed_cell_size_]
                seed_cell_index[:, i][_seed_cell_index_] = 1
                seed_cell_weight[:, i][_seed_cell_index_] = self._get_seed_cell_weight_(seed_cell_index=_seed_cell_index_, value=trait_value)

                _enrichment_start_index_: int = _seed_cell_size_
                _enrichment_end_index_: int = 2 * _seed_cell_size_ if self.cell_size > 2 * _seed_cell_size_ else _seed_cell_size_ - 1

                if _gt0_cell_size_ == _seed_cell_size_:
                    _enrichment_start_index_ = int(_seed_cell_size_ - self._enrichment_seed_cell_min_count_) if _seed_cell_size_ > self._enrichment_seed_cell_min_count_ else ((_seed_cell_size_ - 1) if _seed_cell_size_ > 2 else 0)
                    _enrichment_end_index_ = _seed_cell_size_

                _seed_cell_en_index_ = trait_value_sort_index[_enrichment_start_index_:_enrichment_end_index_]
                _seed_cell_en_weight_ = self._get_seed_cell_weight_(seed_cell_index=_seed_cell_index_ if len(_seed_cell_en_index_) == len(_seed_cell_index_) else _seed_cell_en_index_, value=trait_value, seed_cell_index_enrichment=_seed_cell_en_index_)
                seed_cell_weight_en[:, i][_seed_cell_en_index_] = _seed_cell_en_weight_

                if not self.is_simple and self.is_ablation:
                    # Without weight
                    seed_cell_value = np.zeros(self.cell_size)
                    seed_cell_value[_seed_cell_index_] = 1
                    seed_cell_matrix[:, i] = seed_cell_value / (1 if seed_cell_value.sum() == 0 else seed_cell_value.sum())
                    seed_cell_en_value = np.zeros(self.cell_size)
                    seed_cell_en_value[_seed_cell_en_index_] = 1
                    seed_cell_matrix_en[:, i] = seed_cell_en_value / (1 if seed_cell_en_value.sum() == 0 else seed_cell_en_value.sum())

        return seed_cell_count, seed_cell_threshold, seed_cell_matrix, seed_cell_weight, seed_cell_index, seed_cell_matrix_en, seed_cell_weight_en

    @staticmethod
    def scale_norm(score: matrix_data, is_verbose: bool = False) -> matrix_data:
        cell_value = mean_symmetric_scale(score, axis=0, is_verbose=is_verbose)
        cell_value = np.log1p(min_max_norm(cell_value, axis=0))
        return cell_value

    def _simple_error_(self) -> None:

        if self.is_simple and "is_simple" in self.trs_adata.uns.keys() and self.trs_adata.uns["is_simple"]:
            ul.log(__name__).error("The parameter `is_simple` is True, so running this method is not supported.")
            raise RuntimeError("The parameter `is_simple` is True, so running this method is not supported.")

    def run_benchmark(self) -> None:
        """
        Perform random walk of random seeds on all traits.
        """
        self._simple_error_()

        ul.log(__name__).info(f"Calculate {len(self.trait_list)} traits/diseases for process `run_benchmark` (Count: {self.benchmark_count}). (Randomly perturb seed cells. ===> `benchmark`)")

        total_steps = len(self.trait_list) * self.benchmark_count
        with tqdm(total=total_steps) as pbar:
            for i in self.trait_range:

                cell_value = np.zeros(self.cell_size)

                for _ in range(self.benchmark_count):
                    # Set random seed information
                    random_seed_cell = np.zeros(self.cell_size)
                    random_seed_index = np.random.choice(np.arange(0, self.cell_size), size=self.seed_cell_count[i], replace=False)

                    # Obtain all cell score values in a trait
                    trait_adata: AnnData = self.init_status[:, i]
                    trait_value: collection = to_dense(trait_adata.X, is_array=True).flatten()

                    # Obtain the maximum initial score
                    trait_value_max = np.max(trait_value)
                    trait_value_min = np.min(trait_value)

                    if trait_value_min != trait_value_max:
                        # seed cell weight
                        random_seed_cell[random_seed_index] = 1 / self.cell_size

                        # Random walk
                        cell_value += self._random_walk_core_(random_seed_cell)
                    pbar.update(1)
                # Remove the influence of background
                self.random_seed_cell[:, i] = cell_value / self.benchmark_count

        cell_value = self.scale_norm(self.random_seed_cell)
        self.trs_adata.layers["benchmark"] = to_sparse(cell_value)
        self.is_benchmark = True

    @staticmethod
    def _get_label_description_(label: str) -> Tuple[str, str]:
        if label == "run_core" or label == "run_en":
            return "Calculate random walk with weighted seed cells.", "trs"
        elif label == "run_ablation_ncsw" or label == "run_en_ablation_ncsw":
            return "Removed cell weights in random walk and cluster type weights in initial scores.", "trs_ncsw"
        elif label == "run_ablation_nsw" or label == "run_en_ablation_nsw":
            return "Removed cell weights from random walk.", "trs_nsw"
        elif label == "run_ablation_ncw" or label == "run_en_ablation_ncw":
            return "Removed cell cluster type weights in initial scores.", "trs_ncw"
        elif label == "run_ablation_m_knn" or label == "run_en_ablation_m_knn":
            return "Using the M-KNN method during the execution of weighted random walks.", "trs_m_knn"
        elif label == "run_knock (positive)":
            return "Run knockout or knockdown by random walk with weight. (positive)", "knock_effect_positive"
        elif label == "run_knock (negative)":
            return "Run knockout or knockdown by random walk with weight. (negative)", "knock_effect_negative"
        elif label == "run_knock_control (control & positive)":
            return "Run knockout or knockdown by random walk with weight. (control & positive)", "knock_effect_positive_control"
        elif label == "run_knock_control (control & negative)":
            return "Run knockout or knockdown by random walk with weight. (control & negative)", "knock_effect_negative_control"
        else:
            raise ValueError(f"{label} is not a valid information.")

    def _run_(self, seed_cell_data: matrix_data, label: str, weight: matrix_data = None) -> matrix_data:
        """
        Calculate random walk
        :param seed_cell_data: Seed cell data
        :return: Return values without `scale` normalization
        """

        if weight is None:
            weight = self.weight

        score = np.zeros(self.trs_adata.shape)

        _log_info_, _layer_label_ = self._get_label_description_(label)
        ul.log(__name__).info(f"Calculate {len(self.trait_list)} traits/diseases for process `{label}`. ({_log_info_} ===> `{_layer_label_}`)")

        for i in tqdm(self.trait_range):
            score[:, i] = self._random_walk_core_(seed_cell_data[:, i], weight=weight)

        cell_value = self.scale_norm(score)

        if _layer_label_ == "trs":
            self.trs_adata.X = to_sparse(cell_value)
        else:
            self.trs_adata.layers[_layer_label_] = to_sparse(cell_value)

        return score

    def run_core(self) -> None:
        """
        Calculate weighted random walk
        """
        if not self.is_simple:
            self.trs_adata.layers["seed_cell_weight"] = to_sparse(self.seed_cell_weight)

        self.trs_adata.layers["seed_cell_index"] = to_sparse(self.seed_cell_index)

        self.trs_adata.var["seed_cell_count"] = self.seed_cell_count
        self.trs_adata.var["seed_cell_threshold"] = self.seed_cell_threshold
        self.trs_source = self._run_(self.seed_cell_weight, "run_core")

        self.trs_adata.layers["trs_source"] = to_sparse(self.trs_source)
        self.is_run_core = True

    def run_ablation_m_knn(self) -> None:
        """
        Using M-KNN fully connected cellular network
        """
        self._simple_error_()
        self.trs_m_knn_source = self._run_(self.seed_cell_weight, "run_ablation_m_knn", self.weight_m_knn)
        self.is_run_ablation_m_knn = True

    def run_ablation_ncw(self) -> None:
        """
        Removed cell cluster type weights in initial scores
        """
        self._simple_error_()
        self.trs_adata.layers["seed_cell_weight_ncw"] = self.seed_cell_weight_ncw

        if "seed_cell_count_nw" not in self.trs_adata.var.columns:
            self.trs_adata.var["seed_cell_count_nw"] = self.seed_cell_count_nw

        if "seed_cell_threshold_nw" not in self.trs_adata.var.columns:
            self.trs_adata.var["seed_cell_threshold_nw"] = self.seed_cell_threshold_nw

        self.trs_ncw_source = self._run_(self.seed_cell_weight_ncw, "run_ablation_ncw")
        self.is_run_ablation_ncw = True

    def run_ablation_nsw(self) -> None:
        """
        Removed cell weights from random walk
        """
        self._simple_error_()
        self.trs_adata.layers["seed_cell_weight_nsw"] = self.seed_cell_weight_nsw
        self.trs_nsw_source = self._run_(self.seed_cell_weight_nsw, "run_ablation_nsw")
        self.is_run_ablation_nsw = True

    def run_ablation_ncsw(self) -> None:
        """
        Removed cell weights in random walk and cluster type weights in initial scores
        """
        self._simple_error_()
        self.trs_adata.layers["seed_cell_weight_ncsw"] = self.seed_cell_weight_ncsw

        if "seed_cell_count_nw" not in self.trs_adata.var.columns:
            self.trs_adata.var["seed_cell_count_nw"] = self.seed_cell_count_nw

        if "seed_cell_threshold_nw" not in self.trs_adata.var.columns:
            self.trs_adata.var["seed_cell_threshold_nw"] = self.seed_cell_threshold_nw

        self.trs_ncsw_source = self._run_(self.seed_cell_weight_ncsw, "run_ablation_ncsw")
        self.is_run_ablation_ncsw = True

    def _run_enrichment_(self, seed_cell_en_weight: matrix_data, label: str) -> None:
        """
        Enrichment analysis of traits/cells
        :param seed_cell_en_weight: Seed cell data
        """

        _layer_label_: str = "tre"

        source_value: matrix_data = self.trs_source

        _, _trs_layer_label_ = self._get_label_description_(label)

        if label == "run_en":
            if not self.is_run_core:
                ul.log(__name__).warning("Need to run the `run_core` method first in order to run this method. Start run...")
                self.run_core()

        elif label == "run_en_ablation_m_knn":
            if not self.is_run_ablation_m_knn:
                ul.log(__name__).warning("Need to run the `run_ablation_m_knn` method first in order to run this method. Start run...")
                self.run_ablation_m_knn()

            _layer_label_ = "tre_m_knn"
            source_value = self.trs_m_knn_source

        elif label == "run_en_ablation_ncw":
            if not self.is_run_ablation_ncw:
                ul.log(__name__).warning("Need to run the `run_ablation_ncw` method first in order to run this method. Start run...")
                self.run_ablation_ncw()

            _layer_label_ = "tre_ncw"
            source_value = self.trs_ncw_source

        elif label == "run_en_ablation_nsw":
            if not self.is_run_ablation_nsw:
                ul.log(__name__).warning("Need to run the `run_ablation_nsw` method first in order to run this method. Start run...")
                self.run_ablation_nsw()

            _layer_label_ = "tre_nsw"
            source_value = self.trs_nsw_source

        elif label == "run_en_ablation_ncsw":
            if not self.is_run_ablation_ncsw:
                ul.log(__name__).warning("Need to run the `run_ablation_ncsw` method first in order to run this method. Start run...")
                self.run_ablation_ncsw()

            _layer_label_ = "tre_ncsw"
            source_value = self.trs_ncsw_source

        else:
            raise ValueError(f"{label} error. `run_en`, `run_en_ablation_m_knn`, `run_en_ablation_ncw`, `run_en_ablation_nsw` or `run_en_ablation_ncsw`")

        cell_anno: DataFrame = self.cell_anno.copy()
        trs_score = to_dense(self.trs_adata.X if label == "run_en" else self.trs_adata.layers[_trs_layer_label_], is_array=True)

        # Initialize enriched container
        trait_cell_enrichment = np.zeros(self.trs_adata.shape)
        trait_cell_credible = np.zeros(self.trs_adata.shape)

        ul.log(__name__).info(f"Calculate {len(self.trait_list)} traits/diseases for process `{label}`. (Enrichment)")
        for i in tqdm(self.trait_range):
            # Random walk
            cell_value = self._random_walk_(seed_cell_en_weight[:, i], weight=self.weight_m_knn if label == "run_en_ablation_m_knn" else self.weight, gamma=self.enrichment_gamma)
            # separate
            cell_value_credible = mean_symmetric_scale(np.array(source_value[:, i]).flatten() - np.array(cell_value).flatten(), is_verbose=False)

            # This step is only executed if it contains cell clustering type weights
            if label == "run_en" or label == "run_en_ablation_nsw" or label == "run_en_ablation_m_knn":
                _enrichment_index_ = trs_score[:, i] > self.enrichment_threshold

                if np.any(_enrichment_index_):
                    # Ratio of cell clustering types enriched by threshold
                    _, _clustering_map_ = self._get_seed_cell_clustering_weight_(_enrichment_index_)
                    _clustering_weight_ = cell_anno["clusters"].map(_clustering_map_)
                    _clustering_weight_ = mean_symmetric_scale(_clustering_weight_, is_verbose=False)
                    _clustering_weight_mean_ = _clustering_weight_.mean()
                    # Correction score
                    cell_value_credible += (_clustering_weight_ - _clustering_weight_mean_)

            trait_cell_enrichment[:, i][cell_value_credible > self.credible_threshold] = 1
            trait_cell_credible[:, i] = cell_value_credible

        self.trs_adata.layers[_layer_label_] = to_sparse(trait_cell_enrichment.astype(int))

        if not self.is_simple:
            self.trs_adata.layers[f"credible_{_layer_label_}"] = to_sparse(trait_cell_credible)

    def run_enrichment(self) -> None:
        """
        Enrichment analysis
        """
        self._run_enrichment_(self.seed_cell_weight_en, "run_en")
        self.is_run_enrichment = True

    def run_en_ablation_m_knn(self) -> None:
        """
        Using M-KNN fully connected cellular network (Enrichment analysis)
        """
        self._simple_error_()
        self._run_enrichment_(self.seed_cell_weight_en, "run_en_ablation_m_knn")
        self.is_run_en_ablation_m_knn = True

    def run_en_ablation_ncw(self) -> None:
        """
        Removed cell cluster type weights in initial scores
        """
        self._simple_error_()
        self._run_enrichment_(self.seed_cell_weight_en_ncw, "run_en_ablation_ncw")
        self.is_run_en_ablation_ncw = True

    def run_en_ablation_nsw(self) -> None:
        """
        Removed cell weights from random walk
        """
        self._simple_error_()
        self._run_enrichment_(self.seed_cell_weight_en_nsw, "run_en_ablation_nsw")
        self.is_run_en_ablation_nsw = True

    def run_en_ablation_ncsw(self) -> None:
        """
        Removed cell weights in random walk and cluster type weights in initial scores
        """
        self._simple_error_()
        self._run_enrichment_(self.seed_cell_weight_en_ncsw, "run_en_ablation_ncsw")
        self.is_run_en_ablation_ncsw = True

    def run_knock(self, trs: AnnData, knock_trait: str, is_control: bool = False) -> None:

        if trs.shape[0] != self.cell_size:
            ul.log(__name__).error(f"The number of cells ({trs.shape[0]}) in the input `trs` is inconsistent with the number of cells ({self.cell_size}) in the knockdown after knockout")
            raise ValueError(f"The number of cells ({trs.shape[0]}) in the input `trs` is inconsistent with the number of cells ({self.cell_size}) in the knockdown after knockout.")

        if "trs_source" not in trs.layers:
            ul.log(__name__).error("`trs_source` is not in `trs.layers`, please execute function `ml.core` first to obtain the result as input for the `trs` parameter.")
            raise ValueError("`trs_source` is not in `trs.layers`, please execute function `ml.core` first to obtain the result as input for the `trs` parameter.")

        if "seed_cell_index" not in trs.layers:
            ul.log(__name__).error("`seed_cell_index` is not in `trs.layers`, please execute function `ml.core` first to obtain the result as input for the `trs` parameter.")
            raise ValueError("`seed_cell_index` is not in `trs.layers`, please execute function `ml.core` first to obtain the result as input for the `trs` parameter.")

        if knock_trait not in trs.var["id"]:
            ul.log(__name__).error(f"`{knock_trait}` trait or disease does not exist.")
            raise ValueError(f"`{knock_trait}` trait or disease does not exist.")

        knock_info_content = "run_knock_control" if is_control else "run_knock"

        ul.log(__name__).info(f"Calculate {len(self.trait_list)} for seed cells information. ({knock_info_content})")
        init_trait_source_value: matrix_data = to_dense(trs[:, knock_trait].layers["init_trs"])
        init_trait_value: matrix_data = to_dense(self.trs_adata.layers["init_trs"])

        init_trait_positive_effect = init_trait_source_value - init_trait_value
        init_trait_positive_effect[init_trait_positive_effect < 0] = 0
        init_trait_negative_effect = init_trait_value - init_trait_source_value
        init_trait_negative_effect[init_trait_negative_effect < 0] = 0

        self.trs_adata.layers["init_trait_positive"] = to_sparse(init_trait_positive_effect)
        self.trs_adata.layers["init_trait_negative"] = to_sparse(init_trait_negative_effect)

        init_trait_positive_adata = check_adata_get(self.trs_adata, "init_trait_positive")
        (_, positive_seed_cell_threshold, _, positive_seed_cell_weight, _, _, _,) = self._get_seed_cell_(init_data=init_trait_positive_adata, info="knock (positive)")

        init_trait_negative_adata = check_adata_get(self.trs_adata, "init_trait_negative")
        (_, negative_seed_cell_threshold, _, negative_seed_cell_weight, _, _, _,) = self._get_seed_cell_(init_data=init_trait_negative_adata, info="knock (negative)")

        self.trs_adata.var["positive_seed_cell_threshold"] = positive_seed_cell_threshold
        self.trs_adata.var["negative_seed_cell_threshold"] = negative_seed_cell_threshold

        if is_control:
            ul.log(__name__).info("Perturb the initialization TRS.")
            for i in tqdm(self.trait_range):
                positive_seed_cell_weight[:, i] = perturb_data(positive_seed_cell_weight[:, i], 1.0)
                negative_seed_cell_weight[:, i] = perturb_data(negative_seed_cell_weight[:, i], 1.0)

        # Obtain the result after random walk
        _positive_label_: str = "control & positive" if is_control else "positive"
        self.trs_source_positive = self._run_(positive_seed_cell_weight, f"{knock_info_content} ({_positive_label_})")
        _negative_label_: str = "control & negative" if is_control else "negative"
        self.trs_source_negative = self._run_(negative_seed_cell_weight, f"{knock_info_content} ({_negative_label_})")

        self.trs_adata.layers["knock_effect_positive_control" if is_control else "knock_effect_positive"] = to_sparse(self.trs_source_positive)
        self.trs_adata.layers["knock_effect_negative_control" if is_control else "knock_effect_negative"] = to_sparse(self.trs_source_negative)

        ul.log(__name__).info("Obtain the effect size of knocking out or knocking down ==> .layers[\"{}\"]".format("knock_effect_control" if is_control else "knock_effect"))
        knock_effect_value = self.trs_source_positive - self.trs_source_negative
        self.trs_adata.layers["knock_effect_source_control" if is_control else "knock_effect_source"] = to_sparse(knock_effect_value)
        self.trs_adata.layers["knock_effect_control" if is_control else "knock_effect"] = to_sparse(mean_symmetric_scale(knock_effect_value, axis=0, is_verbose=False))


def euclidean_distances(data1: matrix_data, data2: matrix_data = None, block_size: int = -1) -> matrix_data:
    """
    Calculate the Euclidean distance between two matrices
    :param data1: First data;
    :param data2: Second data (If the second data is empty, it will default to the first data.)
    :param block_size: The size of the segmentation stored in block wise matrix multiplication.
        If the value is less than or equal to zero, no block operation will be performed
    :return: Data of Euclidean distance.
    """
    ul.log(__name__).info("Start euclidean distances")

    if data2 is None:
        data2 = data1.copy()

    data1 = to_dense(data1)
    data2 = to_dense(data2)
    __data1_sum_sq__ = np.power(data1, 2).sum(axis=1)
    data1_sum_sq = __data1_sum_sq__.reshape((-1, 1))
    data2_sum_sq = __data1_sum_sq__ if data2 is None else np.power(data2, 2).sum(axis=1)
    del __data1_sum_sq__

    distances = data1_sum_sq + data2_sum_sq - 2 * matrix_dot_block_storage(data1, data2.transpose(), block_size)
    del data1_sum_sq, data2_sum_sq

    distances[distances < 0] = 0.0
    distances = np.sqrt(distances)
    return distances


def overlap(regions: DataFrame, variants: DataFrame) -> DataFrame:
    """
    Relate the peak region and variant site
    :param regions: peaks information
    :param variants: variants information
    :return: The variant maps data in the peak region
    """
    regions_columns: list = list(regions.columns)

    if "chr" not in regions_columns or "start" not in regions_columns or "end" not in regions_columns:
        ul.log(__name__).error(
            f"The peaks information {regions_columns} in data `adata` must include three columns: `chr`, `start` and "
            f"`end`. (It is recommended to use the `read_sc_atac` method.)"
        )
        raise ValueError(
            f"The peaks information {regions_columns} in data `adata` must include three columns: `chr`, `start` and "
            f"`end`. (It is recommended to use the `read_sc_atac` method.)"
        )

    columns = ['variant_id', 'index', 'chr', 'position', 'rsId', 'chr_a', 'start', 'end']

    if regions.shape[0] == 0 or variants.shape[0] == 0:
        ul.log(__name__).warning("Data is empty.")
        return pd.DataFrame(columns=columns)

    regions = regions.rename_axis("index")
    regions = regions.reset_index()
    # sort
    regions_sort = regions.sort_values(["chr", "start", "end"])[["index", "chr", "start", "end"]]
    variants_sort = variants.sort_values(["chr", "position"])[["variant_id", "chr", "position", "rsId"]]

    # Intersect and Sort
    chr_keys: list = list(set(regions_sort["chr"]).intersection(set(variants_sort["chr"])))
    chr_keys.sort()

    variants_chr_type: dict = {}
    variants_position_list: dict = {}

    # Cyclic region chromatin
    for chr_key in chr_keys:
        # variant chr information
        sort_chr_regions_chr = variants_sort[variants_sort["chr"] == chr_key]
        variants_chr_type.update({chr_key: sort_chr_regions_chr})
        variants_position_list.update({chr_key: list(sort_chr_regions_chr["position"])})

    variants_overlap_info_list: list = []

    for index, chr_a, start, end in zip(regions_sort["index"], regions_sort["chr"], regions_sort["start"], regions_sort["end"]):

        # judge chr
        if chr_a in chr_keys:
            # get chr variant
            variants_chr_type_position_list = variants_position_list[chr_a]
            # judge start and end position
            if start <= variants_chr_type_position_list[-1] and end >= variants_chr_type_position_list[0]:
                # get index
                start_index = get_index(start, variants_chr_type_position_list)
                end_index = get_index(end, variants_chr_type_position_list)

                # Determine whether it is equal, Equality means there is no overlap
                if start_index != end_index:
                    start_index = start_index if isinstance(start_index, number) else start_index[1]
                    end_index = end_index + 1 if isinstance(end_index, number) else end_index[1]

                    if start_index > end_index:
                        ul.log(__name__).error("The end index in the region is greater than the start index.")
                        raise IndexError("The end index in the region is greater than the start index.")

                    variants_chr_type_chr_a = variants_chr_type[chr_a]
                    # get data
                    variants_overlap_info: DataFrame = variants_chr_type_chr_a[start_index:end_index].copy()
                    variants_overlap_info["index"] = index
                    variants_overlap_info["chr_a"] = chr_a
                    variants_overlap_info["start"] = start
                    variants_overlap_info["end"] = end
                    variants_overlap_info.index = (variants_overlap_info["variant_id"].astype(str) + "_" + variants_overlap_info["index"].astype(str))
                    variants_overlap_info_list.append(variants_overlap_info)

    # merge result
    if len(variants_overlap_info_list) > 0:
        overlap_data: DataFrame = pd.concat(variants_overlap_info_list, axis=0)
    else:
        return pd.DataFrame(columns=columns)

    return overlap_data


def overlap_sum(regions: AnnData, variants: dict, trait_info: DataFrame) -> AnnData:
    """
    Overlap regional data and mutation data and sum the PP values of all mutations in a region as the values for that
    region.
    :param regions: peaks data
    :param variants: variants data
    :param trait_info: traits information
    :return: overlap data
    """

    # Unique feature set
    label_all = list(regions.var.index)
    # Peak number
    label_all_size: int = len(label_all)

    # trait/disease information
    trait_names: list = list(trait_info["id"])

    matrix = np.zeros((label_all_size, len(trait_names)))

    ul.log(__name__).info(f"Obtain peak-trait/disease matrix. (overlap variant information)")
    for trait_name in tqdm(trait_names):

        variant: AnnData = variants[trait_name]
        index: int = trait_names.index(trait_name)

        # handle overlap data
        overlap_info: DataFrame = overlap(regions.var, variant.obs)

        if overlap_info.shape[0] == 0:
            continue

        overlap_info.rename({"index": "label"}, axis="columns", inplace=True)
        overlap_info.reset_index(inplace=True)
        overlap_info["region_id"] = (
            overlap_info["chr"].astype(str)
            + ":" + overlap_info["start"].astype(str) + "-" + overlap_info["end"].astype(str)
        )

        # get region
        region_info = overlap_info.groupby("region_id", as_index=False)["label"].first()
        region_info.index = region_info["label"].astype(str)
        label: list = list(region_info["label"])

        # Mutation information with repetitive features
        label_size: int = len(label)

        for j in range(label_size):

            # Determine whether the features after overlap exist, In other words, whether there is overlap in this feature
            if label[j] in label_all:
                # get the index of label
                label_index = label_all.index(label[j])
                overlap_info_region = overlap_info[overlap_info["label"] == label[j]]
                # sum value
                overlap_variant = variant[list(overlap_info_region["variant_id"]), :]
                matrix[label_index, index] = overlap_variant.X.sum(axis=0)

    overlap_adata = AnnData(to_sparse(matrix), var=trait_info, obs=regions.var)
    overlap_adata.uns["is_overlap"] = True
    return overlap_adata


def calculate_fragment_weighted_accessibility(
    input_data: dict,
    block_size: int = -1
) -> matrix_data:
    """
    Calculate the initial trait- or disease-related cell score
    :param input_data:
        1. data: Convert the `counts` matrix to the `fragments` matrix using the `scvi.data.reads_to_fragments`
        2. overlap_data: Peaks-traits/diseases data
    :param block_size: The size of the segmentation stored in block wise matrix multiplication.
        If the value is less than or equal to zero, no block operation will be performed
    :return: Initial TRS
    """

    if "data" not in input_data:
        ul.log(__name__).error("The `data` field needs to be included in parameter `input_data`.")
        raise ValueError("The `data` field needs to be included in parameter `input_data`.")

    if "overlap_data" not in input_data:
        ul.log(__name__).error("The `overlap_data` field needs to be included in parameter `input_data`.")
        raise ValueError("The `overlap_data` field needs to be included in parameter `input_data`.")

    # Processing data
    ul.log(__name__).info("Data pre conversion.")

    matrix = to_dense(input_data["data"])
    del input_data["data"]

    # init_score
    overlap_matrix = to_dense(input_data["overlap_data"])
    del input_data["overlap_data"]

    # Summation information
    ul.log(__name__).info("Calculate expected counts matrix ===> (numerator)")
    row_col_multiply = vector_multiply_block_storage(matrix.sum(axis=1), matrix.sum(axis=0), block_size=block_size)

    all_sum = matrix.sum()

    ul.log(__name__).info("Calculate expected counts matrix.")
    row_col_multiply = matrix_division_block_storage(row_col_multiply, all_sum, block_size=block_size, data=row_col_multiply)

    ul.log(__name__).info("Calculate fragment weighted accessibility ===> (denominator)")
    global_scale_data = matrix_dot_block_storage(row_col_multiply, overlap_matrix, block_size=block_size)
    del row_col_multiply
    global_scale_data[global_scale_data == 0] = global_scale_data[global_scale_data != 0].min() / 2
    ul.log(__name__).info("Calculate fragment weighted accessibility ===> (numerator)")
    init_score: matrix_data = matrix_dot_block_storage(matrix, overlap_matrix, block_size=block_size)
    del matrix, overlap_matrix
    ul.log(__name__).info("Calculate fragment weighted accessibility.")
    init_score: matrix_data = matrix_division_block_storage(init_score, global_scale_data, block_size=block_size, data=init_score)

    return init_score


def calculate_init_score_weight(
    adata: AnnData,
    da_peaks_adata: AnnData,
    overlap_adata: AnnData,
    top_rate: Optional[float] = None,
    diff_peak_value: difference_peak_optional = 'emp_effect',
    is_simple: bool = True,
    block_size: int = -1
) -> AnnData:
    """
    Calculate the initial trait- or disease-related cell score with weight.
    :param adata: scATAC-seq data;
    :param da_peaks_adata: Differential peak data;
    :param overlap_adata: Peaks-traits/diseases data;
    :param top_rate: Only retaining a specified proportion of peak information in peak correction of clustering type differences;
        The default is the reciprocal of the number of Leiden clustering types.
    :param diff_peak_value: Specify the correction value in peak correction of clustering type differences.
        {'emp_effect', 'bayes_factor', 'emp_prob1', 'all'}
    :param is_simple: True represents not adding unnecessary intermediate variables, only adding the final result. It
        is worth noting that when set to `True`, the `is_ablation` parameter will become invalid, and when set to
        `False`, `is_ablation` will only take effect;
    :param block_size: The size of the segmentation stored in block wise matrix multiplication.
        If the value is less than or equal to zero, no block operation will be performed
    :return: Initial TRS with weight.
    """
    if "is_overlap" not in overlap_adata.uns:
        ul.log(__name__).warning("The `is_overlap` is not in `overlap_data.uns`. (Need to execute function `tl.overlap_sum`)")

    if "dp_delta" not in da_peaks_adata.uns:
        ul.log(__name__).warning("The `dp_delta` is not in `da_peaks_adata.uns`. (Need to execute function `pp.poisson_vi`)")

    if top_rate is not None and (top_rate <= 0 or top_rate >= 1):
        ul.log(__name__).error("The parameter of `top_rate` should be between 0 and 1, or not set.")
        raise ValueError("The parameter of `top_rate` should be between 0 and 1, or not set.")

    if top_rate is not None and top_rate >= 0.5:
        ul.log(__name__).error("The `top_rate` value is set to be greater than or equal to 0.5, it is recommended to be less than this value.")

    cluster_size: int = adata.uns["poisson_vi"]["cluster_size"]

    if top_rate is None:
        top_rate = 1 / cluster_size

    top_peak_count: int = int(np.ceil(top_rate * da_peaks_adata.shape[1]))

    fragments = adata.layers["fragments"]
    overlap_matrix = to_dense(overlap_adata.X)

    ul.log(__name__).info("Calculate cell type weight")

    def _get_cluster_weight_(da_matrix: matrix_data):
        _cluster_weight_data_: matrix_data = matrix_dot_block_storage(to_dense(min_max_norm(da_matrix, axis=0)), overlap_matrix, block_size=block_size)
        return sigmoid(mean_symmetric_scale(_cluster_weight_data_, axis=0, is_verbose=False))

    if diff_peak_value == "emp_effect":
        _cluster_weight_ = _get_cluster_weight_(da_peaks_adata.X)
    elif diff_peak_value == "bayes_factor":
        _cluster_weight_ = _get_cluster_weight_(da_peaks_adata.layers["bayes_factor"])
    elif diff_peak_value == "emp_prob1":
        _cluster_weight_ = _get_cluster_weight_(da_peaks_adata.layers["emp_prob1"])
    elif diff_peak_value == "all":
        _cluster_weight1_ = _get_cluster_weight_(da_peaks_adata.X)
        _cluster_weight2_ = _get_cluster_weight_(da_peaks_adata.layers["bayes_factor"])
        _cluster_weight3_ = _get_cluster_weight_(da_peaks_adata.layers["emp_prob1"])
        _cluster_weight_ = (_cluster_weight1_ + _cluster_weight2_ + _cluster_weight3_) / 3
        del _cluster_weight1_, _cluster_weight2_, _cluster_weight3_
    else:
        ul.log(__name__).error("The `diff_peak_value` parameter only supports one of the {'emp_effect', 'bayes_factor', 'emp_prob1', 'all'} values.")
        raise ValueError("The `diff_peak_value` parameter only supports one of the {'emp_effect', 'bayes_factor', 'emp_prob1', 'all'} values.")

    # calculate
    input_data: dict = {
        "data": fragments,
        "overlap_data": overlap_matrix
    }
    del fragments, overlap_matrix
    _init_trs_ncw_ = calculate_fragment_weighted_accessibility(input_data, block_size=block_size)

    # enrichment_factor
    cluster_weight_factor = _cluster_weight_.copy()

    da_peaks_adata.obsm["cluster_weight"] = to_sparse(_cluster_weight_)

    ul.log(__name__).info("Broadcasting the weight factor to the cellular level")
    anno_info = adata.obs
    _cell_type_weight_ = np.zeros((adata.shape[0], _cluster_weight_.shape[1]))
    del _cluster_weight_

    for cluster in da_peaks_adata.obs_names:
        _cluster_weight_tmp_ = da_peaks_adata[cluster, :].obsm["cluster_weight"]
        _cell_type_weight_[anno_info["clusters"] == cluster, :] = to_dense(_cluster_weight_tmp_, is_array=True).flatten()
        del _cluster_weight_tmp_

    ul.log(__name__).info("Calculate trait- or disease-cell related initial score")
    _init_trs_weight_ = matrix_multiply_block_storage(_init_trs_ncw_, _cell_type_weight_, block_size=block_size)

    init_trs_adata = AnnData(to_sparse(_init_trs_weight_), obs=adata.obs, var=overlap_adata.var)
    del _init_trs_weight_

    if not is_simple:
        init_trs_adata.layers["init_trs_ncw"] = to_sparse(_init_trs_ncw_)
        init_trs_adata.layers["cell_type_weight"] = to_sparse(_cell_type_weight_)
        init_trs_adata.uns["cluster_weight_factor"] = to_sparse(cluster_weight_factor)

    del _init_trs_ncw_, _cell_type_weight_

    init_trs_adata.uns["is_sample"] = is_simple
    init_trs_adata.uns["top_rate"] = top_rate
    init_trs_adata.uns["top_peak_count"] = top_peak_count
    return init_trs_adata


def obtain_cell_cell_network(
    adata: AnnData,
    k: int = 30,
    or_k: int = 1,
    weight: float = 0.1,
    gamma: Optional[float] = None,
    is_simple: bool = True
) -> AnnData:
    """
    Calculate cell-cell correlation
    :param adata: scATAC-seq data;
    :param k: When building an mKNN network, the number of nodes connected by each node (and);
    :param or_k: When building an mKNN network, the number of nodes connected by each node (or);
    :param weight: The weight of interactions or operations;
    :param gamma: If None, defaults to 1.0 / n_features. Otherwise, it should be strictly positive;
    :param is_simple: True represents not adding unnecessary intermediate variables, only adding the final result.
        It is worth noting that when set to `True`, the `is_ablation` parameter will become invalid, and when set to
        `False`, `is_ablation` will only take effect;
    :return: Cell similarity data.
    """

    from sklearn.metrics.pairwise import laplacian_kernel

    # data
    if "poisson_vi" not in adata.uns.keys():
        ul.log(__name__).error(
            "`poisson_vi` is not in the `adata.uns` dictionary, and the scATAC-seq data needs to be processed through "
            "the `poisson_vi` function."
        )
        raise ValueError(
            "`poisson_vi` is not in the `adata.uns` dictionary, and the scATAC-seq data needs to be processed through "
            "the `poisson_vi` function."
        )

    _latent_name_ = "latent" if adata.uns["poisson_vi"]["latent_name"] is None else adata.uns["poisson_vi"]["latent_name"]
    latent = adata.obsm[_latent_name_]
    del _latent_name_
    cell_anno = adata.obs

    ul.log(__name__).info("Laplacian kernel")
    # Laplacian kernel
    cell_affinity = laplacian_kernel(latent, gamma=gamma)

    # Define KNN network
    cell_mutual_knn_weight, cell_mutual_knn = semi_mutual_knn_weight(cell_affinity, neighbors=k, or_neighbors=or_k, weight=weight, is_mknn_fully_connected=False)

    # cell-cell graph
    cc_data: AnnData = AnnData(to_sparse(cell_mutual_knn_weight), var=cell_anno, obs=cell_anno)
    cc_data.layers["cell_affinity"] = to_sparse(cell_affinity)

    if not is_simple:
        cc_data.layers["cell_mutual_knn"] = to_sparse(cell_mutual_knn)

    return cc_data


def perturb_data(data: collection, percentage: float) -> collection:
    """
    Randomly perturbs the positions of a percentage of data.
    :param data: List of data elements to be perturbed.
    :param percentage: Percentage of data to be perturbed.
    :return: Perturbed data list.
    """

    if percentage <= 0 or percentage > 1:
        raise ValueError("The value of the `percentage` parameter must be greater than 0 and less than or equal to 1.")

    new_data = data.copy()
    num_elements = len(new_data)
    num_to_perturb = int(num_elements * percentage)

    # Select random indices to perturb
    indices_to_perturb = random.sample(range(num_elements), num_to_perturb)

    # Swap elements at selected indices with other random elements
    for index in indices_to_perturb:
        swap_index = random.choice([i for i in range(num_elements) if i != index])
        new_data[index], new_data[swap_index] = new_data[swap_index], new_data[index]

    return new_data


def add_noise(data: matrix_data, rate: float) -> matrix_data:
    """
    Add peak percentage noise to each cell
    """

    if rate <= 0 or rate >= 1:
        raise ValueError("The value of the `rate` parameter must be greater than 0 and less than 1.")

    shape = data.shape
    noise = to_dense(data.copy())

    for i in tqdm(range(shape[0])):
        count_i = np.array(noise[i, :]).flatten()
        # Add noise to the accessibility of unopened chromatin
        count0_i = count_i[count_i == 0]
        max_i = np.max(count_i)
        count0 = int(count0_i.size * rate)
        noise0_i = np.random.randint(low=1, high=2 if max_i < 2 else max_i, size=count0)
        random_index0 = np.random.choice(np.arange(0, count0_i.size), size=count0, replace=False)
        count0_i[random_index0] = noise0_i
        count_i_value = count_i.copy()
        count_i_value[count_i_value == 0] = count0_i
        noise[i, :] = count_i_value

        # Close open chromatin accessibility
        count1_i = count_i[count_i == 1]
        count1 = int(count1_i.size * rate)
        random_index1 = np.random.choice(np.arange(0, count1_i.size), size=count1, replace=False)
        count1_i[random_index1] = 0
        count_i[count_i == 1] = count1_i
        noise[i, :] = count_i

        # disturbance
        noise[i, :] = perturb_data(noise[i, :], rate)

    return noise
