# ocfinance

[![Build Passing](https://github.com/dhruvan2006/ocfinance/actions/workflows/release.yml/badge.svg)](https://github.com/dhruvan2006/ocfinance/actions/workflows/release.yml)
[![Tests Passing](https://github.com/dhruvan2006/ocfinance/actions/workflows/tests.yml/badge.svg)](https://github.com/dhruvan2006/ocfinance/actions/workflows/tests.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/ocfinance)](https://pypi.org/project/ocfinance/)
[![PyPI Downloads](https://static.pepy.tech/badge/ocfinance)](https://pypi.org/project/ocfinance/)
[![GitHub License](https://img.shields.io/github/license/dhruvan2006/ocfinance)](https://github.com/dhruvan2006/ocfinance)

`ocfinance` is a python package that enables you to download on-chain data from various sources, including Cryptoquant, CheckOnChain, etc.

## Features
- **Easy Data Download**: Download on-chain data from various sources with a single line of code.
- **CSV Export**: Save data as CSV files for easy analysis in Excel or other tools.
- **Pandas Integration**: Work with data directly as a pandas DataFrame for simple manipulation and analysis.
- **Customizable Queries**: Specify start and end date parameters.

## Documentation: [https://ocfinance.readthedocs.io/](https://ocfinance.readthedocs.io/)

**Complete documentation is available at:** 
[https://ocfinance.readthedocs.io/](https://ocfinance.readthedocs.io/)

## Supported Websites
- [CheckOnChain](https://charts.checkonchain.com/)
- [ChainExposed](https://chainexposed.com/)
- [Woocharts](https://woocharts.com/)
- [Cryptoquant](https://cryptoquant.com/)
- [Bitbo Charts](https://charts.bitbo.io/)
- [Bitcoin Magazine Pro](https://www.bitcoinmagazinepro.com)
- [Blockchain.com](https://www.blockchain.com/explorer/charts)

## Installation
To install the `ocfinance` package, use pip:
```bash
pip install ocfinance
```

## Quick Start
To download the data of a chart, simply obtain the URL and pass it to the download function

```python
import ocfinance as of

# Download the data from the specified URL
data = of.download("https://charts.checkonchain.com/btconchain/pricing/pricing_picycleindicator/pricing_picycleindicator_light.html")

# Usage examples
# Export as CSV
data.to_csv('out.csv')

# Plot
data.plot()
```

For detailed usage instructions, including how to work with Cryptoquant data and advanced features, please refer to our [documentation](https://ocfinance.readthedocs.io/).
