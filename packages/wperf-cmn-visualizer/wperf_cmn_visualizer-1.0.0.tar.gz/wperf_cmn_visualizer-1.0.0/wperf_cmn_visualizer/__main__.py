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

"""
Entry point for running cmn-visualizer as a module.
"""
import sys
import argparse
from . import __version__
from .config import Config
from .wperf_cmn_visualizer import wperfCmnVisualizer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="A GUI-based visualizer for Arm CMN (Coherent Mesh Network)"
                    " systems using WindowsPerf backend"
    )
    parser.add_argument(
        "--version", action="version", version=f"{__version__}"
    )
    parser.add_argument(
        "--topology",
        type=str,
        default=Config.DEFAULT_TOPOLOGY_FILE,
        help=f"Path to the topology JSON file (default: {Config.DEFAULT_TOPOLOGY_FILE})",
    )
    parser.add_argument(
        "--telemetry",
        type=str,
        help="Path to the directory with Telemetry CSV files.",
    )
    return parser.parse_args()


def main() -> int:
    args: argparse.Namespace = parse_args()
    app: wperfCmnVisualizer = wperfCmnVisualizer(args)
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
