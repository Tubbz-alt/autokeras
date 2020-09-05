# Copyright 2020 The AutoKeras Authors.
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
import tensorflow as tf

from autokeras.preprocessors.common import AddOneDimension
from autokeras.preprocessors.common import LambdaPreprocessor
from autokeras.preprocessors.encoders import LabelEncoder
from autokeras.preprocessors.encoders import MultiLabelEncoder
from autokeras.preprocessors.encoders import OneHotEncoder


def serialize(encoder):
    return tf.keras.utils.serialize_keras_object(encoder)


def deserialize(config, custom_objects=None):
    return tf.keras.utils.deserialize_keras_object(
        config,
        module_objects=globals(),
        custom_objects=custom_objects,
        printable_module_name="preprocessors",
    )
