# ultrasound-metrics

[![Linting badge](https://github.com/Forest-Neurotech/ultrasound-metrics/actions/workflows/check.yml/badge.svg)](https://github.com/Forest-Neurotech/ultrasound-metrics/actions/workflows/check.yml/badge.svg)
[![Test badge](https://github.com/Forest-Neurotech/ultrasound-metrics/actions/workflows/test.yml/badge.svg)](https://github.com/Forest-Neurotech/ultrasound-metrics/actions/workflows/test.yml/badge.svg)

> **⚠️ Alpha Release**
>
> This library is currently under active development and is released as an alpha version. The primary goal of this release is to collect community feedback.

## Introduction

*ultrasound-metrics* is an open-source Python library for ultrasound data and image quality analysis developed at [Forest Neurotech](https://forestneurotech.org/). It is written in the [Array API standard](https://data-apis.org/array-api/2024.12/), making it compatible across NumPy, JAX, and PyTorch backends. The implementation supports GPU acceleration (CuPy, JAX, PyTorch), software acceleration (JIT or AOT compilation), and interactive region-of-interest selection for metrics in 2D.

Documentation on *ultrasound-metrics* can be found [here](https://forest-neurotech-ultrasound-metrics.readthedocs-hosted.com/latest/) and examples can be viewed [here](https://forest-neurotech-ultrasound-metrics.readthedocs-hosted.com/latest/example_gallery/index.html). We are actively taking [requests](https://github.com/Forest-Neurotech/ultrasound-metrics/issues) for additional metrics that may be helpful to ultrasound researchers.

## Installation

### Install from PyPi (recommended:)

```bash
pip install ultrasound-metrics
```

### Build from source

```bash
make install
```

Build prerequisites:
* `uv >= 0.6.10`
* optional: `make`

## Documentation
We currently support the following ultrasound data and image quality metrics:
* contrast-to-noise ratio (CNR)
* generalized contrast-to-noise ratio (gCNR)
* signal-to-noise ratio for raw radiofrequency signals (RF SNR)
* temporal signal-to-noise ratio (tSNR)
* sharpness (tenengrad)
* coherence factor
and more!

We are actively taking requests for metrics, ultrasound data file types to support, and additional features that would be helpful to the ultrasound imaging community. To make a feature request, please [submit a GitHub issue](https://github.com/Forest-Neurotech/ultrasound-metrics/issues).

## Acknowledgements

ultrasound-metrics builds upon the excellent work of the ultrasound imaging community:

- **[ultraspy](https://ultraspy.readthedocs.io/en/latest/index.html#)** - For educational examples and validation benchmarks
- **[PICMUS](https://www.creatis.insa-lyon.fr/Challenge/IEEE_IUS_2016/)** - For public, standardized datasets used in examples

This package was developed by the [Forest Neurotech](https://forestneurotech.org/) team, a [Focused Research Organization](https://www.convergentresearch.org/about-fros) supported by [Convergent Research](https://www.convergentresearch.org/) and [generous philanthropic funders](https://www.convergentresearch.org/fro-portfolio).
