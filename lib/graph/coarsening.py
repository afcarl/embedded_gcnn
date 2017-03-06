from __future__ import division

from six.moves import xrange

import numpy as np
import scipy.sparse as sp


def coarsen_adj(adj, level=1, rid=None):
    if rid is None:
        rid = np.random.permutation(np.arange(adj.shape[0]))

    degree = np.array(adj.sum(axis=1)).flatten()

    # Sort by row index.
    rows, cols, vals = sp.find(adj)
    perm = np.argsort(rows)
    rows = rows[perm]
    cols = cols[perm]
    vals = np.array(vals[perm], np.float32)

    # Local normalized cut.
    for i in xrange(vals.shape[0]):
        vals[i] = vals[i] * (1 / degree[rows[i]] + 1 / degree[cols[i]])

    # Get the beginning indices and the count of a new row of rows
    _, rowstart, rowlength = np.unique(
        rows, return_index=True, return_counts=True)

    clusters = np.zeros_like(rowstart, np.int32) - 1
    for i in xrange(rowstart.shape[0]):
        tid = rid[i]  # iterate randomly

        if clusters[tid] >= 0:  # already marked
            continue

        start = rowstart[tid]
        end = start + rowlength[tid]
        sliced_vals = vals[start:end]

        # Randomly sort values of the looked up row.
        perm = np.random.permutation(np.arange(sliced_vals.shape[0]))
        sliced_vals = sliced_vals[perm]
        j = np.argmax(sliced_vals)

        if sliced_vals[j] > 0:
            # Get neighbor index.
            sliced_cols = cols[start:end]
            sliced_cols = sliced_cols[perm]
            neighbor = sliced_cols[j]

            # Set cluster.
            clusters[tid] = neighbor
            clusters[neighbor] = tid

            # Set edge weights to zero if the contain one of the nodes.
            vals[np.where(np.logical_or(cols == tid, cols == neighbor))] = 0
        else:
            # No unmarked neighbor found.
            clusters[tid] = tid

    return clusters
