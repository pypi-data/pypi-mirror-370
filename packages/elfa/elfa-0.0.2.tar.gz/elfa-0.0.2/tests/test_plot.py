import unittest
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt

import elfa.plot_module

np.random.seed(42)
ROOT = Path(__file__).parent.resolve()


class TestElfa(unittest.TestCase):

    def test_gallery(self):
        images = np.random.rand(1024, 5)
        images_shape = (32, 32)
        n_col = 2
        n_row = 3
        cmap = plt.cm.magma
        path = ROOT / "test_gallery.png"
        elfa.plot_module.plot_gallery(
            images,
            images_shape,
            n_col=n_col,
            n_row=n_row,
            cmap=cmap,
            path=path,
        )
        self.assertTrue(path.exists())

    def test_matrix(self):
        matrix = np.random.rand(8, 16)
        cmap = "magma"
        path = ROOT / "test_matrix.png"
        elfa.plot_module.plot_matrix(matrix, cmap=cmap, path=path)
        self.assertTrue(path.exists())

    def test_montage(self):
        images = np.random.rand(32, 32, 3, 5)
        elfa.plot_module.images_montage(images)
        self.assertTrue(True)

    def test_similarfa(self):
        WT = np.random.rand(8, 16)
        n_factor = 2
        output = np.random.rand(250, 16)
        factors = np.random.rand(250, 8)
        num_img = 5
        img_size = (5, 5)
        max_value = 0.4
        path = ROOT / "test_similarfa.png"
        elfa.plot_module.similar_to_factor(
            WT,
            n_factor,
            output,
            factors,
            num_img,
            img_size,
            max_value=max_value,
            path=path,
        )

        self.assertTrue(path.exists())

    def test_attr(self):
        num_images = 5
        images = [np.random.rand(224, 224, 3) for _ in range(num_images)]
        attr_efam0 = np.random.rand(num_images, 5, 5)
        attr_efam1 = np.random.rand(num_images, 5, 5)
        attrs = {}
        attrs["efam0"] = attr_efam0
        attrs["efam1"] = attr_efam1
        cmap = "magma"
        path_sup = ROOT / "test_attrsup.png"
        path_mask = ROOT / "test_attrmask.png"

        elfa.plot_module.plot_attributions(
            num_images, images, attrs, mode="superposition", cmap=cmap, path=path_sup
        )
        self.assertTrue(path_sup.exists())

        elfa.plot_module.plot_attributions(
            num_images, images, attrs, mode="mask", cmap=cmap, path=path_mask
        )
        self.assertTrue(path_mask.exists())


if __name__ == "__main__":
    unittest.main()
