import unittest

import numpy as np
import tensorflow as tf

import elfa.conv_process
import elfa.inversion

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

    def test_faloading(self):
        WT = np.random.rand(8, 16)
        num_factor = 2
        hpx = 5
        wpx = 5
        num_channels = 16
        loadings_features = elfa.inversion.factor_loading_features(
            WT, num_factor, hpx, wpx, num_channels
        )
        self.assertEqual(loadings_features.shape, (hpx, wpx, num_channels))

    def test_inversion(self):
        img = np.random.rand(32, 32, 3).astype(np.float32)
        partial_model = elfa.conv_process.partial_model(self.dummy_net(), 0)
        output = np.random.rand(30, 30, 16).astype(np.float32)
        loss, result = elfa.inversion.intrinsic_features_inversion(
            img, partial_model, output
        )

        self.assertIsInstance(loss, np.floating)
        self.assertEqual(result.shape, img.shape)


if __name__ == "__main__":
    unittest.main()
