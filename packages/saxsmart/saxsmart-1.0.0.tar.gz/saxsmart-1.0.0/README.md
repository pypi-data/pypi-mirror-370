# SAXSMART: SAXS Modelling and Refinement Toolkit

## Overview

SAXSMART is an interactive web application for the analysis and refinement of Small-Angle X-ray Scattering (SAXS) data. It provides a user-friendly interface to perform common SAXS analyses and refine structural models against experimental data using PEPSI-SAXS.

## Features

- **Data Upload:** Upload SAXS curves (.dat), protein sequences (.fasta), and structures (.pdb/.cif).
- **Database Fetch:** Fetch structural models directly from the PDB or AlphaFold Database.
- **Automated Analysis:** Automatic calculation of Guinier fit, P(r) distribution, and Kratky plots.
- **Interactive Refinement:** Integrated PEPSI-SAXS for rigid-body and flexible model refinement.
- **Rich Visualization:** Interactive plots and 3D molecular viewers.

---

## Installation

### From Pypi

```bash
# Create and activate a virtual environment (or use conda)
python3 -m venv .venv
source .venv/bin/activate

# Install
pip install -e saxsmart
```

### From source

```bash
# Clone your repository
git clone https://gitlab.esrf.fr/hayden5a/saxsmart.git
cd saxsmart

# Create and activate a virtual environment (or use conda)
python3 -m venv .venv
source .venv/bin/activate

# Install
python -m pip install -U pip
pip install -e .
```

> **Note:** Dependencies are declared in `pyproject.toml`.

---

## Running

After installation, use the console script:

```bash
saxsmart
```

Alternative entry points:

```bash
python -m saxsmart
```

- Dash automatically serves files in the packaged `assets/` directory.
- Example data is bundled under `saxsmart/example_data/`.

---

## Configuration

You can configure paths via environment variables:

- `PEPSI_SAXS_BIN` — Full path to the `pepsi-SAXS` executable (if not on `PATH`).
  ```bash
  export PEPSI_SAXS_BIN=/opt/pepsi/pepsi-SAXS
  ```
- `SAXSMART_CACHE_DIR` — Override the directory for long-callback caching.
  ```bash
  export SAXSMART_CACHE_DIR=/scratch/$USER/saxsmart-cache
  ```
- `SAXSMART_TEMP` — Override the temporary working directory.
  ```bash
  export SAXSMART_TEMP=/scratch/$USER/saxsmart-tmp
  ```

> If `PEPSI-SAXS` is not required for your workflow, related actions will be disabled or produce a friendly error message.

---

## License

MIT (see `LICENSE`).