import unittest

import numpy as np
import torch
from scipy.stats import multivariate_normal as mvnorm
from scipy.stats import norm

from torchdensityestimation import ratio, difference


class TestRatioExamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data = torch.load(r"tests/ratio_examples_data.pt")

    def test_univariate(self):
        mean = 0
        std_x = 1 / 8
        std_y = 1 / 2
        n_samples = 500
        rng = np.random.default_rng(0)
        x = torch.from_numpy(
            norm.rvs(size=n_samples, loc=mean, scale=std_x, random_state=rng)
        ).unsqueeze(1)
        y = torch.from_numpy(
            norm.rvs(size=n_samples, loc=mean, scale=std_y, random_state=rng)
        ).unsqueeze(1)
        alpha = 0.1
        seed = int(rng.integers(0, 2**32))
        mdl = ratio.rulsif_fit(x, y, alpha, seed=seed)
        n_vals = 200
        vals = torch.linspace(-1, 2, n_vals, dtype=x.dtype)
        predicted = ratio.rulsif_predict(mdl, vals.reshape(-1, 1))

        data = self.data
        torch.testing.assert_close(
            mdl.negative_half_precision,
            data["univariate_negative_half_precision"],
            msg="Univariate negative half precision mismatch",
        )
        torch.testing.assert_close(
            mdl.regularization,
            data["univariate_regularization"],
            msg="Univariate regularization mismatch",
        )
        torch.testing.assert_close(
            mdl.centers, data["univariate_centers"], msg="Univariate centers mismatch"
        )
        torch.testing.assert_close(
            mdl.coeffs,
            data["univariate_coeffs"],
            msg="Univariate coefficients mismatch",
        )
        torch.testing.assert_close(
            predicted,
            data["univariate_prediction"],
            msg="Univariate prediction mismatch",
        )

    def test_multivariate(self):
        n_dim = 2
        mean = np.ones(n_dim)
        cov_x = np.eye(n_dim) / 8
        cov_y = np.eye(n_dim) / 2
        n_samples = 3000
        rng = np.random.default_rng(0)
        x = torch.from_numpy(
            mvnorm.rvs(size=n_samples, mean=mean, cov=cov_x, random_state=rng)
        )
        y = torch.from_numpy(
            mvnorm.rvs(size=n_samples, mean=mean, cov=cov_y, random_state=rng)
        )
        alpha = 0.0
        sigmas = torch.as_tensor([0.1, 0.3, 0.5, 0.7, 1.0], dtype=x.dtype)
        lambdas = torch.as_tensor([0.01, 0.02, 0.03, 0.04, 0.05], dtype=x.dtype)
        seed = int(rng.integers(0, 2**32))
        mdl = ratio.rulsif_fit(x, y, alpha, sigmas, lambdas, seed=seed)
        n_vals = 200
        vals = torch.linspace(0, 2, n_vals, dtype=x.dtype)
        grid = torch.dstack(torch.meshgrid(vals, vals, indexing="xy")).reshape(-1, 2)
        predicted = ratio.rulsif_predict(mdl, grid).reshape(n_vals, n_vals)

        data = self.data
        torch.testing.assert_close(
            mdl.negative_half_precision,
            data["multivariate_negative_half_precision"],
            msg="Multivariate negative half precision mismatch",
        )
        torch.testing.assert_close(
            mdl.regularization,
            data["multivariate_regularization"],
            msg="Multivariate regularization mismatch",
        )
        torch.testing.assert_close(
            mdl.centers,
            data["multivariate_centers"],
            msg="Multivariate centers mismatch",
        )
        torch.testing.assert_close(
            mdl.coeffs,
            data["multivariate_coeffs"],
            msg="Multivariate coefficients mismatch",
        )
        torch.testing.assert_close(
            predicted,
            data["multivariate_prediction"],
            msg="Multivariate prediction mismatch",
        )


class TestDifferenceExamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data = torch.load(r"tests/difference_examples_data.pt")

    def test_univariate(self):
        mean_x = 0
        mean_y = 1
        std = 1
        n_samples = 50
        rng = np.random.default_rng(0)
        x = torch.from_numpy(
            norm.rvs(size=n_samples, loc=mean_x, scale=std, random_state=rng)
        ).unsqueeze(1)
        y = torch.from_numpy(
            norm.rvs(size=n_samples, loc=mean_y, scale=std, random_state=rng)
        ).unsqueeze(1)
        seed = int(rng.integers(0, 2**32))
        mdl = difference.lsdd_fit(x, y, seed=seed)
        n_vals = 200
        vals = torch.linspace(-5, 5, n_vals, dtype=x.dtype)
        predicted = difference.lsdd_predict(mdl, vals.reshape(-1, 1))

        data = self.data
        torch.testing.assert_close(
            mdl.negative_half_precision,
            data["univariate_negative_half_precision"],
            msg="Univariate negative half precision mismatch",
        )
        torch.testing.assert_close(
            mdl.regularization,
            data["univariate_regularization"],
            msg="Univariate regularization mismatch",
        )
        torch.testing.assert_close(
            mdl.centers, data["univariate_centers"], msg="Univariate centers mismatch"
        )
        torch.testing.assert_close(
            mdl.coeffs,
            data["univariate_coeffs"],
            msg="Univariate coefficients mismatch",
        )
        torch.testing.assert_close(
            predicted,
            data["univariate_prediction"],
            msg="Univariate prediction mismatch",
        )


if __name__ == "__main__":
    unittest.main()
