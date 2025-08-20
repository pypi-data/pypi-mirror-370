import unittest

import numpy as np

import elfa.layerfa

np.random.seed(42)


class TestElfa(unittest.TestCase):

    def test_faoutput_deter_residuals(self):
        data = np.random.rand(250, 16)
        n_factors = 8
        hpx = 5
        wpx = 5
        WT, fa, latentFactors = elfa.layerfa.lfa_output(data, n_factors, hpx, wpx)
        R2 = elfa.layerfa.get_determination_coef(data, fa)
        residuals, res_norm = elfa.layerfa.get_model_residuals(data, fa)

        self.assertEqual(WT.shape, (n_factors, 16))
        self.assertEqual(latentFactors.shape, (250, 8))
        self.assertEqual(fa.components_[0][0], WT[0][0])
        self.assertGreaterEqual(R2, 0)
        self.assertEqual(residuals.shape, (16, 16))
        self.assertGreaterEqual(res_norm, 0)

    def test_faresiduals(self):
        data = np.random.rand(250, 16)
        WT = np.random.rand(8, 16)
        latent_factors = np.random.rand(250, 8)
        u, covu, d1, dg = elfa.layerfa.get_factor_residuals_cov(
            data, WT, latent_factors
        )

        self.assertEqual(u.shape, (250, 16))
        self.assertEqual(covu.shape, (16, 16))
        self.assertLessEqual(d1, 1)
        self.assertGreaterEqual(d1, 0)
        self.assertGreaterEqual(dg, 0)

    def test_correlation(self):
        WT = np.random.rand(8, 16)
        data = np.random.rand(250, 16)
        corr_coef = elfa.layerfa.get_correlation_coef(WT, data)

        self.assertEqual(corr_coef.shape, (16,))
        for i in range(8):
            self.assertGreaterEqual(corr_coef[i], 0)

    def test_favariance(self):
        WT = np.random.rand(8, 16)
        data = np.random.rand(250, 16)
        var, prop_var, cum_var = elfa.layerfa.get_factors_variance(WT)
        totvar = elfa.layerfa.get_totvar_explained(WT, data)

        self.assertEqual(var.shape, (8,))
        self.assertEqual(prop_var.shape, (8,))
        self.assertEqual(cum_var.shape, (8,))
        self.assertGreaterEqual(totvar, 0)
        self.assertLess(totvar, 100)


if __name__ == "__main__":
    unittest.main()
