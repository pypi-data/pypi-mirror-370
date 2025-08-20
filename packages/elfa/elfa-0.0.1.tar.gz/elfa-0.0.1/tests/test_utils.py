import unittest

import numpy as np
import tensorflow as tf

import elfa.utils

np.random.seed(42)
ROOT = Path(__file__).parent.resolve()


class TestElfa(unittest.TestCase):

    def dummy_dataset(self):
        images = np.random.rand(10, 32, 32, 3)
        labels = np.random.randint(0, 5, size=10)
        return tf.data.Dataset.from_tensor_slices((images, labels))

    def test_writedata(self):
        data = ["test", "data"]
        file_name = ROOT / "test_output.csv"
        elfa.utils.write_data(data, file_name)

        with open(file_name, "r") as f:
            content = f.read().strip()
            self.assertEqual(content, "test,data")

    def test_getbatch(self):
        dataset = self.dummy_dataset()
        img_size = (32, 32)
        batch_size = 2

        images_batch, images_list = elfa.utils.get_batch(batch_size, dataset, img_size)

        self.assertEqual(images_batch.shape, (batch_size, 32, 32, 3))
        self.assertEqual(len(images_list), batch_size)
        self.assertEqual(images_list[0].shape, (32, 32, 3))

    def test_getbatchlabels(self):
        dataset = self.dummy_dataset()
        img_size = (32, 32)
        batch_size = 2

        images_batch, images_list, labels_list = elfa.utils.get_batch_labels(
            batch_size, dataset, img_size
        )

        self.assertEqual(images_batch.shape, (batch_size, 32, 32, 3))
        self.assertEqual(len(images_list), batch_size)
        self.assertEqual(images_list[0].shape, (32, 32, 3))
        self.assertEqual(len(labels_list), batch_size)

    def test_setbatch(self):
        images = np.random.rand(10, 32, 32, 3)
        labels = np.random.randint(0, 5, size=10)
        x_batch_list, x_batch, y_batch, idx_batch = elfa.utils.set_batch(
            images, labels, 2
        )

        self.assertEqual(len(idx_batch), 2)
        self.assertTrue(np.allclose(y_batch, np.array([labels[i] for i in idx_batch])))
        self.assertTrue(np.allclose(np.array(x_batch_list), images[idx_batch]))
        self.assertEqual(x_batch.shape, (2, 32, 32, 3))

    def test_resizemap(self):
        map = np.random.rand(10, 10)
        size = (20, 20)

        resized_map = elfa.utils.resize_map(map, size)
        self.assertTrue(
            np.allclose(
                resized_map.numpy(),
                tf.image.resize(map[:, :, tf.newaxis], (20, 20))[:, :, 0].numpy(),
            )
        )
        self.assertEqual(resized_map.shape, (20, 20))

    def test_importtfds(self):
        data_name = "imagenette/320px-v2"
        set_name = "validation"
        dataset = elfa.utils.import_tf_dataset(data_name, set_name)

        self.assertIsInstance(dataset, tf.data.Dataset)


if __name__ == "__main__":
    unittest.main()
