---
icon: material/cog-box
---

# :material-cog-box: Installation & Setup

## Requirements

EasyDiffraction is a cross-platform Python library compatible with **Python 3.10
through 3.12**.  
Make sure Python is installed on your system before proceeding with the
installation.

## Environment Setup <small>optional</small> { #environment-setup data-toc-label="Environment Setup" }

We recommend using a **virtual environment** to isolate dependencies and avoid
conflicts with system-wide packages. If any issues arise, you can simply delete
and recreate the environment.

#### Creating and Activating a Virtual Environment:

- Create a new virtual environment:
  ```console
  python3 -m venv venv
  ```

<!-- prettier-ignore-start -->

- Activate the environment:

    === ":material-apple: macOS"
        ```console
        . venv/bin/activate
        ```
    === ":material-linux: Linux"
        ```console
        . venv/bin/activate
        ```
    === ":fontawesome-brands-windows: Windows"
        ```console
        . venv/Scripts/activate      # Windows with Unix-like shells
        .\venv\Scripts\activate.bat  # Windows with CMD
        .\venv\Scripts\activate.ps1  # Windows with PowerShell
        ```

<!-- prettier-ignore-end -->

- The terminal should now show `(venv)`, indicating that the virtual environment
  is active.

#### Deactivating and Removing the Virtual Environment:

- Exit the environment:
  ```console
  deactivate
  ```

<!-- prettier-ignore-start -->

- If this environment is no longer needed, delete it:

    === ":material-apple: macOS"
        ```console
        rm -rf venv
        ```
    === ":material-linux: Linux"
        ```console
        rm -rf venv
        ```
    === ":fontawesome-brands-windows: Windows"
        ```console
        rmdir /s /q venv
        ```

<!-- prettier-ignore-end -->

## Installation Guide

### Installing from PyPI <small>recommended</small> { #from-pypi data-toc-label="Installing from PyPI" }

EasyDiffraction is available on **PyPI (Python Package Index)** and can be
installed using `pip`. We strongly recommend installing it within a virtual
environment, as described in the [Environment Setup](#environment-setup)
section.

We recommend installing the latest release of EasyDiffraction with the
`visualization` extras, which include optional dependencies used for simplified
visualization of charts and tables. This can be especially useful for running
the Jupyter Notebook examples. To do so, use the following command:

```console
pip install 'easydiffraction[visualization]'
```

If only the core functionality is needed, the library can be installed simply
with:

```console
pip install easydiffraction
```

To install a specific version of EasyDiffraction, e.g., 1.0.3:

```console
pip install 'easydiffraction==1.0.3'
```

To upgrade to the latest version:

```console
pip install --upgrade --force-reinstall easydiffraction
```

To check the installed version:

```console
pip show easydiffraction
```

### Installing from GitHub

Installing unreleased versions is generally not recommended but may be useful
for testing.

To install EasyDiffraction from, e.g., the `develop` branch of GitHub:

```console
pip install git+https://github.com/easyscience/diffraction-lib@develop
```

To include extra dependencies (e.g., visualization):

```console
pip install 'easydiffraction[visualization] @ git+https://github.com/easyscience/diffraction-lib@develop'
```

## How to Run Tutorials

EasyDiffraction includes a collection of **Jupyter Notebook examples** that
demonstrate key functionality. These tutorials serve as **step-by-step guides**
to help users understand the diffraction data analysis workflow.

They are available as **static HTML pages** in the
[:material-school: Tutorials](../tutorials/index.md) section. You can also run
them interactively in two ways:

- **Run Locally** – Download the notebook via the :material-download:
  **Download** button and run it on your computer.
- **Run Online** – Use the :google-colab: **Open in Google Colab** button to run
  the tutorial directly in your browser (no setup required).

!!! note

    You can also download all Jupyter notebooks at once as a zip archive from the
    [EasyDiffraction Releases](https://github.com/easyscience/diffraction-lib/releases/latest).

### Run Tutorials Locally

To run tutorials locally, install **Jupyter Notebook** or **JupyterLab**. Here
are the steps to follow in the case of **Jupyter Notebook**:

- Install Jupyter Notebook:
  ```console
  pip install notebook
  ```
- Download the latest EasyDiffraction tutorial examples from GitHub, e.g., using
  curl:
  ```console
  curl --location --remote-name https://github.com/easyscience/diffraction-lib/releases/latest/download/examples.zip
  ```
- Unzip the archive:
  ```console
  unzip examples.zip
  ```
- Launch the Jupyter Notebook server in the `examples/` directory:
  ```console
  jupyter notebook examples/
  ```
- In your web browser, go to:
  ```console
  http://localhost:8888/
  ```
- Open one of the `*.ipynb` files.

### Run Tutorials via Google Colab

**Google Colab** lets you run Jupyter Notebooks in the cloud without any local
installation.

To use Google Colab:

- Ensure you have a **Google account**.
- Go to the **[:material-school: Tutorials](../tutorials/index.md)** section.
- Click the :google-colab: **Open in Google Colab** button on any tutorial.

This is the fastest way to start experimenting with EasyDiffraction, without
setting up Python on your system.
