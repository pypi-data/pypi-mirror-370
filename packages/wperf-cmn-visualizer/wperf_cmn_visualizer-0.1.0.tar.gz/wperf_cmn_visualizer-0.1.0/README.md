# CMN Mesh Visualizer

This is a Python project that uses WindowsPerf as a backend to provide a GUI-based visualiser for Arm CMN (Coherent Mesh Network) systems. It enables visual analysis of topology, traffic, and performance metrics using PMU data from XPs, DTCs, and related components—helping engineers identify bottlenecks and understand system behaviour across complex SoCs.

## Installation

To install the project locally:

```bash
pip install .
```
For development mode installation:

```bash
pip install -e .
```

## Project Structure

```bash
cmn-mesh-visualizer/
├── wperf-cmn-visualizer/     # Main Python module containing *.py implementation files
│   └── *.py
├── tests/                    # Test suite containing *.py test files
│   └── *.py
└── pyproject.toml            # Project build and dependency metadata
```

## Contributing

To contribute to the project follow our [Contributing Guidelines](CONTRIBUTING.md).

## License

All code in this repository is licensed under the [BSD 3-Clause License](LICENSE)
