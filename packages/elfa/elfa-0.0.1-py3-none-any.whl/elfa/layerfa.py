"""Layer Factor Analysis module for convolutional layers.

It is based on the following Python package:

Scikit-learn FactorAnalysis
https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.FactorAnalysis.html

    Calculation of the factorial model by maximum likelihood estimation (direct method) using SVD, x = mu + Wh + e. Returns an object of class FactorAnalysis with all its attributes fitted with the observable variables:
    - faMatrix = fa.fit(matrix).
    - faMatrix.components_  is W^T.
    - faMatrix.loglike_ is log likelihood on each iteration.
    - faMatrix.noise_variance_ i psi.
    - dataMeanLoglike = fa.score(matrix).
    - dataLoglike = fa.score_samples(matrix).
    - latent_factors = fa.transform(matrix) are the latent factors obtained using the original samples or new ones and the linear predictor fi = (I + W^Tpsi^{-1}W)^{-1}W^Tpsi^{-1}xi.
    - faCovData = faMatrix.get_covariance() is the covariance matrix of the observable variables according to the factor analysis model, that is, cov = WW^T + psi.
"""

import numpy as np
from sklearn.decomposition import FactorAnalysis

from . import constants, plot_module


def lfa_output(
    data: np.ndarray,
    n_factors: int,
    hpx: int,
    wpx: int,
    svd_method: str = constants.SVD_METHOD,
    rotation_method: str = constants.ROTATION_METHOD,
    max_iter: str = constants.MAX_ITER,
    iterated_power: int = constants.ITERATED_POWER,
    noise_variance_init: np.ndarray = constants.NOISE_VARIANCE_INIT,
    num_image=(0, 1),
    plotting=False,
) -> tuple:
    """Fit factor analysis model for convolutional layers (layer factor analysis).

    Parameters
    ----------
    data : array-like of shape (n_samples, n_features)
        Data (observed variables).

    n_factors : int
        Number of latent factors to compute factor analysis.

    hpx : int
        Number of row pixels.

    wpx : int
        Number of column pixels.

    svd_method : {'lapack', 'randomized'}, default=constants.SVD_METHOD
        Which SVD method to use. For most applications 'randomized' will be sufficiently precise while providing significant speed gains.

    rotation_method : {'varimax', 'quartimax'}, default=constants.ROTATION_METHOD
        If not None, apply the indicated rotation.

    max_iter : int, default=constants.MAX_ITER
        Maximum number of iterations.

    iterated_power : int, default=constants.ITERATED_POWER
        Number of iterations for the power method. Only used if ``svd_method`` equals 'randomized'.

    noise_variance_init : array-like of shape (n_features,), default=constants.NOISE_VARIANCE_INIT
        The initial guess of the noise variance for each feature. If None, it defaults to np.ones(n_features).

    num_image : duple, default=(0,1)
        Range of images for which the latent factors will be plotted.

    plotting : bool, default=False
        Whether you want to display the loading matrix and the latent factors.

    Returns
    -------
    WT : array-like of shape (n_components, n_features)
        Transpose factor loading matrix.

    lfa : Factor Analysis
        Fitted layer factor analysis model.

    latent_factors : array-like of shape (n_samples, n_components)
        Latent factors obtained for the observable variables.
    """
    lfa = FactorAnalysis(
        n_components=n_factors,
        svd_method=svd_method,
        rotation=rotation_method,
        max_iter=max_iter,
        iterated_power=iterated_power,
        noise_variance_init=noise_variance_init,
    )

    lfa.fit(data)
    WT = lfa.components_
    latent_factors = lfa.transform(data)

    # Plots WT and num_image images of the batch. Only first by default
    if plotting:
        plot_module.plot_matrix(WT)
        hw = hpx * wpx
        numImages = range(num_image[0], num_image[1])
        for i in numImages:
            plot_module.plot_gallery(
                latent_factors[hw * i : hw * (i + 1), :],
                (hpx, wpx),
                n_col=constants.N_COL,
                n_row=constants.N_ROW,
            )

    return WT, lfa, latent_factors


def get_communalities(WT: np.ndarray) -> np.ndarray:
    """Compute communalities of the layer factor analysis model.

    Parameters
    -------
    WT : array-like of shape (n_components, n_features)
        Factor loading matrix.

    Returns
    -------
    communalities : 1D array of shape n_features
        Sum of the effect of the latent factors on the data corresponding to the variance of data explained by factors (sum of the squared rows of the factor loading matrix).
    """
    comunalities = (WT**2).sum(axis=0)  # h^2_j
    return comunalities


def get_factor_residuals_cov(
    data: np.ndarray, WT: np.ndarray, latent_factors: np.ndarray
) -> tuple:
    """Compute factor residuals u = x - Wf and their covariance matrix. If the covariance matrix of the noise is not diagonal, the number of latent factors need to be increased.

    Parameters
    -------
    data : array-like of shape (n_samples, n_features)
        Data (observed variables).

    WT : array-like of shape (n_components, n_features)
        Transpose factor loading matrix.

    latent_factors : array-like of shape (n_samples, n_components)
        Laten factors. Captures the correlation between observed variables.

    Returns :
    -------
    u : array-like of shape (n_samples, n_features)
        Noise (non-observable perturbations).

    convu : array-like of shape (n_features, n_features)
        Noise covariance matrix, whose diagonal elements are called uniqueness, which represents the independent noise variances for each of the variables.

    d1 : float
        Measure of how diagonal is covu. The closer to one, the better.
        d1 = ||diag(covu)||/||covu||

    dg : float
        Measure of how diagonal is covu. The greater, the better.
        dg = ||diag(covu)||/||covu - diag(covu)||
    """
    u = data - np.dot(latent_factors, WT)
    covu = np.cov(u, rowvar=False)

    # check diagonality
    covu_diag = np.diag(np.diagonal(covu))
    d1 = np.linalg.norm(covu_diag) / np.linalg.norm(covu)
    dg = np.linalg.norm(covu_diag) / np.linalg.norm(covu - covu_diag)

    return u, covu, d1, dg


def get_model_residuals(
    data: np.ndarray, lfa: FactorAnalysis, ord: int | None = None
) -> tuple:
    """Compute model residuals, which are defined as the difference between the covariance matrix of the original data and the covariance matrix according to the factor model. The norm of the difference is also computed. The smaller the better. Correlation matrices are used instead of covariance.

    Parameters
    -------
    data : array-like of shape (n_samples, n_features)
        Data (observed variables).

    lfa : Factor Analysis class
        Fitted layer factor analysis model.

    ord : int, optional, default=None
        Norm used in residual calculation, defaults as l2/Frobenius. ord=1 is max(sum(abs(x), 0)), same as ord=np.inf since x is symmetric.

    Returns
    -------
    residuals : array-like of shape (n_features, n_features)
        Factor residuals.

    res_norm : float
        Measure of the similarity of correlation matrices, with values between 0 and 1. The smaller the better
        res_norm = ||S-V||/||S||+||V||
    """
    V_correlation = _calc_corr_matrix(lfa.get_covariance())
    S_correlation = np.corrcoef(data, rowvar=False)
    residuals = S_correlation - V_correlation
    # Obtain a measure of how close they are with norm between 0 and 1
    sum_norms = np.linalg.norm(V_correlation, ord) + np.linalg.norm(S_correlation, ord)
    res_norm = np.linalg.norm(residuals, ord) / sum_norms

    return residuals, res_norm


def get_correlation_coef(WT: np.ndarray, data: np.ndarray) -> np.ndarray:
    """Compute the squared correlation coefficient, which is defined as the communality divided by the variance of the variable. With values between 0 and 1, for a well fitted model it has to be close to 1:
    gamma^2_j = h^2_j/s^2_j = 1 - psi^2_j/s^2_j

    Parameters
    -------
    WT : array-like of shape (n_components, n_features)
        Factor loading matrix.

    data : array-like of shape (n_samples, n_features)
        Data (observable variables).

    Returns
    -------
    corr_coef : 1D array of shape n_features
        Squared correlation coefficients.
    """
    communalities = get_communalities(WT)
    data_var = np.var(data, axis=0)
    corr_coef = np.divide(communalities, data_var)

    return corr_coef


def get_determination_coef(data: np.ndarray, lfa: FactorAnalysis) -> float:
    """Compute the determination coefficient of the system, which is defined using the determinant of Psi (the covariance of the noise) and the determinant of covariance matrix of the data according to the model:
    R^2 = 1 - (det(Psi)/det(V))^(1/n_features).

    Parameters
    -------
    lfa : Factor Analysis
        Fitted layer factor analysis model.

    data : array-like of shape (n_samples, n_features)
        Data (observable variables).

    Returns
    -------
    R2 : float
        Determination coefficient of the system.
    """
    data_cov = np.linalg.det(lfa.get_covariance())
    psi = np.linalg.det(np.diag(lfa.noise_variance_))
    m = data.shape[1]
    R2 = 1 - np.power(psi / data_cov, 1 / m)

    return R2


def get_factors_variance(WT: np.ndarray) -> tuple:
    """Compute the variance, proportional variance, and cumulative variance.

    Each element of the variance variable is the norm of the covariance between the data and the j-th latent factor. The greater it is, the more influence the j-th factor has over the data. Proportional variance is obtained by dividing by the number of features, whereas the cumulative variance is computed by adding the results one by one.

    Parameters
    -------
    WT : array-like of shape (n_component, n_features)
        Factor loading matrix.

    Returns
    -------
    variance : 1D array of shape n_component
        Variance.

    proportional_variance : 1D array of shape n_component
        Proportional variance.

    cumulative_variance : 1D array of shape n_component
        Cumulative sum of the proportional variance.
    """
    W = WT.transpose()
    n_rows = W.shape[0]

    # Compute variance
    W = W**2
    variance = np.sum(W, axis=0)

    # Compute proportional variance
    proportional_variance = variance / n_rows

    # Compute cumulative variance
    cumulative_variance = np.cumsum(proportional_variance, axis=0)

    return variance, proportional_variance, cumulative_variance


def get_totvar_explained(WT: np.ndarray, data: np.ndarray) -> float:
    """Compute the total variance explained by the factors.

    Parameters
    -------
    WT : array-like of shape (n_components, n_features)
        Factor loading matrix.

    data : array-like of shape (n_samples, n_features)
        Data (observable variables).

    Returns
    -------
    var_exp : float
        Total variance explained.
    """
    communalities = get_communalities(WT)
    data_totvar = np.sum(np.var(data, axis=0))

    return np.sum(communalities / data_totvar)


def _calc_corr_matrix(cov_matrix: np.ndarray) -> np.ndarray:
    """Compute the correlation matrix given a covariance matrix.

    Parameters
    -------
    cov_matrix : array-like of shape (rows, columns)
        Covariance matrix.

    Returns
    -------
    corr_matrix: array-like of shape (rows, columns)
        Correlation matrix.
    """
    rows, columns = cov_matrix.shape
    corr_matrix = np.zeros((rows, rows))
    for i in range(rows):
        for j in range(columns):
            sigma = np.sqrt(cov_matrix[i, i] * cov_matrix[j, j])
            corr_matrix[i, j] = cov_matrix[i, j] / sigma

    return corr_matrix
