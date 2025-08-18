<a id="readme-top"></a>

[![PyPI Version](https://img.shields.io/pypi/v/teppy)](https://pypi.org/project/teppy/)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-GPLv3-green)](https://github.com/gianlucagag/TEPpy/LICENSE)
[![Open Issues](https://img.shields.io/github/issues/gianlucagag/TEPpy)](https://github.com/gianlucagag/TEPpy/issues)

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/gianlucagag/TEPpy">
    <img src="https://raw.githubusercontent.com/gianlucagag/TEPpy/docs/images/logo.png" 
         alt="TEPpy Logo" width="220">
  </a>

  <h1 align="center">TEPpy</h1>
  
  <p align="center">
    TMS-EEG Evoked Potential Analysis Framework
    <br />
    <a href="https://github.com/gianlucagag/TEPpy/tree/main/examples"><strong>Explore examples »</strong></a>
    <br />
    <br />
    <a href="https://github.com/gianlucagag/TEPpy/issues/new?labels=bug&template=bug-report.md">
      <img src="https://img.shields.io/badge/REPORT-BUG-red" alt="Report Bug">
    </a>
    &nbsp;
    <a href="https://github.com/gianlucagag/TEPpy/issues/new?labels=enhancement&template=feature-request.md">
      <img src="https://img.shields.io/badge/REQUEST-FEATURE-green" alt="Request Feature">
    </a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#key-features">Key Features</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#dependencies">Dependencies</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#citation">Citation</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

TEPpy is a Python package for analyzing Transcranial Magnetic Stimulation combined with Electroencephalography (TMS-EEG) data. It provides tools for characterizing TMS-EEG evoked potential (TEP) temporal and spectral features, with automated peak detection and time-frequency analysis methods.

### Key Features

- Convert MNE-Python Epochs objects to TEP objects
- Automatic detection of TEP peaks
- Automatic selection of most reponsive channels
- Time-frequency analysis using Stockwell transform
- Extraction of temporal and spectral features
- Visualization of temporal and spectral features
- Customizable analysis parameters for research flexibility

### Analysis Workflow

![TEPpy Analysis Workflow](docs/images/workflow.png)
*Typical TEPpy analysis workflow from MNE Epochs to extracted features*

<!-- GETTING STARTED -->
## Getting Started

### Dependencies

- numpy>=2.0.1
- scipy>=1.14.0
- mne>=1.9.0
- matplotlib>=3.9.1
- stockwell>=1.2

### Installation

Install from PyPI:

```bash
pip install teppy
```

<!-- USAGE -->
## Usage

```python
import mne
from teppy import TEP

TEP.plot_summary()
```
<div align="center">
  <div style="display:flex; flex-wrap:wrap; justify-content:center">
    <div style="margin:10px; text-align:center">
      <img src="docs/images/plot_summary.png" width="50%">
    </div>
  </div>
</div>

```python
timef = TEP.compute_timefreq()
timef.plot_natfreq1()
```

<div align="center">
  <div style="display:flex; flex-wrap:wrap; justify-content:center">
    <div style="margin:10px; text-align:center">
      <img src="docs/images/plot_natfreq1.png" width="50%">
    </div>
  </div>
</div>

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CITATION -->
## Citation

<!-- LICENSE -->
## License

<!-- CONTACT -->
## Contact
