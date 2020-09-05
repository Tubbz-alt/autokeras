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
import numpy as np
from tensorflow.python.util import nest

from autokeras.engine import analyser

CATEGORICAL = "categorical"
NUMERICAL = "numerical"


class InputAnalyser(analyser.Analyser):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shape = None

    def update(self, data):
        self.shape = data.shape.as_list()


class ImageAnalyser(InputAnalyser):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.has_channel_dim = False

    def finalize(self):
        if len(self.shape) not in [3, 4]:
            raise ValueError(
                "Expect the data to ImageInput to have shape (batch_size, "
                "height, width, channels) or (batch_size, height, width) "
                "dimensions, but got input shape {shape}".format(shape=self.shape)
            )
        self.has_channel_dim = len(self.shape) == 4


class StructuredDataAnalyser(InputAnalyser):
    def __init__(self, column_names=None, column_types=None, **kwargs):
        super().__init__(**kwargs)
        self.column_names = column_names
        self.column_types = column_types
        # Variables for inferring column types.
        self.count_numerical = None
        self.count_categorical = None
        self.count_unique_numerical = []
        self.num_col = None

    def update(self, data):
        super().update(data)
        # Calculate the statistics.
        data = nest.flatten(data)[0].numpy()
        for instance in data:
            self._update_instance(instance)

    def _update_instance(self, x):
        if self.num_col is None:
            self.num_col = len(x)
            self.count_numerical = np.zeros(self.num_col)
            self.count_categorical = np.zeros(self.num_col)
            for i in range(len(x)):
                self.count_unique_numerical.append({})
        for i in range(self.num_col):
            x[i] = x[i].decode("utf-8")
            try:
                tmp_num = float(x[i])
                self.count_numerical[i] += 1
                if tmp_num not in self.count_unique_numerical[i]:
                    self.count_unique_numerical[i][tmp_num] = 1
                else:
                    self.count_unique_numerical[i][tmp_num] += 1
            except ValueError:
                self.count_categorical[i] += 1

    def finalize(self):
        self.infer_column_types()

        # Check if column_names has the correct length.
        if len(self.column_names) != self.shape[1]:
            raise ValueError(
                "Expect column_names to have length {expect} "
                "but got {actual}.".format(
                    expect=self.shape[1], actual=len(self.column_names)
                )
            )

    def infer_column_types(self):
        column_types = {}

        # Check if column_names has the correct length.
        if len(self.column_names) != self.num_col:
            raise ValueError(
                "Expect column_names to have length {expect} "
                "but got {actual}.".format(
                    expect=self.num_col, actual=len(self.column_names)
                )
            )

        for i in range(self.num_col):
            if self.count_categorical[i] > 0:
                column_types[self.column_names[i]] = CATEGORICAL
            elif (
                len(self.count_unique_numerical[i]) / self.count_numerical[i] < 0.05
            ):
                column_types[self.column_names[i]] = CATEGORICAL
            else:
                column_types[self.column_names[i]] = NUMERICAL

        # Partial column_types is provided.
        if self.column_types is None:
            self.column_types = {}
        for key, value in column_types.items():
            if key not in self.column_types:
                self.column_types[key] = value
