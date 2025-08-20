import unittest
from pathlib import Path

import numpy as np
import tensorflow as tf
from matplotlib import pyplot as plt

import elfa.loadshow

np.random.seed(42)

ROOT = Path(__file__).parent.parent.parent.resolve()
image_path = ROOT / "Python" / "PythonScripts" / "Datasets" / "sheep.jpg"


class TestElfa(unittest.TestCase):

    def test_load(self):
        size = 32
        img = elfa.loadshow.load(image_path, size)
        self.assertEqual(img.shape, (size, size, 3))
        plt.imshow(img)
        plt.show()

    def test_deprocess(self):
        img = np.random.rand(32, 32, 3)
        img_processed = elfa.loadshow.deprocess(img)
        self.assertEqual(img_processed.shape, (32, 32, 3))
        self.assertTrue(np.all(img_processed >= 0))
        self.assertTrue(np.all(img_processed <= 255))
        plt.imshow(img_processed)
        plt.show()

    def test_show(self):
        img = np.random.rand(32, 32, 3)
        # Check if the image is displayed without errors
        elfa.loadshow.show(img)
        self.assertTrue(True)
        elfa.loadshow.show(img, gray=True)
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
