# -*- coding: UTF-8 -*-

import math
import os
import pickle
import random
import shutil
import string
from typing import Tuple, Union, Literal

import numpy as np
import pandas as pd
from numpy import asarray
from anndata import AnnData
from pandas import DataFrame
from scipy import sparse
from tqdm import tqdm

from yzm_file import StaticMethod
from yzm_log import Logger

from .. import util as ul
from ._constant_ import dense_data, sparse_data, sparse_matrix, matrix_data, number, collection, project_name

__name__: str = "util_core"


def file_method(name: str = None) -> StaticMethod:
    name = f"{project_name}_{name}" if name is not None else project_name
    return StaticMethod(log_file=os.path.join(ul.log_file_path, name), is_form_log_file=ul.is_form_log_file)


def log(name: str = None) -> Logger:
    name = f"{project_name}_{name}" if name is not None else project_name
    return Logger(name, log_path=os.path.join(ul.log_file_path, name), is_form_file=ul.is_form_log_file)


def to_dense(sm: matrix_data, is_array: bool = False) -> dense_data:
    """
    Convert sparse matrix to dense matrix
    :param sm: sparse matrix
    :param is_array: True converted to array form, False natural output
    :return: dense matrix
    """

    if sm is None:
        log(__name__).warning("The input matrix (sm parameter) is not feasible")
        return np.asmatrix([])

    if isinstance(sm, sparse_data):
        return np.array(sm.todense()) if is_array else sm.todense()

    dense_sm = sm.todense() if sparse.issparse(sm) else sm
    return np.array(dense_sm) if is_array else dense_sm


def to_sparse(dm: dense_data, way_callback=sparse.csr_matrix, is_matrix: bool = True) -> sparse_matrix:
    """
    Convert dense matrix to sparse matrix
    :param dm: dense matrix
    :param way_callback: How to form sparse matrix
    :param is_matrix: True converted to matrix form, False natural output
    :return: sparse matrix
    """

    if dm is None:
        log(__name__).warning("The input matrix (dm parameter) is not feasible")
        return sparse.coo_matrix([])

    if isinstance(dm, dense_data):
        return way_callback(dm) if is_matrix else dm

    sparse_m = dm if sparse.issparse(dm) else way_callback(dm)
    return way_callback(sparse_m) if is_matrix else sparse_m


def sum_min_max(data: matrix_data, axis: int = 1) -> Tuple[number, number]:
    """
    Obtain the minimum/maximum sum of rows in the matrix
    :param data: matrix data
    :param axis: {0, 1} 1: row, 0: col
    :return: Minimum value of rows, maximum value of rows
    """
    rows, cols = data.shape

    if rows == 0 or cols == 0:
        return 0, 0

    rows_sum = list(np.array(data.sum(axis=axis)).flatten())
    return min(rows_sum), max(rows_sum)


def get_index(position: number, positions_list: list) -> Union[number, Tuple[number, number]]:
    """
    Search for position information. Similar to half search.
        If the position exists in the list, return the index.
        If it does not exist, return the index located between the two indexes
    :param position: position
    :param positions_list: position list
    :return: position index
    """
    # sort
    positions_list.sort()
    # search
    position_size: int = len(positions_list)
    left, right = 0, position_size - 1

    while left <= right:
        mid = (left + right) // 2

        if positions_list[mid] == position:
            return mid
        elif positions_list[mid] > position:
            right = mid - 1
        else:
            left = mid + 1

    return right, left


def list_duplicate_set(data: list) -> list:
    """
    Append numbering to duplicate information
    :param data: input data
    :return: Unique data with constant quantity
    """

    if len(data) == len(set(data)):
        return data

    new_data = []
    range_data = range(len(data))

    is_warn: bool = False

    for i in range_data:

        # judge duplicate
        if data[i] not in new_data:
            new_data.append(data[i])
        else:
            j: int = 2

            while True:

                if not isinstance(data[i], str) and not is_warn:
                    log(__name__).warning("Convert non string types to string types.")
                    is_warn = True

                # format new index
                elem: str = data[i] + "+" + str(j)

                # Add index
                if elem not in new_data:
                    new_data.append(elem)
                    break

                j += 1

    return new_data


def get_sub_data(data: collection, size: int) -> collection:
    # get information
    old_size = len(data)

    if size >= old_size:
        log(__name__).warning("The given size is greater than the original data size")
        return data

    old_data: list = data.copy()
    rate = size / old_size
    # add sub data
    new_data: list = []

    for i in range(size):
        new_data.append(old_data[math.floor(rate * i)])

    return new_data


def split_matrix(data: matrix_data, axis: Literal[0, 1] = 0, chunk_number: int = 1000) -> list:
    # get size
    new_data = to_dense(data, is_array=True)
    rows, cols = new_data.shape

    # get number
    total: int = rows if axis == 0 else cols

    # get split number
    split_number = total // chunk_number

    # Determine whether to divide equally
    tail_number = total % chunk_number
    if tail_number != 0:
        split_number += 1

    log(__name__).info(f"Divide the matrix into {split_number} parts")

    # Add data
    split_data_list = []
    for i in range(split_number):
        # set index
        start_index: int = i * chunk_number
        end_index: int = total if (i + 1) * chunk_number > total else (i + 1) * chunk_number
        split_data = new_data[start_index:end_index, :] if axis == 0 else new_data[:, start_index:end_index]
        split_data_list.append(split_data)

    return split_data_list


def merge_matrix(datas: list, axis: Literal[0, 1] = 0) -> list:
    # get size
    size = len(datas)
    range_size = range(size)

    # get row col
    constant: int = datas[0].shape[1] if axis == 0 else datas[0].shape[0]
    total: int = 0
    shapes: list = []

    # get chunk size
    for i in range_size:
        shape = datas[i].shape
        judge = shape[1] if axis == 0 else shape[0]

        # judge size
        if judge != constant:
            log(__name__).error("Inconsistent traits in the input dataset set.")
            raise ValueError("Inconsistent traits in the input dataset set.")

        total += shape[0] if axis == 0 else shape[1]
        shapes.append(shape)

    # format matrix
    matrix_shape = (total if axis == 0 else constant, constant if axis == 0 else total)
    log(__name__).info(f"Merge matrix {matrix_shape} shape")
    matrix: matrix_data = np.zeros(matrix_shape)

    # merge matrix
    col_record: int = 0
    for i in range_size:
        col_i = datas[i].shape[0] if axis == 0 else datas[i].shape[1]
        if axis == 0:
            matrix[col_record:col_record + col_i, :] = datas[i]
        else:
            matrix[:, col_record:col_record + col_i] = datas[i]
        col_record += col_i

    return matrix


def list_index(data: list) -> Tuple[list, collection]:
    info: list = []

    size: int = len(data)

    types: asarray = np.unique(data)

    for type_ in types:
        type_info: list = []
        for i in range(size):
            if type_ == data[i]:
                type_info.append(i)
        info.append(set(type_info))

    return info, types


def numerical_bisection_step(min_value: float, max_value: float, step_length: float) -> Tuple[collection, int]:
    if min_value > max_value:
        log(__name__).error(f"`min_value` ({min_value}) must be smaller than `max_value` ({max_value}).")
        raise ValueError(f"`min_value` ({min_value}) must be smaller than `max_value` ({max_value}).")

    number_list: list = []

    i = 0
    while min_value <= max_value:
        number_list.append(min_value)
        i += 1
        min_value += step_length

    return number_list, i


def get_real_predict_label(
    df: DataFrame,
    map_cluster: Union[str, collection],
    clusters: str = "clusters",
    value: str = "value"
) -> Tuple[DataFrame, int, list]:
    df_sort: DataFrame = df.sort_values([value], ascending=False)

    # Obtain the type of positive set clustering corresponding to the trait
    cluster_list: list = []
    if isinstance(map_cluster, str):
        cluster_list.append(map_cluster)
    else:
        cluster_list = list(map_cluster)

    # total label size
    total_size = df.shape[0]

    # true label size
    df_sort.insert(0, "true_label", 0)
    df_sort.loc[df_sort[df_sort[clusters].isin(cluster_list)].index, "true_label"] = 1

    # predict label size
    df_cluster = df[df[clusters].isin(cluster_list)].copy()
    df_cluster_size = df_cluster.shape[0]
    predict_label = list(np.ones(df_cluster_size))
    predict_label.extend(np.zeros(total_size - df_cluster_size))
    df_sort.insert(0, "predict_label", 0)
    df_sort.loc[:, "predict_label"] = predict_label
    df_sort["predict_label"] = df_sort["predict_label"].astype(int)

    return df_sort, df_cluster_size, cluster_list


def strings_map_numbers(str_list: list, start: int = 0) -> list:
    # Create an empty dictionary to store the mapping of strings to numerical values
    mapping = {}

    # Traverse the list and assign a unique numerical value to each string
    for i, item in enumerate(set(str_list), start=start):  # 使用set去除重复项，并从1开始编号
        mapping[item] = i

    # Use list derivation to convert strings to corresponding numerical values
    numeric_list = [mapping[item] for item in str_list]

    return numeric_list


def down_sampling_data(data: Union[matrix_data | collection], sample_number: int = 1000000) -> list:
    """
    down-sampling
    :param data: Data that requires down-sampling;
    :param sample_number: How many samples (values) were down-sampled.
    :return: Data after down-sampling.
    """

    if isinstance(data, collection):

        # Judge data size
        if data.size <= sample_number:
            return list(data)

        index = np.random.choice(range(data.size), sample_number, replace=False)

        return list(np.array(data)[index])

    elif isinstance(data, matrix_data):

        # Judge data size
        if data.shape[0] * data.shape[1] <= sample_number:
            return list(to_dense(data, is_array=True).flatten())

        data = to_dense(data, is_array=True)
        row_count = data.shape[0]
        col_count = data.shape[1]

        if row_count < 0:
            log(__name__).error("The number of rows of data must be greater than zero")
            raise ValueError("The number of rows of data must be greater than zero")

        log(__name__).info(f"Kernel density estimation plot down-sampling data from {row_count * col_count} to {sample_number}")

        # get count
        count = row_count * col_count
        iter_number: int = count // sample_number
        iter_sample_number: int = sample_number // iter_number
        iter_sample_number_final: int = sample_number % iter_number

        if iter_sample_number < 1:
            log(__name__).error("The sampling data is too small, increase the `sample_number` parameter value")
            raise ValueError("The sampling data is too small, increase the `sample_number` parameter value")

        log(__name__).info(f"Divide and conquer {iter_number} chunks")

        # Create index container
        return_data: list = []

        for i in range(iter_number + 1):

            if iter_number < 50:
                log(__name__).info(f"Start {i + 1}th chunk, {(i + 1) / iter_number * 100}%")
            elif iter_number >= 50 and i % 50 == 0:
                log(__name__).info(f"Start {i + 1}th chunk, {(i + 1) / iter_number * 100}%")

            # Determine if it is the last cycle
            end_count: int = count if i == iter_number else (i + 1) * sample_number

            if iter_sample_number_final == 0:
                index = np.random.choice(range(i * sample_number, end_count), iter_sample_number, replace=False)
            else:
                per_iter_sample_number: int = iter_sample_number_final if i == iter_number else iter_sample_number
                index = np.random.choice(range(i * sample_number, end_count), per_iter_sample_number, replace=False)

            # Add index
            for j in index:
                # row
                row_index = j // col_count
                # column
                col_index = j % col_count

                if row_index >= row_count:
                    log(__name__).error(f"index ({row_index}) out of range ({row_count})")
                    raise IndexError(f"index ({row_index}) out of range ({row_count})")

                if col_index >= col_count:
                    log(__name__).error(f"index ({col_index}) out of range ({col_count})")
                    raise IndexError(f"index ({col_index}) out of range ({col_count})")

                return_data.append(data[row_index, col_index])

        return return_data
    else:
        ul.log(__name__).error("The input data type is incorrect.")
        raise ValueError("The input data type is incorrect.")


def matrix_dot_block_storage(
    data1: matrix_data,
    data2: matrix_data,
    block_size: int = 10000,
    data: matrix_data = None
) -> matrix_data:
    """
    Perform Cartesian product of two matrices through block storage method.
    :param data1: Matrix 1
    :param data2: Matrix 2
    :param block_size: The size of the segmentation stored in block wise matrix multiplication.
        If the value is less than or equal to zero, no block operation will be performed.
    :param data: Return the placeholder variables of the result matrix.
        If there is value, it will reduce the consumption of memory space.
    :return: Cartesian product result
    """
    n, m = data1.shape
    p, q = data2.shape

    if m != p:
        log(__name__).error(f"Need to meet the principle of matrix multiplication. ({m} != {p})")
        raise ValueError(f"Need to meet the principle of matrix multiplication. ({m} != {p})")

    if block_size <= 0 or n <= block_size and m <= block_size and q <= block_size:
        return np.dot(data1, data2)

    n_range = range(0, n, block_size)
    q_range = range(0, q, block_size)
    m_range = range(0, m, block_size)

    _cache_path_ = os.path.join(ul.project_cache_path, generate_str(50))
    file_method(__name__).makedirs(_cache_path_)

    # Store block data
    log(__name__).info("[matrix_dot_block_storage]: Store block data...")
    total_steps = len(n_range) * len(q_range) * len(m_range)
    with tqdm(total=total_steps) as pbar:
        for i in n_range:
            for j in q_range:
                for k in m_range:
                    i_max = min(i + block_size, n)
                    j_max = min(j + block_size, q)
                    k_max = min(k + block_size, m)

                    _matrix_ = np.dot(data1[i:i_max, k:k_max], data2[k:k_max, j:j_max])

                    with open(os.path.join(_cache_path_, str(i) + str(j) + str(k) + ".pkl"), 'wb') as f:
                        pickle.dump(_matrix_, f)

                    del _matrix_
                    pbar.update(1)

    del data1, data2

    if data is None or data.shape != (n, q):
        data = np.zeros((n, q))

    # Read data
    log(__name__).info("[matrix_dot_block_storage]: Read block data...")
    with tqdm(total=total_steps) as pbar:
        for i in n_range:
            for j in q_range:
                for k in m_range:
                    i_max = min(i + block_size, n)
                    j_max = min(j + block_size, q)

                    with open(os.path.join(_cache_path_, str(i) + str(j) + str(k) + ".pkl"), 'rb') as f:
                        _matrix_ = pickle.load(f)
                        data[i:i_max, j:j_max] += _matrix_
                        del _matrix_

                    pbar.update(1)

    shutil.rmtree(_cache_path_)

    return data


def matrix_multiply_block_storage(
    data1: matrix_data,
    data2: matrix_data,
    block_size: int = 10000,
    data: matrix_data = None
) -> matrix_data:
    """
    Perform Hadamard product of two matrices through block storage method.
    :param data1: Matrix 1
    :param data2: Matrix 2
    :param block_size: The size of the segmentation stored in block wise matrix multiplication.
        If the value is less than or equal to zero, no block operation will be performed.
    :param data: Return the placeholder variables of the result matrix.
        If there is value, it will reduce the consumption of memory space.
    :return: Hadamard product result
    """
    n, m = data1.shape
    n1, m1 = data2.shape

    if n != n1 or m != m1:
        log(__name__).error(f"Need to satisfy the multiplication principle of Hadamard products in matrices. ({(n, m)} != {n1, m1})")
        raise ValueError(f"Need to satisfy the multiplication principle of Hadamard products in matrices. ({(n, m)} != {n1, m1})")

    if block_size <= 0 or n <= block_size and m <= block_size:
        return np.multiply(data1, data2)

    n_range = range(0, n, block_size)
    m_range = range(0, m, block_size)

    _cache_path_ = os.path.join(ul.project_cache_path, generate_str(50))
    file_method(__name__).makedirs(_cache_path_)

    # Store block data
    log(__name__).info("[matrix_multiply_block_storage]: Store block data...")
    total_steps = len(n_range) * len(m_range)
    with tqdm(total=total_steps) as pbar:
        for i in n_range:
            for k in m_range:
                i_max = min(i + block_size, n)
                k_max = min(k + block_size, m)

                _matrix_ = np.multiply(data1[i:i_max, k:k_max], data2[i:i_max, k:k_max])

                with open(os.path.join(_cache_path_, str(i) + str(k) + ".pkl"), 'wb') as f:
                    pickle.dump(_matrix_, f)

                del _matrix_
                pbar.update(1)

    del data1, data2

    if data is None or data.shape != (n, m):
        data = np.zeros((n, m))

    # Read data
    log(__name__).info("[matrix_multiply_block_storage]: Read block data...")
    with tqdm(total=total_steps) as pbar:
        for i in n_range:
            for k in m_range:
                i_max = min(i + block_size, n)
                k_max = min(k + block_size, m)

                with open(os.path.join(_cache_path_, str(i) + str(k) + ".pkl"), 'rb') as f:
                    _matrix_ = pickle.load(f)
                    data[i:i_max, k:k_max] += _matrix_
                    del _matrix_

                pbar.update(1)

    shutil.rmtree(_cache_path_)

    return data


def vector_multiply_block_storage(
    data1: collection,
    data2: collection,
    block_size: int = 10000,
    data: matrix_data = None
) -> matrix_data:
    """
    Two vectors are broadcast in rows and columns respectively and multiplied by Hadamard product
    :param data1: Vector 1
    :param data2: Vector 2
    :param block_size: The size of the segmentation stored in block wise matrix multiplication.
        If the value is less than or equal to zero, no block operation will be performed.
    :param data: Return the placeholder variables of the result matrix.
        If there is value, it will reduce the consumption of memory space.
    :return: Matrix
    """

    vector1 = to_dense(data1, is_array=True).flatten()[:, np.newaxis]
    vector2 = to_dense(data2, is_array=True).flatten()

    del data1, data2

    n, _ = vector1.shape
    q = vector2.shape[0]

    if block_size <= 0 or n <= block_size and q <= block_size:
        return vector1 * vector2

    n_range = range(0, n, block_size)
    q_range = range(0, q, block_size)

    _cache_path_ = os.path.join(ul.project_cache_path, generate_str(50))
    file_method(__name__).makedirs(_cache_path_)

    # Store block data
    log(__name__).info("[vector_multiply_block_storage]: Store block data...")

    total_steps = len(n_range) * len(q_range)
    with tqdm(total=total_steps) as pbar:
        for i in n_range:
            for j in q_range:
                i_max = min(i + block_size, n)
                j_max = min(j + block_size, q)

                _matrix_ = vector1[i:i_max, :] * vector2[j:j_max]

                with open(os.path.join(_cache_path_, str(i) + str(j) + ".pkl"), 'wb') as f:
                    pickle.dump(_matrix_, f)

                del _matrix_
                pbar.update(1)

    del vector1, vector2

    if data is None or data.shape != (n, q):
        data = np.zeros((n, q))

    # Read data
    log(__name__).info("[vector_multiply_block_storage]: Read block data...")
    with tqdm(total=total_steps) as pbar:
        for i in n_range:
            for j in q_range:
                i_max = min(i + block_size, n)
                j_max = min(j + block_size, q)

                with open(os.path.join(_cache_path_, str(i) + str(j) + ".pkl"), 'rb') as f:
                    _matrix_ = pickle.load(f)
                    data[i:i_max, j:j_max] += _matrix_
                    del _matrix_

                pbar.update(1)

    shutil.rmtree(_cache_path_)

    return data


def matrix_division_block_storage(
    matrix: matrix_data,
    value: Union[float, int, collection, matrix_data],
    block_size: int = 10000,
    data: matrix_data = None
) -> matrix_data:
    """
    Dividing a matrix by another value, vector, or matrix.
    :param matrix: Matrix
    :param value: Value, vector, or matrix
    :param block_size: The size of the segmentation stored in block wise matrix multiplication.
        If the value is less than or equal to zero, no block operation will be performed.
    :param data: Return the placeholder variables of the result matrix.
        If there is value, it will reduce the consumption of memory space.
    :return: Matrix
    """

    n, m = matrix.shape

    is_status: int = -1

    if isinstance(value, collection):
        value = to_dense(value, is_array=True)
        q = value.shape[0]

        if q != n and q != m:
            log(__name__).error(f"Inconsistent dimensions cannot be divided. {(n, m)} != {q}")
            raise ValueError(f"Inconsistent dimensions cannot be divided. {(n, m)} != {q}")

        is_status = 1 if n == q else 0
    elif isinstance(value, matrix_data):
        is_status = 2

    if block_size <= 0 or n <= block_size and m <= block_size:
        return matrix / value

    n_range = range(0, n, block_size)
    m_range = range(0, m, block_size)

    _cache_path_ = os.path.join(ul.project_cache_path, generate_str(50))
    file_method(__name__).makedirs(_cache_path_)

    # Store block data
    log(__name__).info("[matrix_division_block_storage]: Store block data...")
    total_steps = len(n_range) * len(m_range)
    with tqdm(total=total_steps) as pbar:
        for i in n_range:
            for k in m_range:
                i_max = min(i + block_size, n)
                k_max = min(k + block_size, m)

                if is_status == -1:
                    _matrix_ = matrix[i:i_max, k:k_max] / value
                elif is_status == 0:
                    _matrix_ = matrix[i:i_max, k:k_max] / value[k:k_max]
                elif is_status == 1:
                    _matrix_ = matrix[i:i_max, k:k_max] / value[i:i_max]
                elif is_status == 2:
                    _matrix_ = matrix[i:i_max, k:k_max] / value[i:i_max, k:k_max]
                else:
                    raise RuntimeError("nothingness")

                with open(os.path.join(_cache_path_, str(i) + str(k) + ".pkl"), 'wb') as f:
                    pickle.dump(_matrix_, f)

                del _matrix_
                pbar.update(1)

    del matrix, value

    if data is None or data.shape != (n, m):
        data = np.zeros((n, m))

    # Read data
    log(__name__).info("[matrix_division_block_storage]: Read block data...")
    with tqdm(total=total_steps) as pbar:
        for i in n_range:
            for k in m_range:
                i_max = min(i + block_size, n)
                k_max = min(k + block_size, m)

                with open(os.path.join(_cache_path_, str(i) + str(k) + ".pkl"), 'rb') as f:
                    _matrix_ = pickle.load(f)
                    data[i:i_max, k:k_max] += _matrix_
                    del _matrix_

                pbar.update(1)

    shutil.rmtree(_cache_path_)

    return data


def matrix_callback_block_storage(
    matrix: matrix_data,
    callback,
    block_size: int = 10000,
    data: matrix_data = None
) -> matrix_data:
    """
    Dividing a matrix by another value, vector, or matrix.
    :param matrix: Matrix
    :param callback: callback function
    :param block_size: The size of the segmentation stored in block wise matrix multiplication.
        If the value is less than or equal to zero, no block operation will be performed.
    :param data: Return the placeholder variables of the result matrix.
        If there is value, it will reduce the consumption of memory space.
    :return: Matrix
    """

    n, m = matrix.shape

    n_range = range(0, n, block_size)
    m_range = range(0, m, block_size)

    if block_size <= 0 or n <= block_size and m <= block_size:
        return callback(matrix)

    _cache_path_ = os.path.join(ul.project_cache_path, generate_str(50))
    file_method(__name__).makedirs(_cache_path_)

    # Store block data
    log(__name__).info("[matrix_callback_block_storage]: Store block data...")
    total_steps = len(n_range) * len(m_range)
    with tqdm(total=total_steps) as pbar:
        for i in n_range:
            for k in m_range:
                i_max = min(i + block_size, n)
                k_max = min(k + block_size, m)

                _matrix_ = callback(matrix[i:i_max, k:k_max])

                with open(os.path.join(_cache_path_, str(i) + str(k) + ".pkl"), 'wb') as f:
                    pickle.dump(_matrix_, f)

                del _matrix_
                pbar.update(1)

    del matrix

    if data is None or data.shape != (n, m):
        data = np.zeros((n, m))

    # Read data
    log(__name__).info("[matrix_callback_block_storage]: Read block data...")
    with tqdm(total=total_steps) as pbar:
        for i in n_range:
            for k in m_range:
                i_max = min(i + block_size, n)
                k_max = min(k + block_size, m)

                with open(os.path.join(_cache_path_, str(i) + str(k) + ".pkl"), 'rb') as f:
                    _matrix_ = pickle.load(f)
                    data[i:i_max, k:k_max] += _matrix_
                    del _matrix_

                pbar.update(1)

    shutil.rmtree(_cache_path_)

    return data


def generate_str(length: int = 10) -> str:
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def set_inf_value(matrix: matrix_data) -> None:
    # solve -Inf/Inf value
    matrix_inf = np.logical_and(np.isinf(matrix), matrix > 0)
    matrix__inf = np.logical_and(np.isinf(matrix), matrix < 0)

    # set inf
    if np.any(matrix_inf):
        matrix[matrix_inf] = np.max(matrix[~matrix_inf]) * 2

    # set -inf
    if np.any(matrix__inf):
        matrix[matrix__inf] = np.min(matrix[~matrix__inf]) / 2


def check_adata_get(adata: AnnData, layer: str = None, is_dense: bool = True, is_matrix: bool = False) -> AnnData:
    # judge input data
    if adata.shape[0] == 0:
        log(__name__).warning("Input data is empty")
        raise ValueError("Input data is empty")

    # get data
    data: AnnData = adata.copy()

    # judge layers
    if layer is not None:
        if layer not in list(data.layers):
            log(__name__).error("The `layer` parameter needs to include in `adata.layers`")
            raise ValueError("The `layer` parameter needs to include in `adata.layers`")

        data.X = to_dense(data.layers[layer], is_array=True) if is_dense else to_sparse(
            data.layers[layer], is_matrix=is_matrix
        )
    else:
        data.X = to_dense(data.X, is_array=True) if is_dense else to_sparse(data.X, is_matrix=is_matrix)

    return data


def add_cluster_info(data: DataFrame, data_ref: DataFrame, cluster: str) -> DataFrame:

    new_data: DataFrame = data.copy()
    if data_ref is not None and cluster not in new_data.columns:

        new_data: DataFrame = pd.merge(new_data, data_ref, how="left", left_index=True, right_index=True)

        if "barcode_x" in new_data.columns:
            new_data["barcode"] = new_data["barcode_x"]
            new_data.drop("barcode_x", axis=1, inplace=True)

            if "barcode_y" in new_data.columns:
                new_data.drop("barcode_y", axis=1, inplace=True)

        if "barcodes_x" in new_data.columns:
            new_data["barcodes"] = new_data["barcodes_x"]
            new_data.drop("barcodes_x", axis=1, inplace=True)

            if "barcodes_y" in new_data.columns:
                new_data.drop("barcodes_y", axis=1, inplace=True)

    if cluster not in new_data.columns:
        log(__name__).error(f"`{cluster}` is not in `adata.obs.columns`.")
        raise ValueError(f"`{cluster}` is not in `columns` ({new_data.columns}).")

    return new_data
