# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Test the Keras MNIST model on GPU."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import functools

from absl.testing import parameterized
import tensorflow as tf
import tensorflow_datasets as tfds

from tensorflow.python.distribute import combinations
from tensorflow.python.distribute import strategy_combinations
from official.utils.misc import keras_utils
from official.utils.testing import integration
from official.vision.image_classification import mnist_main


def eager_strategy_combinations():
  return combinations.combine(
      distribution=[
          strategy_combinations.default_strategy,
          strategy_combinations.tpu_strategy,
          strategy_combinations.one_device_strategy_gpu,
      ],
      mode="eager",
  )


class KerasMnistTest(tf.test.TestCase, parameterized.TestCase):
  """Unit tests for sample Keras MNIST model."""
  _tempdir = None

  @classmethod
  def setUpClass(cls):  # pylint: disable=invalid-name
    super(KerasMnistTest, cls).setUpClass()
    mnist_main.define_mnist_flags()

  def tearDown(self):
    super(KerasMnistTest, self).tearDown()
    tf.io.gfile.rmtree(self.get_temp_dir())

  @combinations.generate(eager_strategy_combinations())
  def test_end_to_end(self, distribution):
    """Test Keras MNIST model with `strategy`."""
    config = keras_utils.get_config_proto_v1()
    tf.compat.v1.enable_eager_execution(config=config)

    extra_flags = [
        "-train_epochs", "1",
        # Let TFDS find the metadata folder automatically
        "--data_dir="
    ]

    def _mock_dataset(self, *args, **kwargs):  # pylint: disable=unused-argument
      """Generate mock dataset with TPU-compatible dtype (instead of uint8)."""
      return tf.data.Dataset.from_tensor_slices({
          "image": tf.ones(shape=(10, 28, 28, 1), dtype=tf.int32),
          "label": tf.range(10),
      })

    run = functools.partial(mnist_main.run, strategy_override=distribution)

    with tfds.testing.mock_data(as_dataset_fn=_mock_dataset):
      integration.run_synthetic(
          main=run,
          synth=False,
          tmp_root=self.get_temp_dir(),
          extra_flags=extra_flags)


if __name__ == "__main__":
  tf.compat.v1.enable_v2_behavior()
  tf.test.main()
