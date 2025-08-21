# BSD 3-Clause License
#
# Copyright (c) 2025, Arm Limited
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import numpy as np


class HitTest:
    def __init__(self, data_dtype: np.dtype, initial_capacity: int = 256):
        """
        Args:
            data_dtype: NumPy dtype for user data (can be structured or simple).
                        Must be provided for type safety & performance.
            initial_capacity: Initial size of internal arrays.
        """
        self.capacity = initial_capacity
        self.count = 0
        self.data_dtype = np.dtype(data_dtype)

        # Rectangles: (centre_x, centre_y, width, height)
        self.rects = np.zeros((initial_capacity, 4), dtype=np.float32)
        self.data = np.zeros(initial_capacity, dtype=self.data_dtype)

        # Cache for spatial locality
        self._cache_x = float('inf')
        self._cache_y = float('inf')
        self._cache_result = None

    def _resize_if_needed(self):
        """Double array size if capcity is reached"""
        if self.count >= self.capacity:
            old_capacity = self.capacity
            self.capacity *= 2

            # Resize rect array
            new_rects = np.zeros((self.capacity, 4), dtype=np.float32)
            new_rects[:old_capacity] = self.rects
            self.rects = new_rects

            # Resize data array
            new_data = np.zeros(self.capacity, dtype=self.data_dtype)
            new_data[:old_capacity] = self.data
            self.data = new_data

    def add_rect(
        self,
        centre_x: float,
        centre_y: float,
        width: float,
        height: float,
        user_data
    ):
        """
        Add a rectangle with associated user data.
        Args:
            centre_x, centre_y: Rectangle centre coordinates
            width, height: Rectangle dimensions
            user_data: A value matching the dtype passed at initialisation
        """
        self._resize_if_needed()

        self.rects[self.count] = [centre_x, centre_y, width, height]
        self.data[self.count] = user_data

        self.count += 1

    def clear(self):
        self.count = 0
        # invalid cache
        self._cache_x = float('inf')
        self._cache_y = float('inf')
        self._cache_result = None

    def hit_test(self, x: float, y: float):
        """
        Return the top-most user record whose rectangle contains the point.
        Args:
            x, y: Coordinates to test
        Returns:
            Structured record or scalar matching self.data_dtype, or None if no hit.
        """
        if self.count == 0:
            return None

        # Check cache - if mouse barely moved, return cached result
        if (abs(x - self._cache_x) < 2.0 and abs(y - self._cache_y) < 2.0):
            return self._cache_result

        # Cache miss - do the full calculation
        hit_mask = (
            (np.abs(x - self.rects[:self.count, 0]) <= self.rects[:self.count, 2] * 0.5)
            & (np.abs(y - self.rects[:self.count, 1]) <= self.rects[:self.count, 3] * 0.5)
        )

        hit_indices = np.flatnonzero(hit_mask)
        if hit_indices.size > 0:
            result = self.data[hit_indices[-1]]
        else:
            result = None

        # Update cache
        self._cache_x = x
        self._cache_y = y
        self._cache_result = result

        return result
