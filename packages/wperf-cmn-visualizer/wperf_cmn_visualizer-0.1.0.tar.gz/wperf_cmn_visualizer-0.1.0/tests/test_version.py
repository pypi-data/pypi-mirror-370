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

import pytest
from common import run_command

from wperf_cmn_visualizer import __version__


def test_version_is_string():
    """Verify that the __version__ variable is a string."""
    assert isinstance(__version__, str)


def test_version_not_empty():
    """Ensure the __version__ string is not empty or just whitespace."""
    assert __version__.strip() != ''


def test_version_matches_git_tag():
    """
    Confirm that the version string matches the latest Git tag.
    If no Git tags are found, the test is skipped.
    """
    stdout, stderr = run_command(['git', 'describe', '--tags', '--abbrev=0'])
    git_tag = stdout.strip()
    if not git_tag:
        pytest.skip("No git tags available")
    else:
        assert git_tag.decode() == __version__


def test_cli_version_output():
    """
    Verify that the CLI --version option outputs the correct version string.
    """
    stdout, _ = run_command(['wperf-cmn-visualizer', '--version'])
    assert stdout.strip().decode() == __version__
