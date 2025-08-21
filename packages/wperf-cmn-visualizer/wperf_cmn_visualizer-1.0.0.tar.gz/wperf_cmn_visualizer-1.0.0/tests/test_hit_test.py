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
from wperf_cmn_visualizer.hit_test import HitTest


class TestHitTest:
    """Tests for HitTest spatial data structure."""

    def test_initial_state(self):
        """Test proper initialization."""
        hit_test = HitTest(np.dtype(np.int32), 128)

        assert hit_test.capacity == 128
        assert hit_test.count == 0
        assert hit_test.data_dtype == np.dtype(np.int32)
        assert hit_test.rects.shape == (128, 4)
        assert hit_test.data.shape == (128,)

    def test_structured_dtype_initialization(self):
        """Test initialization with structured dtype."""
        node_dtype = np.dtype([
            ('type', np.uint8),
            ('x', np.uint8),
            ('y', np.uint8),
            ('port', np.uint8),
        ])

        hit_test = HitTest(node_dtype, 64)
        assert hit_test.data_dtype == node_dtype
        assert hit_test.data.shape == (64,)

    def test_add_single_rect(self):
        """Test adding a single rectangle."""
        hit_test = HitTest(np.dtype(np.int32), 10)
        hit_test.add_rect(100.0, 50.0, 20.0, 30.0, 42)

        assert hit_test.count == 1
        np.testing.assert_array_equal(hit_test.rects[0], [100.0, 50.0, 20.0, 30.0])
        assert hit_test.data[0] == 42

    def test_add_structured_data(self):
        """Test adding rectangle with structured data."""
        node_dtype = np.dtype([
            ('type', np.uint8),
            ('x', np.uint8),
            ('y', np.uint8),
        ])

        hit_test = HitTest(node_dtype)

        node_data = np.array((1, 5, 3), dtype=node_dtype)
        hit_test.add_rect(10.0, 20.0, 5.0, 5.0, node_data)

        assert hit_test.count == 1
        assert hit_test.data[0]['type'] == 1
        assert hit_test.data[0]['x'] == 5
        assert hit_test.data[0]['y'] == 3

    def test_clear(self):
        """Test clearing all rectangles."""
        hit_test = HitTest(np.dtype(np.int32))

        hit_test.add_rect(10.0, 10.0, 5.0, 5.0, 1)
        hit_test.add_rect(20.0, 20.0, 5.0, 5.0, 2)
        assert hit_test.count == 2

        hit_test.clear()
        assert hit_test.count == 0

    def test_hit_test_hit(self):
        """Test hitting the center of a rectangle."""
        hit_test = HitTest(np.dtype(np.int32))
        hit_test.add_rect(100.0, 50.0, 20.0, 30.0, 42)

        result = hit_test.hit_test(100.0, 50.0)
        assert result == 42

    def test_hit_test_edge_hit(self):
        """Test hitting the edges of a rectangle."""
        hit_test = HitTest(np.dtype(np.int32))
        hit_test.add_rect(100.0, 50.0, 20.0, 30.0, 42)

        # Test all four edges
        assert hit_test.hit_test(90.0, 50.0) == 42
        assert hit_test.hit_test(110.0, 50.0) == 42
        assert hit_test.hit_test(100.0, 35.0) == 42
        assert hit_test.hit_test(100.0, 65.0) == 42

    def test_hit_test_corner_hit(self):
        """Test hitting the corners of a rectangle."""
        hit_test = HitTest(np.dtype(np.int32))
        hit_test.add_rect(100.0, 50.0, 20.0, 30.0, 42)

        # Test all four corners
        assert hit_test.hit_test(90.0, 35.0) == 42
        assert hit_test.hit_test(110.0, 35.0) == 42
        assert hit_test.hit_test(90.0, 65.0) == 42
        assert hit_test.hit_test(110.0, 65.0) == 42

    def test_hit_test_miss(self):
        """Test missing a rectangle."""
        hit_test = HitTest(np.dtype(np.int32))
        hit_test.add_rect(100.0, 50.0, 20.0, 30.0, 42)

        # Test points outside the rectangle
        assert hit_test.hit_test(89.0, 50.0) is None
        assert hit_test.hit_test(111.0, 50.0) is None
        assert hit_test.hit_test(100.0, 34.0) is None
        assert hit_test.hit_test(100.0, 66.0) is None

        # Very Far away points
        assert hit_test.hit_test(0.0, 0.0) is None
        assert hit_test.hit_test(1000.0, 1000.0) is None

    def test_hit_test_empty(self):
        """Test hit testing with no rectangles."""
        hit_test = HitTest(np.dtype(np.int32))

        result = hit_test.hit_test(100.0, 50.0)
        assert result is None

    def test_hit_test_multiple_rects_returns_topmost(self):
        """Test that overlapping rectangles return the topmost (last added)."""
        hit_test = HitTest(np.dtype(np.int32))

        # Add overlapping rectangles
        hit_test.add_rect(100.0, 50.0, 20.0, 30.0, 1)
        hit_test.add_rect(105.0, 55.0, 20.0, 30.0, 2)
        hit_test.add_rect(110.0, 60.0, 20.0, 30.0, 3)

        # Test point that hits all three
        result = hit_test.hit_test(105.0, 55.0)
        assert result == 3  # should be last added rect (top most)

    def test_hit_test_multiple_rects_no_overlap(self):
        """Test multiple non-overlapping rectangles."""
        hit_test = HitTest(np.dtype(np.int32))

        hit_test.add_rect(10.0, 10.0, 10.0, 10.0, 1)
        hit_test.add_rect(30.0, 30.0, 10.0, 10.0, 2)
        hit_test.add_rect(50.0, 50.0, 10.0, 10.0, 3)

        # Test hitting each rectangle
        assert hit_test.hit_test(10.0, 10.0) == 1
        assert hit_test.hit_test(30.0, 30.0) == 2
        assert hit_test.hit_test(50.0, 50.0) == 3

        # Test missing all rectangles
        assert hit_test.hit_test(20.0, 20.0) is None

    def test_resize_functionality(self):
        """Test that arrays resize properly when capacity is exceeded."""
        initial_capacity = 4
        hit_test = HitTest(np.dtype(np.int32), initial_capacity)

        # Add more rectangles than initial capacity
        for i in range(10):
            hit_test.add_rect(float(i * 10), float(i * 10), 5.0, 5.0, i)

        assert hit_test.count == 10
        assert hit_test.capacity >= 10  # Should have been resized

        # Verify overflown data has been successfully added
        for i in range(10):
            result = hit_test.hit_test(float(i * 10), float(i * 10))
            assert result == i

    def test_zero_size_rectangle(self):
        """Test edge case with zero-size rectangle."""
        hit_test = HitTest(np.dtype(np.int32))

        hit_test.add_rect(10.0, 20.0, 0.0, 0.0, 42)
        # only successful hit at center
        assert hit_test.hit_test(10.0, 20.0) == 42
        assert hit_test.hit_test(15.0, 20.0) is None
        assert hit_test.hit_test(10.0, 25.0) is None

    def test_negative_coordinates(self):
        """Test with negative coordinates."""
        hit_test = HitTest(np.dtype(np.int32))

        hit_test.add_rect(-50.0, -100.0, 20.0, 30.0, 99)

        # Test center and edges
        assert hit_test.hit_test(-50.0, -100.0) == 99
        assert hit_test.hit_test(-60.0, -115.0) == 99
        assert hit_test.hit_test(-40.0, -85.0) == 99

        # Should Miss
        assert hit_test.hit_test(-61.0, -100.0) is None
        assert hit_test.hit_test(-50.0, -116.0) is None
