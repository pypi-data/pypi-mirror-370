# Gumerov Expansion Coefficients

<p align="center">
  <a href="https://github.com/34j/gumerov-expansion-coefficients/actions/workflows/ci.yml?query=branch%3Amain">
    <img src="https://img.shields.io/github/actions/workflow/status/34j/gumerov-expansion-coefficients/ci.yml?branch=main&label=CI&logo=github&style=flat-square" alt="CI Status" >
  </a>
  <a href="https://gumerov-expansion-coefficients.readthedocs.io">
    <img src="https://img.shields.io/readthedocs/gumerov-expansion-coefficients.svg?logo=read-the-docs&logoColor=fff&style=flat-square" alt="Documentation Status">
  </a>
  <a href="https://codecov.io/gh/34j/gumerov-expansion-coefficients">
    <img src="https://img.shields.io/codecov/c/github/34j/gumerov-expansion-coefficients.svg?logo=codecov&logoColor=fff&style=flat-square" alt="Test coverage percentage">
  </a>
</p>
<p align="center">
  <a href="https://github.com/astral-sh/uv">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv">
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff">
  </a>
  <a href="https://github.com/pre-commit/pre-commit">
    <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=flat-square" alt="pre-commit">
  </a>
</p>
<p align="center">
  <a href="https://pypi.org/project/gumerov-expansion-coefficients/">
    <img src="https://img.shields.io/pypi/v/gumerov-expansion-coefficients.svg?logo=python&logoColor=fff&style=flat-square" alt="PyPI Version">
  </a>
  <img src="https://img.shields.io/pypi/pyversions/gumerov-expansion-coefficients.svg?style=flat-square&logo=python&amp;logoColor=fff" alt="Supported Python versions">
  <img src="https://img.shields.io/pypi/l/gumerov-expansion-coefficients.svg?style=flat-square" alt="License">
</p>

---

**Documentation**: <a href="https://gumerov-expansion-coefficients.readthedocs.io" target="_blank">https://gumerov-expansion-coefficients.readthedocs.io </a>

**Source Code**: <a href="https://github.com/34j/gumerov-expansion-coefficients" target="_blank">https://github.com/34j/gumerov-expansion-coefficients </a>

---

Multiple translation and rotation coefficients for the 3D Helmholtz Equation

## Installation

Install this via pip (or your favourite package manager):

```shell
pip install gumerov-expansion-coefficients
```

## Usage

```python
from gumerov_expansion_coefficients import translational_coefficients

translational_coefficients(
    k * r, theta, phi, same=True, n_end=10
)  # (R|R) coefficients from 0 to 9 th degree
translational_coefficients(
    k * r, theta, phi, same=False, n_end=10
)  # (S|R) coefficients from 0 to 9 th degree
```

## References

- Gumerov, N. A., & Duraiswami, R. (2004). Recursions for the Computation of Multipole Translation and Rotation Coefficients for the 3-D Helmholtz Equation. SIAM Journal on Scientific Computing, 25(4), 1344–1381. https://doi.org/10.1137/S1064827501399705

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- prettier-ignore-start -->
<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- markdownlint-disable -->
<!-- markdownlint-enable -->
<!-- ALL-CONTRIBUTORS-LIST:END -->
<!-- prettier-ignore-end -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

## Credits

[![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json)](https://github.com/copier-org/copier)

This package was created with
[Copier](https://copier.readthedocs.io/) and the
[browniebroke/pypackage-template](https://github.com/browniebroke/pypackage-template)
project template.
