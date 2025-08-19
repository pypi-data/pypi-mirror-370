# ccfit2

`ccfit2` is a package for working with magnetometry data, specifically those from AC susceptibility, DC decay, and DC Waveform measurements.

Although the main use of `ccfit2` is to extract and later fit temperature/field dependent relaxation rate data from these experiments, the modular nature
of `ccfit2` means that the user is free to include any of `ccfit2`'s functionality in their own work.

## Documentation and Installation

To get started, head to the online documentation for `ccfit2` [here](https://chilton-group.gitlab.io/cc-fit2/).

## Developers

Install in editable mode by running

```
pip install -e .
```

in the repository HEAD.

## Reference

We request that any data processed with `ccfit2` is accompanied by the version number (obtained with `pip show ccfit2`)  and **both** of the following citations

1. William J. A. Blackmore, Gemma K. Gransbury, Peter Evans, Jon G. C. Kragskow, David P. Mills, and Nicholas F. Chilton. Characterisation of magnetic relaxation on extremely long timescales. Phys. Chem. Chem. Phys., 2023, 25, 16735-16744. URL: https://dx.doi.org/10.1039/d3cp01278f

2. Daniel Reta and Nicholas F. Chilton. Uncertainty estimates for magnetic relaxation times and magnetic relaxation parameters. 	Phys. Chem. Chem. Phys., 2019, 21, 23567-23575. URL: https://dx.doi.org/10.1039/C9CP04301B 
