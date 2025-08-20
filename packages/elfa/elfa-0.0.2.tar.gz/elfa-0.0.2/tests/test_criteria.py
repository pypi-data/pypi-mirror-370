import unittest

import numpy as np

import elfa.criteria
import elfa.layerfa

np.random.seed(42)


class TestElfa(unittest.TestCase):

    def test_dataval(self):
        data = np.random.rand(250, 16)
        chi_square_value, p_value, kmo_model = elfa.criteria.check_data_validity(
            data, verbose=True
        )
        self.assertIsInstance(chi_square_value, float)
        self.assertIsInstance(p_value, float)
        self.assertIsInstance(kmo_model, float)
        self.assertGreaterEqual(p_value, 0)
        self.assertLessEqual(p_value, 1)
        self.assertGreaterEqual(kmo_model, 0)

    def test_fafit(self):
        data = np.random.rand(250, 16)
        n_factors = 8
        hpx = 5
        wpx = 5
        WT, fa, latentFactors = elfa.layerfa.lfa_output(
            data,
            n_factors,
            hpx,
            wpx,
        )
        u, covu, communalities, residuals, corr_coef = elfa.criteria.check_fa_fit(
            data, WT, latentFactors, fa, verbose=True
        )

        self.assertEqual(u.shape, (250, 16))
        self.assertEqual(covu.shape, (16, 16))
        self.assertEqual(communalities.shape, (16,))
        self.assertGreaterEqual(np.min(communalities), 0)
        self.assertEqual(residuals.shape, (16, 16))
        self.assertEqual(corr_coef.shape, (16,))
        for i in range(8):
            self.assertGreaterEqual(corr_coef[i], 0)

    def test_eigen_citeria(self):
        data = np.random.rand(250, 16)
        eigenvalues, n_factors = elfa.criteria.eigenvalues_criterion(
            data, plotting=True
        )

        self.assertEqual(len(eigenvalues), 16)
        self.assertGreaterEqual(n_factors, 1)
        self.assertIsInstance(n_factors, int)

    def test_var_criteria(self):
        data = np.random.rand(250, 16)
        m = 0.9
        n_factors = elfa.criteria.variance_nfactors_criterion(data, m)

        self.assertIsInstance(n_factors, int)
        self.assertGreaterEqual(n_factors, 1)

    def test_ses_criteria(self):
        data = np.random.rand(250, 16)
        n_factors = elfa.criteria.standard_error_scree_criterion(data)

        self.assertIsInstance(n_factors, int)
        self.assertGreaterEqual(n_factors, 1)

    def test_bartletts(self):
        data = np.random.rand(250, 16)
        chi_square_value, p_value = elfa.criteria.bartletts_test(data)

        self.assertIsInstance(chi_square_value, float)
        self.assertIsInstance(p_value, float)
        self.assertGreaterEqual(p_value, 0)
        self.assertLessEqual(p_value, 1)

    def test_kmo(self):
        data = np.random.rand(250, 16)
        kmo_model = elfa.criteria.kmo_test(data)

        self.assertIsInstance(kmo_model, float)
        self.assertGreaterEqual(kmo_model, 0)


if __name__ == "__main__":
    unittest.main()
