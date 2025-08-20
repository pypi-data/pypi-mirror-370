import unittest

import numpy as np
import tensorflow as tf

import elfa.conv_process

np.random.seed(42)


class TestElfa(unittest.TestCase):

    def dummy_net(self):
        inputs = tf.keras.Input(shape=(32, 32, 3), name="input")
        x = tf.keras.layers.Conv2D(16, (3, 3), activation="relu", name="conv1")(inputs)
        x = tf.keras.layers.Conv2D(32, (3, 3), activation="relu", name="conv2")(x)
        x = tf.keras.layers.Flatten(name="flatten")(x)
        outputs = tf.keras.layers.Dense(5, activation="softmax", name="output")(x)
        model = tf.keras.Model(inputs=inputs, outputs=outputs)

        return model

    def dummy_dataset(self):
        images = np.random.rand(10, 32, 32, 3)
        labels = np.random.randint(0, 5, size=10)
        return tf.data.Dataset.from_tensor_slices((images, labels))

    def test_getconvidx(self):
        idx_conv = elfa.conv_process.get_conv_indx(self.dummy_net())
        idxs = [1, 2]
        self.assertEqual(len(idx_conv), 2)
        self.assertEqual(idx_conv, idxs)

    def test_partialmodel(self):
        partial_model = elfa.conv_process.partial_model(self.dummy_net(), 0)
        self.assertEqual(partial_model.layers[-1].name, "conv1")
        self.assertIsInstance(partial_model, tf.keras.Model)

        partial_model1 = elfa.conv_process.partial_model(
            self.dummy_net(), None, id_layer=1
        )
        self.assertEqual(partial_model1.layers[-1].name, "conv1")
        self.assertIsInstance(partial_model1, tf.keras.Model)

    def test_convoutput(self):
        partial_model = elfa.conv_process.partial_model(self.dummy_net(), 0)
        data, h, w, n = elfa.conv_process.conv_output_data(
            partial_model, np.random.rand(1, 32, 32, 3)
        )
        self.assertEqual(h, 30)
        self.assertEqual(w, 30)
        self.assertEqual(n, 16)
        self.assertEqual(data.shape, (900, 16))

    def test_getfainput(self):
        dstrain = self.dummy_dataset()
        img_size = (32, 32)
        batch_size = 2
        partial_model = elfa.conv_process.partial_model(self.dummy_net(), 0)

        data, h, w, n = elfa.conv_process.get_fa_input(
            batch_size, dstrain, img_size, partial_model
        )
        self.assertEqual(h, 30)
        self.assertEqual(w, 30)
        self.assertEqual(n, 16)
        self.assertEqual(data.shape, (1800, 16))


if __name__ == "__main__":
    unittest.main()
