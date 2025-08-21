[![PyPI version](https://badge.fury.io/py/pyDWS.svg)](https://pypi.org/project/pyDWS)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

# *pyDWS* - Expanding the reach of diffusing wave spectroscopy and tracer bead microrheology

Welcome to the repository for [pyDWS](https://github.com/ManuelH26/pyDWS), a Python package implementing the two-cell Echo diffusing wave spectroscopy (DWS) scheme.

This package provides:

- A calibration-free method to blend and merge Echo and two-cell DWS data

- Exponential spectrum fitting to enhance data quality, particularly at very short times

- Stable corrections for bead and fluid inertia, significantly improving microrheology data quality at high frequencies

pyDWS is based on:

> **M. Helfer, C. Zhang, and F. Scheffold, "Expanding the reach of diffusing wave spectroscopy and tracer bead microrheology," *arXiv*:2502.14973 (2025), [https://doi.org/10.48550/arXiv.2502.14973](https://doi.org/10.48550/arXiv.2502.14973).**

## Introduction

Diffusing Wave Spectroscopy (DWS) is an extension of standard dynamic light scattering (DLS), applied to soft materials that are turbid or opaque. The propagation of light is modeled using light diffusion, characterized by a light diffusion coefficient that depends on the *transport mean free path* l* of the medium. DWS is highly sensitive to small particle displacements or other local fluctuations in the scattering properties and can
probe subnanometer displacements. Analyzing the motion of beads in a viscoelastic matrix, known as one-bead microrheology, is one of the most common applications of DWS. Despite significant advancements since its invention in 1987, including two-cell and multi-speckle DWS, challenges such as merging single and multi-speckle data and limited accuracy for short correlation times persist.

With this package, we address these key challenges in the implementation of the two-cell Echo DWS measurement scheme and propose two major improvements.

First, we introduce a calibration-free method to blend and merge Echo and two-cell DWS measurements.
Second, we show that an unbiased fit of the intensity correlation function (ICF) at short times significantly improves data quality in this regime.

Building on this approach, we also demonstrate that a stable correction for bead and fluid inertia can be applied, further enhancing the reliability of microrheology data at short times.

## Requirements

This package is compatible with **Python ≥ 3.10** and depends on the following libraries:

- `matplotlib >= 3.10.5`  
- `numpy >= 2.3.2`  
- `pandas >= 2.3.1`  
- `scikit-learn >= 1.7.1`  
- `scipy >= 1.16.1`  
- `statsmodels >= 0.14.5`

## Installation

You can install **pyDWS** directly from PyPI using `pip`:  

```bash
pip install pyDWS
```

## Examples

We provide example workflows for wormlike micellar and microgel samples via Jupyter notebooks in the [examples](https://github.com/ManuelH26/pyDWS/tree/main/examples) folder, illustrating how this package can be used.

The example datasets are available in the [data](https://github.com/ManuelH26/pyDWS/tree/main/examples/data) folder. All measurements were performed using the following setup:  
![DWS Setup](https://raw.githubusercontent.com/ManuelH26/pyDWS/refs/heads/main/images/DWS-SetUp.svg)

From the intensity fluctuations, the correlator outputs the intensity correlation function (ICF), g₂(t) - 1.  
The two-cell measurements were performed at a frequency of 13 mHz, and the echo measurements at 25 Hz, both with an amplitude of 3 Vᵣₘₛ. The actual frequency during the Echo measurement is 24.9997 Hz, which is slightly lower than the set frequency because of the inertia of the oscillator.

- [**Wormlike micellar sample:**](https://github.com/ManuelH26/pyDWS/blob/main/examples/dws_micelle.ipynb)
  
    | Parameters | Values |
    | ----------- | ----------- |
    | Sample | An aqueous solution of cetylpyridinium chloride and sodium salicylate (100 mM CPyCl–60 mM NaSal). The sample is mixed with polystyrene beads to a final concentration slightly below 1% by volume. |
    | l* | 330 μm |
    | n_water | 1.33 |
    | λ | 633 nm |
    | L (Cuvette thickness) | 2 mm |
    | a (bead radius) | 210 nm |
    | ρ_b (bead density) | 1050 kg/m³ (polystyrene bead mass density)|
    | ρ (medium density) | 1000 kg/m³ (water)|
    | T  | 20 °C|

- [**Microgel sample:**](https://github.com/ManuelH26/pyDWS/blob/main/examples/dws_microgel.ipynb)
  
    | Parameters | Values |
    | ----------- | ----------- |
    | Sample | pNIPAM microgel in MilliQ water with 5 mol% crosslinker BIS|
    | φ | ~18 wt% |
    | l* | 325 μm |
    | n_water | 1.33 |
    | λ | 633 nm |
    | L (Cuvette thickness) | 5 mm |
    | a (bead radius) | 293 nm (size of the microgel itself)|
    | T  | 28 °C|

---

## Reference

If you use **pyDWS** in your research, please cite:

> M. Helfer, C. Zhang, and F. Scheffold,  
> *"Expanding the reach of diffusing wave spectroscopy and tracer bead microrheology,"*  
> arXiv:2502.14973 (2025).  
> [https://doi.org/10.48550/arXiv.2502.14973](https://doi.org/10.48550/arXiv.2502.14973)
