from collections import namedtuple

import torch
from torch import Tensor

LSDDModel = namedtuple(
    "LSDDModel", ("negative_half_precision", "regularization", "centers", "coeffs")
)


def lsdd_fit(
    x: Tensor,
    y: Tensor,
    sigma: None | float | Tensor = None,
    lambd: None | float | Tensor = None,
    cv_folds: int = 5,
    kernel_num: int = 300,
    seed: int | None = None,
) -> LSDDModel:
    r"""Fits a Least-Squares Density Difference (LSDD) estimation model to
    the given data `x` and `y`. The model estimates the difference

    .. math::
        d(x) = p(x) - q(x)

    where `p` and `q` are the densities of samples `x` and `y`, respectively.

    Parameters
    ----------
    x : Tensor
        Samples from `p(x)`, shape `(n_samples_x, n_features)`.
    y : Tensor
        Samples from `q(x)`, shape `(n_samples_y, n_features)`.
    sigma : float or Tensor, optional
        The bandwidth of the Gaussian kernel used for the density estimation. If `None`,
        a range of values will be automatically selected and the optimal value selected
        by k-fold cross-validation. The same if a tensor of values is provided. If a
        single float value is provided, it will be used as the bandwidth, without
        cross-validation. By default, `None`.
    lambd : float or Tensor, optional
        The regularization parameter used for the density estimation. If `None`, a range
        of values will be automatically selected and the optimal value selected by
        k-fold cross-validation. The same if a tensor of values is provided. If a single
        float value is provided, it will be used as the regularization, without
        cross-validation. By default, `None`.
    cv_folds : int, optional
        The number of cross-validation folds to use for selecting the optimal `sigma`
        and `lambd` parameters. By default, `5`.
    kernel_num : int, optional
        The number of kernel centers to use for the difference estimation. If the
        combined number of samples in `x` and `y` is less than `kernel_num`, this will
        be set to `n_samples_x` + `n_samples_y`. By default, `300`.
    seed : int, optional
        The random seed for selecting the kernel centers. If `None`, a random seed will
        be generated. By default, `None`.

    Returns
    -------
    LSDDModel
        A named tuple containing the fitted model parameters:
          - `negative_half_precision`: optimal negative half precision of the kernel
          - `regularization`: optimal regularization parameter
          - `centers`: kernel centers
          - `coeffs`: coefficients for the linear combination of kernels

    Raises
    ------
    ValueError
        If `x` or `y` is not a 2-dimensional tensor, or if the number of features in
        `x` and `y` do not match.
    """
    if x.ndim != 2 or y.ndim != 2:
        raise ValueError("x and y must be 2-dimensional arrays.")
    if (features := x.shape[1]) != y.shape[1]:
        raise ValueError("x and y must have the same number of column features.")

    device = x.device
    dtype = x.dtype
    nx = x.shape[0]
    ny = y.shape[0]

    z = torch.cat((x, y), dim=0)
    nz = nx + ny
    kernel_num = min(kernel_num, nz)

    if seed is not None:
        generator = torch.Generator()
        generator.manual_seed(seed)
    else:
        generator = None
    idx = torch.randperm(nz, generator=generator, device=device)[:kernel_num]
    centers = z[idx]
    dist_x_centers = torch.cdist(x, centers).square()
    dist_y_centers = torch.cdist(y, centers).square()
    dist_centers_centers = torch.cdist(centers, centers).square()
    pi_to_half_feat = torch.pi ** (features / 2)

    if sigma is None:
        sigma = torch.linspace(0.25, 5, 14, device=device, dtype=dtype)
    elif isinstance(sigma, (float, int)):
        sigma = torch.scalar_tensor(sigma, device=device, dtype=dtype)
    else:
        sigma = torch.as_tensor(sigma, device=device, dtype=dtype)
    if lambd is None:
        lambd = torch.logspace(-4, 9, 14, device=device, dtype=dtype)
    elif isinstance(sigma, (float, int)):
        lambd = torch.scalar_tensor(lambd, device=device, dtype=dtype)
    else:
        lambd = torch.as_tensor(lambd, device=device, dtype=dtype)
    if sigma.shape[0] > 1 or lambd.shape[0] > 1:
        sigma, lambd = _sigma_lambd_cv(
            nx,
            ny,
            features,
            kernel_num,
            dist_x_centers,
            dist_y_centers,
            dist_centers_centers,
            cv_folds,
            sigma,
            lambd,
            pi_to_half_feat,
            device,
            dtype,
            generator,
        )

    neg_half_prec = -0.5 * sigma.square().reciprocal()
    H = (
        pi_to_half_feat
        * sigma.pow(features)
        * (0.5 * neg_half_prec * dist_centers_centers).exp()
    )
    H.diagonal().add_(lambd)
    phi_x = (neg_half_prec * dist_x_centers).exp()
    phi_y = (neg_half_prec * dist_y_centers).exp()
    h = phi_x.mean(0) - phi_y.mean(0)
    coeffs = torch.linalg.solve(H, h)

    return LSDDModel(neg_half_prec, lambd, centers, coeffs)


def lsdd_predict(mdl: LSDDModel, x: Tensor) -> Tensor:
    """Predicts the density difference for the given input `x` using the LSDD fitted
    model.

    Parameters
    ----------
    mdl : LSDDModel
        The fitted LSDD model (see `lsdd_fit`).
    x : Tensor
        The input data for which to predict the density difference. Must be a 2D tensor
        of shape `(n_samples, n_features)`, where `n_features` matches the number of
        features used during the model fitting.

    Returns
    -------
    Tensor
        The predicted density difference for each row in `x`. The shape is
        `(n_samples,)`.

    Raises
    ------
    ValueError
        If `x` is not a 2-dimensional tensor or if the number of features in `x` does
        not match the number of features used during the model fitting.
    """
    if x.ndim != 2:
        raise ValueError("x must be a 2-dimensional array.")
    centers = mdl.centers
    if x.shape[1] != centers.shape[1]:
        raise ValueError("x has an incorrect number of features.")
    phi_x = (mdl.negative_half_precision * torch.cdist(x, centers).square()).exp()
    return phi_x @ mdl.coeffs


def _sigma_lambd_cv(
    nx: int,
    ny: int,
    features: int,
    kernel_num: int,
    dist_x_centers: Tensor,
    dist_y_centers: Tensor,
    dist_centers_centers: Tensor,
    folds: int,
    sigmas: Tensor,
    lambds: Tensor,
    pi_to_half_feat: float,
    device: torch.device,
    dtype: torch.dtype,
    generator: torch.Generator | None,
) -> tuple[Tensor, Tensor]:
    """Computes the optimal sigma and lambda parameters for LSDD using k-fold
    cross-validation."""

    # NOTE: the shape paradigm is `n_sigma x n_lambds x n_folds x ...`
    n_sigmas = sigmas.numel()
    n_lambds = lambds.numel()

    splits = torch.arange(max(nx, ny), device=device) * folds
    splits_x = (splits[:nx] / nx).long()
    n_cv_x = torch.bincount(splits_x, minlength=folds)
    idx_x = splits_x[torch.randperm(nx, generator=generator, device=device)]
    splits_y = (splits[:ny] / ny).long()
    n_cv_y = torch.bincount(splits_x, minlength=folds)
    idx_y = splits_y[torch.randperm(nx, generator=generator, device=device)]

    sigmas_ = sigmas[:, None, None]
    neg_half_precs = -0.5 * sigmas_.square().reciprocal()
    H = (
        pi_to_half_feat
        * sigmas_.pow(features)
        * (0.5 * neg_half_precs * dist_centers_centers).exp()
    )

    phi_x = (neg_half_precs * dist_x_centers).exp()
    h_cv_x = torch.zeros((n_sigmas, folds, kernel_num), device=device, dtype=dtype)
    idx_x_expanded = idx_x[None, :, None].expand(n_sigmas, -1, kernel_num)
    h_cv_x.scatter_add_(1, idx_x_expanded, phi_x)

    phi_y = (neg_half_precs * dist_y_centers).exp()
    h_cv_y = torch.zeros_like(h_cv_x)
    idx_y_expanded = idx_y[None, :, None].expand(n_sigmas, -1, kernel_num)
    h_cv_y.scatter_add_(1, idx_y_expanded, phi_y)

    # calculate h vectors for training and test
    sum_x = h_cv_x.sum(1, keepdim=True)
    n_cv_x_exp = n_cv_x.view(1, -1, 1)
    sum_y = h_cv_y.sum(1, keepdim=True)
    n_cv_y_exp = n_cv_y.view(1, -1, 1)
    htr = (sum_x - h_cv_x) / (n_cv_x.sum() - n_cv_x_exp) - (sum_y - h_cv_y) / (
        n_cv_y.sum() - n_cv_y_exp
    )
    hte = h_cv_x / n_cv_x_exp - h_cv_y / n_cv_y_exp

    # add missing dims
    H = H.view(n_sigmas, 1, 1, kernel_num, kernel_num)
    htr = htr.view(n_sigmas, 1, folds, kernel_num, 1)
    hte = hte.view(n_sigmas, 1, folds, kernel_num)

    # calcuate coefficients and score for each lambda-sigma-fold combination
    B = H.repeat(1, n_lambds, 1, 1, 1)  # cannot `.expand` here
    B.diagonal(dim1=3, dim2=4).add_(lambds.view(1, n_lambds, 1, 1))
    coeffs = torch.linalg.solve(B, htr)
    coeffs_squeezed = coeffs.squeeze(-1)
    cHc = torch.linalg.vecdot(H.matmul(coeffs).squeeze(-1), coeffs_squeezed)
    chte = torch.linalg.vecdot(coeffs_squeezed, hte)
    scores = (cHc - 2 * chte).sum(2)

    min_idx = scores.argmin().item()
    min_row = min_idx // n_lambds
    min_col = min_idx % n_lambds

    return sigmas[min_row], lambds[min_col]
