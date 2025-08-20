"""Module with criteria to check the validity of the data
and the factor analysis model."""

import matplotlib.pyplot as plt
import numpy as np
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity, calculate_kmo
from sklearn.decomposition import FactorAnalysis
from sklearn.linear_model import LinearRegression

from . import layerfa


def check_data_validity(data: np.ndarray, verbose: bool = True) -> tuple:
    """Apply to check if it is valid to apply layer factor analysis to a given dataset by computing Bartletts and KMO tests.

    Parameters
    ----------
    data : array-like of shape (n_samples, n_features)
        Data (observed variables).

    verbose : bool, default=True
        Whether you want to print the results.

    Returns
    -------
    chi_square_value : float
        Chi square value of the Bartletts test.

    p_value : float
        p value of the Bartletts test.

    kmo_model : float
        Result of the KMO test.
    """
    chi_square_value, p_value = bartletts_test(data)
    kmo_model = kmo_test(data)

    if verbose:
        print(f"Bartlett : chi = {chi_square_value}, p-value = {p_value}")
        print(f"KMO : {kmo_model}")

    return chi_square_value, p_value, kmo_model


def check_fa_fit(
    data: np.ndarray,
    WT: np.ndarray,
    latent_factors: np.ndarray,
    lfa: FactorAnalysis,
    ord: int | None = None,
    verbose: bool = True,
) -> tuple:
    """Apply to check whether the layer factor analysis model is well fitted.

    Prints the factor residuals, D1 and D>, the fitting residuals, Res norm and the max and min values, and the 20th percentil of the correlation coefficient.

    Parameters
    ----------
    data : array-like of shape (n_samples, n_features)
        Data (observed variables).

    WT : array-like of shape (n_components, n_features)
        Transpose factor loading matrix.

    latent_factors : array-like of shape (n_samples, n_components)
        Laten factors.

    lfa : Factor Analysis
        Fitted layer factor analysis model.

    ord : int, optional, default=None
        Norm used in residual calculation, defaults as l2/Frobenius. ord=1 is max(sum(abs(x), 0)), same as ord=np.inf since x is symmetric.

    verbose : bool, default=True
        Whether you want to print the results.

    Returns
    -------
    u : array-like of shape (n_samples, n_features)
        Noise (non-observable perturbations).

    convu : array-like of shape (n_features, n_features)
        Noise covariance matrix.

    communalities : 1D array of shape n_features
        Sum of the effect of the latent factors on the data (sum of the squared rows of the factor loading matrix).

    residuals : array-like of shape (n_features, n_features)
        Model residuals.

    corr_coef : 1D array of shape n_features
        Squared correlation coefficient.
    """
    u, covu, d1, dg = layerfa.get_factor_residuals_cov(data, WT, latent_factors)
    communalities = layerfa.get_communalities(WT)
    residuals, res_norm = layerfa.get_model_residuals(data, lfa, ord)
    corr_coef = layerfa.get_correlation_coef(WT, data)

    if verbose:
        print("D1 = ", d1)
        print("D> = ", dg)
        print(
            f"Res = {res_norm}, with residuals in (max, min) = ({np.max(residuals)}, {np.min(residuals)})"
        )
        print(
            "20th percentil of correlation coefficinet = ", np.percentile(corr_coef, 20)
        )

    return u, covu, communalities, residuals, corr_coef


def eigenvalues_criterion(data: np.ndarray, plotting: bool = False) -> tuple:
    """Apply to obtain the number of latent factors through the Kaiser criterion, which consists on retaining as many factors as eigenvalues are greater than 1.

    Parameters
    ----------
    data : array-like of shape (n_samples, n_features)
        Data (observed variables).

    plotting : bool, default=True
        Whether to display eigenvalue plot.

    Returns
    -------
    orig_eigenvalues : 1D array
        Eigenvalues of the data correlation matrix.

    n_factors : int
        Number of latent factors according to eigenvalue criterion.
    """
    data_normz = (data - np.mean(data, axis=0)) / np.std(data, axis=0)  # ddof = 0
    corr_mtx = np.cov(data_normz, rowvar=False)  # ddof = 0
    orig_eigenvalues, _ = np.linalg.eigh(corr_mtx)
    orig_eigenvalues = orig_eigenvalues[::-1]

    x = orig_eigenvalues[orig_eigenvalues >= 1]
    if plotting:
        _plot_eigenvalues(orig_eigenvalues, data)

    # Stablish the desired number of factors
    n_factors = x.size

    return orig_eigenvalues, n_factors


def _plot_eigenvalues(orig_eigenvalues: np.ndarray, data: np.ndarray):
    """Scree plot plots the eigenvalues.

    Following this criterion, retain as many factors as eigenvalues are before the inflection point.

    Parameters
    ----------
    orig_eigenvalues : 1D array-like of shape n_features
        Eigenvalues.

    data : array-like of shape (n_samples, n_features)
        Data (observed variables).
    """
    plt.scatter(range(1, data.shape[1] + 1), orig_eigenvalues)
    plt.plot(range(1, data.shape[1] + 1), orig_eigenvalues)
    plt.title("Scree Plot")
    plt.xlabel("Factors")
    plt.ylabel("Eigenvalue")
    plt.grid()
    plt.show()


def variance_nfactors_criterion(data: np.ndarray, m: float) -> int:
    """Apply to obtain the number of latent factors through the Variance criterion, which consists on retaining enough factors to account for m% of the variation.

    Parameters
    ----------
    data : array-like of shape (n_samples, n_features)
        Data (observed variables).

    m : float
        Percentage of retained variance.

    Returns
    -------
    i : int
        Number of latent factors according to eigenvalue criterion.
    """
    cov_mtx = np.cov(data, rowvar=False)
    eig, _ = np.linalg.eigh(cov_mtx)
    eig = eig[::-1]
    tot_var = np.sum(eig)
    i = 0
    frac = eig[i] / tot_var
    while frac < m:
        i = i + 1
        frac = frac + eig[i] / tot_var
    if i == 0:
        i = 1

    return i


def standard_error_scree_criterion(data: np.ndarray) -> int:
    """Standard Error Scree based on nSeScree.r

    Zoski, K. and Jurs, S. (1996). An objective counterpart to the visual scree test for factor analysis: the standard error scree. Educational and Psychological Measurement, 56}(3), 443-451.

    Parameters
    ----------
    data : array-like of shape (n_samples, n_features)
        Data (observed variables).

    Returns
    -------
    i : int
        Number of latent factors according to standard error scree criterion.
    """
    cov_mtx = np.cov(data, rowvar=False)
    eig, _ = np.linalg.eigh(cov_mtx)  # decreasing order
    eig = sorted(eig, reverse=True)
    n = len(eig)
    criteria = 1 / n
    i = 0
    while i < n - 2:
        x = np.arange(i, n).reshape(-1, 1)
        y = eig[i:n]
        reg = LinearRegression().fit(x, y)
        R2 = reg.score(x, y)
        scree = np.sqrt((1 - R2) * ((len(y) - 1) / (len(y) - 2))) * np.std(y, ddof=1)
        if scree < criteria:
            break
        else:
            i = i + 1
    if i == 0:
        i = 1
    return i


def bartletts_test(data: np.ndarray) -> tuple:
    """Apply Bartletts sphericity test using factor_analyzer.

    It is used to test the null hypothesis that the correlation matrix of the observed variables is the identity. If this were so, it would imply that the variables are not correlated and, therefore, it would not be appropriate to assume a factorial model. We seek for a p-value < 0.05.

    Parameters
    ----------
    data : array-like of shape (n_samples, n_features)
        Data (observed variables).

    Returns
    -------
    chi_square_value : float
        Chi square value.

    p_value : float
        p-value of the test.
    """
    chi_square_value, p_value = calculate_bartlett_sphericity(data)
    return chi_square_value, p_value


def kmo_test(data: np.ndarray) -> float:
    """Apply Kaiser-Meyer-Olkin (KMO) test using factor_analyzer.

    It indicates the degree of overlapping information of the variables by calculating the determinant of the correlation matrix, and examines the partial correlation between variables (multicollinearity or singularity). We seek for a KMO value close to 1 (at least 0.6).

    Parameters
    ----------
    data : array-like of shape (n_samples, n_features)
        Data (observed variables).

    Returns
    -------
    kmo_model : float
        The overall KMO score.
    """
    _, kmo_model = calculate_kmo(data)
    return kmo_model
