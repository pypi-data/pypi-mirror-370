from collections import namedtuple

import torch
from torch import Tensor

RuLSIFModel = namedtuple(
    "RuLSIFModel", ("negative_half_precision", "regularization", "centers", "coeffs")
)


def rulsif_fit(
    x: Tensor,
    y: Tensor,
    alpha: float = 0.0,
    sigma: None | float | Tensor = None,
    lambd: None | float | Tensor = None,
    kernel_num: int = 100,
    seed: int | None = None,
) -> RuLSIFModel:
    r"""Fits a Relative Unconstrained Least-Squares Importance Fitting (RuLSIF) model to
    the given data `x` and `y`. The model estimates relative ratio

    .. math::
        r(x) = \frac{p(x)}{\alpha p(x) + (1 - \alpha) q(x)}

    where `p` and `q` are the densities of samples `x` and `y`, respectively.

    Parameters
    ----------
    x : Tensor
        Samples from `p(x)`, shape `(n_samples_x, n_features)`.
    y : Tensor
        Samples from `q(x)`, shape `(n_samples_y, n_features)`.
    alpha : float, optional
        The relative weights in the ratio denominator, by default `0.0`.
    sigma : float or Tensor, optional
        The bandwidth of the Gaussian kernel used for the density estimation. If `None`,
        a range of values will be automatically selected and the optimal value selected
        by leave-one-out cross-validation. The same if a tensor of values is provided.
        If a single float value is provided, it will be used as the bandwidth, without
        cross-validation. By default, `None`.
    lambd : float or Tensor, optional
        The regularization parameter used for the density estimation. If `None`, a range
        of values will be automatically selected and the optimal value selected by
        leave-one-out cross-validation. The same if a tensor of values is provided. If a
        single float value is provided, it will be used as the regularization, without
        cross-validation. By default, `None`.
    kernel_num : int, optional
        The number of kernel centers to use for the ratio estimation. If the number of
        samples in `x` is less than `kernel_num`, this will be set to `n_samples_x`. By
        default, `100`.
    seed : int, optional
        The random seed for selecting the kernel centers. If `None`, a random seed will
        be generated. By default, `None`.

    Returns
    -------
    RuLSIFModel
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
    if x.shape[1] != y.shape[1]:
        raise ValueError("x and y must have the same number of column features.")

    device = x.device
    dtype = x.dtype
    nx = x.shape[0]
    ny = y.shape[0]
    kernel_num = min(kernel_num, nx)

    if seed is not None:
        generator = torch.Generator()
        generator.manual_seed(seed)
    else:
        generator = None
    idx = torch.randperm(nx, generator=generator, device=device)[:kernel_num]
    centers = x[idx]
    dist_x_centers = torch.cdist(x, centers).square()
    dist_y_centers = torch.cdist(y, centers).square()

    if sigma is None:
        sigma = torch.logspace(-4, 9, 14, device=device, dtype=dtype)
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
            nx, ny, dist_x_centers, dist_y_centers, alpha, sigma, lambd
        )

    neg_half_prec = -0.5 * sigma.square().reciprocal()
    phi_x = (neg_half_prec * dist_x_centers).exp()
    phi_y = (neg_half_prec * dist_y_centers).exp()
    H = (1 - alpha) / ny * phi_y.T @ phi_y
    if alpha > 0:
        H += alpha / nx * phi_x.T @ phi_x
    h = phi_x.mean(0)
    H.diagonal().add_(lambd)
    coeffs = torch.linalg.solve(H, h).clamp_min(0)

    return RuLSIFModel(neg_half_prec, lambd, centers, coeffs)


def rulsif_predict(mdl: RuLSIFModel, x: Tensor) -> Tensor:
    """Predicts the density ratio for the given input `x` using the RuLSIF fitted model.

    Parameters
    ----------
    mdl : RuLSIFModel
        The fitted RuLSIF model (see `rulsif_fit`).
    x : Tensor
        The input data for which to predict the density ratio. Must be a 2D tensor of
        shape `(n_samples, n_features)`, where `n_features` matches the number of
        features used during the model fitting.

    Returns
    -------
    Tensor
        The predicted density ratio for each row in `x`. The shape is `(n_samples,)`.

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
    dist_x_centers: Tensor,
    dist_y_centers: Tensor,
    alpha: float,
    sigmas: Tensor,
    lambds: Tensor,
) -> tuple[Tensor, Tensor]:
    """Computes the optimal sigma and lambda parameters for RuLSIF using
    leave-one-out cross-validation."""
    n_lambds = lambds.numel()
    n_min = min(nx, ny)

    neg_half_precs = (-0.5 * sigmas.square().reciprocal())[:, None, None]
    phis_x_ = (neg_half_precs * dist_x_centers).exp()
    phis_y_ = (neg_half_precs * dist_y_centers).exp()
    H = (1 - alpha) / ny * phis_y_.mT @ phis_y_
    if alpha > 0:
        H += alpha / nx * phis_x_.mT @ phis_x_
    h = phis_x_.unsqueeze(1).mean(2, keepdim=True).mT  # mean over rows
    phis_x = phis_x_[:, :n_min].unsqueeze(1).mT
    phis_y = phis_y_[:, :n_min].unsqueeze(1).mT

    B = H.unsqueeze(1).repeat(1, n_lambds, 1, 1)  # cannot `.expand` here
    B.diagonal(dim1=2, dim2=3).add_(((ny - 1) / ny * lambds).unsqueeze(-1))

    Binv_Y = torch.linalg.solve(B, phis_y)
    denom = ny - (phis_y * Binv_Y).sum(2, keepdim=True)  # sum over rows
    B0 = torch.linalg.solve(B, h) + Binv_Y * (h.mT @ Binv_Y / denom)
    B1 = torch.linalg.solve(B, phis_x) + Binv_Y * (
        (phis_x * Binv_Y).sum(2, keepdim=True) / denom
    )
    B2 = ((ny - 1) / (ny * (nx - 1)) * (nx * B0 - B1)).clamp_min(0)

    w_y = (phis_y * B2).sum(2)
    sum_of_w_x = (phis_x * B2).sum((2, 3))
    scores = (0.5 * w_y.square().sum(2) - sum_of_w_x) / n_min

    min_idx = scores.argmin().item()
    min_row = min_idx // n_lambds
    min_col = min_idx % n_lambds

    return sigmas[min_row], lambds[min_col]
