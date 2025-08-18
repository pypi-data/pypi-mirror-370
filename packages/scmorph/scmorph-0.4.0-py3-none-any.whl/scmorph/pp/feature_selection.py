from types import SimpleNamespace
from typing import Any

import numpy as np
import pandas as pd
import scanpy as sc
from anndata import AnnData
from packaging.version import Version
from scipy.stats import kruskal, median_abs_deviation
from tqdm.auto import tqdm

from .correlation import corr

if Version(sc.__version__) >= Version("1.11.0"):
    from scanpy.pp import sample

    def subsample(adata: AnnData, n_obs: int | None = None, **kwargs: Any):
        """Wraps `scanpy.pp.sample` to allow subsampling"""
        return sample(adata, n=n_obs, **kwargs)
else:
    from scanpy.pp import subsample


def corr_features(adata: AnnData, method: str = "pearson", M: int = 5) -> AnnData:
    """
    Correlate features and save in `.varm` slot

    Parameters
    ----------
    adata
        The (annotated) data matrix of shape `n_obs` × `n_vars`.
        Rows correspond to cells and columns to genes.

    method
        One of "pearson", "spearman" and "chatterjee" ([:cite:p:`LinHan2023`]_)

    M
        Number of right nearest neighbors to use for Chatterjee correlation.

    Returns
    -------
    Feature correlations saved in `.varm` slot
    """
    adata.varm[method] = corr(adata.X, method=method, M=M)
    return adata.varm[method]


def _corr_wide_to_long(adata: AnnData, method: str) -> pd.DataFrame:
    x = adata.varm[method].copy()
    n_target = int(len(x) ** 2 / 2)
    xdf = pd.DataFrame(np.tril(x, -1), index=adata.var.index, columns=adata.var.index)
    return xdf.stack().iloc[:n_target]


def _corr_filter(adata: AnnData, method: str, cor_cutoff: float) -> list[str]:
    """Filter pairwise feature correlations, discard features with highest correlation to other features"""
    pairwise_corr = _corr_wide_to_long(adata, method)
    candidate_pairs = pairwise_corr.loc[pairwise_corr.abs() > cor_cutoff].index.to_frame()
    candidate_pairs.columns = ["feature_1", "feature_2"]
    candidate_singlets = np.unique(candidate_pairs.to_numpy().flatten())

    tot_corr = np.abs(adata[:, candidate_singlets].varm[method]).sum(axis=0)
    feat_corrs = pd.Series(tot_corr, index=adata.var.index)

    candidate_pairs["corr_1"] = feat_corrs.loc[candidate_pairs["feature_1"]].values
    candidate_pairs["corr_2"] = feat_corrs.loc[candidate_pairs["feature_2"]].values

    def pick_higher_cor(row: pd.Series) -> str:
        if row["corr_1"] < row["corr_2"]:
            return row["feature_1"]
        else:
            return row["feature_2"]

    exclude = list(set(candidate_pairs.apply(pick_higher_cor, axis=1)))
    return exclude


def select_features(
    adata: AnnData,
    method: str = "pearson",
    cor_cutoff: float = 0.9,
    fraction: float | None = None,
    n_obs: int | None = None,
    copy: bool = False,
) -> AnnData | None:
    """
    Feature selection based on correlation metrics.

    This can be useful for reducing the number of features in highly correlated profiling data.
    However, note that if using scmorph for hit calling, this may not be necesary,
    as ~scmorph.tl.get_ks` operates on PCA-space, which reduces the impact of feature correlation.
    Nevertheless, performing this step may improve downstream results and speed up computations.

    Select features by feature correlations. Allows measuring correlation
    on a subset of cells to speed up computations. See ``fraction`` and ``n_obs``
    for details.

    Parameters
    ----------
    adata
        The (annotated) data matrix of shape ``n_obs`` × ``n_vars``.
        Rows correspond to cells and columns to genes.

    method
        Which correlation coefficient to use for filtering.
        One of "pearson", "spearman" and "chatterjee" ([:cite:p:`LinHan2023`]_)

    cor_cutoff
        Cutoff beyond which features with a correlation coefficient
        higher than it are removed. Must be between 0 and 1.

    fraction
        Subsample to this ``fraction`` of the number of observations.

    n_obs
        Subsample to this number of observations.

    copy
        Whether to return a copy or modify ``adata`` inplace
        (i.e. operate inplace)

    Returns
    -------
    Feature correlations saved in ``.varm`` slot and feature selection saved in ``.var`` slot.
    """
    # sampling
    if fraction or n_obs:
        adata_ss = subsample(adata, fraction=fraction, n_obs=n_obs, copy=True)
    else:
        adata_ss = adata

    # variance filter
    pass_var = np.empty(len(adata.var), dtype=bool)

    for i, feat in enumerate(adata_ss.var_names):
        pass_var[i] = False if np.var(adata_ss[:, feat].X) < 1e-5 else True

    adata.var["qc_pass_var"] = pass_var
    adata_ss.var["qc_pass_var"] = pass_var

    # correlation filter
    corr_features(adata_ss, method=method, M=5)
    adata.varm[method] = adata_ss.varm[method]
    exclude = _corr_filter(adata_ss, method=method, cor_cutoff=cor_cutoff)
    keep = np.invert(adata.var.index.isin(exclude))

    if not copy:
        adata._inplace_subset_var(keep)
        return None
    else:
        return adata[:, keep].copy()


def kruskal_test(
    adata: AnnData,
    test_column: str = "PlateID",
    progress: bool = True,
) -> AnnData:
    """
    Perform Kruskal-Wallis H-test for each feature across batches.

    This can help identify features that are associated with confounders, such
    as batch and platemap effects. Note that while it does reduce feature space, its
    main purpose is to remove untrustworthy features associated with technical confounders.

    Parameters
    ----------
    adata
        Annotated data matrix.
    test_column
        The column name in `adata.obs` that contains the batch information.
    progress
        Whether to show a progress bar.

    Returns
    -------
    Kruskal-Wallis test results saved in `adata.uns["kruskal_test"]`.
    """
    confounder_X = adata.obs[test_column].astype(str).astype("category").values
    test_results = {}

    iterator = tqdm(adata.var.index) if progress else adata.var.index
    for selected_feature in iterator:
        feature_X = adata[:, selected_feature].X[:, 0]
        conf_indices_d = (
            pd.DataFrame({test_column: confounder_X, "feature": feature_X})
            .groupby(test_column, observed=True)
            .indices
        )
        feature_split_by_conf = [*[feature_X[conf_indices_d[conf]] for conf in conf_indices_d]]
        try:
            res = kruskal(*feature_split_by_conf)
        except ValueError:
            res = SimpleNamespace(statistic=np.nan, pvalue=np.nan)
        test_results[selected_feature] = res

    kruskal_df = pd.DataFrame(
        [
            (
                feature,
                test_results[feature].statistic,
                test_results[feature].pvalue,
            )
            for feature in test_results
        ],
        columns=["feature", "statistic", "pvalue"],
    )
    kruskal_df.metadata = SimpleNamespace(by=test_column, batch_feature=test_column)
    if "kruskal_test" not in adata.uns:
        adata.uns["kruskal_test"] = {}
    adata.uns["kruskal_test"][test_column] = kruskal_df
    return adata


def kruskal_filter(
    adata, test_column="PlateID", sigma=1, sigma_function="mad", copy=False
) -> AnnData | None:
    """
    Filter features based on Kruskal-Wallis H-test statistics.

    Parameters
    ----------
    adata
        Annotated data matrix.
    test_column
        The column name in `adata.obs` that contains the batch information.
    sigma
        The number of standard deviations to use for the threshold.
    sigma_function
        The function to use for calculating the standard deviation. Either "mad" or "std".
    copy
        Whether to return a copy or modify `adata` inplace

    Returns
    -------
    The filtered or annotated AnnData object.
    """

    def threshold_statistic(adata, test_column):
        df = adata.uns["kruskal_test"][test_column].dropna()
        x = df["statistic"].values
        med = np.median(x)
        if sigma_function == "mad":
            std = median_abs_deviation(x)
        else:
            std = np.std(x)
        thresh = med + sigma * std

        sn = adata.uns["kruskal_test"][test_column].metadata
        new = SimpleNamespace(threshold=thresh, median=med, std=std)

        adata.uns["kruskal_test"][test_column].metadata = SimpleNamespace(
            **{**sn.__dict__, **new.__dict__}
        )
        return adata

    def filter_threshold_statistic(adata, test_column):
        df = adata.uns["kruskal_test"][test_column]
        thresh = df.metadata.threshold
        return df.loc[df["statistic"] < thresh, "feature"]

    adata = threshold_statistic(adata, test_column)

    keep = filter_threshold_statistic(adata, test_column)

    if not copy:
        adata._inplace_subset_var(keep)
        return None
    return adata[:, keep].copy()
