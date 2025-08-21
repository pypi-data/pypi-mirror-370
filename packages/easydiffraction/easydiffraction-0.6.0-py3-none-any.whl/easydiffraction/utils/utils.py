# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

"""
General utilities and helpers for easydiffraction.
"""

import importlib
import os
import re
from typing import List

import numpy as np
import pandas as pd
import pooch
from tabulate import tabulate

try:
    import IPython
    from IPython.display import HTML
    from IPython.display import display
except ImportError:
    IPython = None

from easydiffraction.utils.formatting import warning

# Single source of truth for the data repository branch.
# This can be overridden in CI or development environments.
DATA_REPO_BRANCH = (
    os.environ.get('CI_BRANCH')  # CI/dev override
    or 'master'  # Default branch for the data repository
)


def download_from_repository(
    file_name: str,
    branch: str | None = None,
    destination: str = 'data',
    overwrite: bool = False,
) -> None:
    """Download a data file from the EasyDiffraction repository on GitHub.

    Args:
        file_name: The file name to fetch (e.g., "NaCl.gr").
        branch: Branch to fetch from. If None, uses DATA_REPO_BRANCH.
        destination: Directory to save the file into (created if missing).
        overwrite: Whether to overwrite the file if it already exists. Defaults to False.
    """
    file_path = os.path.join(destination, file_name)
    if os.path.exists(file_path):
        if not overwrite:
            print(warning(f"File '{file_path}' already exists and will not be overwritten."))
            return
        else:
            print(warning(f"File '{file_path}' already exists and will be overwritten."))
            os.remove(file_path)

    base = 'https://raw.githubusercontent.com'
    org = 'easyscience'
    repo = 'diffraction-lib'
    branch = branch or DATA_REPO_BRANCH  # Use the global branch variable if not provided
    path_in_repo = 'tutorials/data'
    url = f'{base}/{org}/{repo}/refs/heads/{branch}/{path_in_repo}/{file_name}'

    pooch.retrieve(
        url=url,
        known_hash=None,
        fname=file_name,
        path=destination,
    )


def is_notebook() -> bool:
    """
    Determines if the current environment is a Jupyter Notebook.

    Returns:
        bool: True if running inside a Jupyter Notebook, False otherwise.
    """
    if IPython is None:
        return False

    if is_pycharm():  # Running inside PyCharm
        return True
    elif is_colab():  # Running inside Google Colab
        return True

    try:
        shell = get_ipython().__class__.__name__  # noqa: F821
        if shell == 'ZMQInteractiveShell':  # Jupyter notebook or qtconsole
            return True
        elif shell == 'TerminalInteractiveShell':  # Terminal running IPython
            return False
        else:  # Other type (unlikely)
            return False
    except NameError:
        return False  # Probably standard Python interpreter


def is_pycharm() -> bool:
    """
    Determines if the current environment is PyCharm.

    Returns:
        bool: True if running inside PyCharm, False otherwise.
    """
    return os.environ.get('PYCHARM_HOSTED') == '1'


def is_colab() -> bool:
    """
    Determines if the current environment is Google Colab.

    Returns:
        bool: True if running in Google Colab PyCharm, False otherwise.
    """
    try:
        return importlib.util.find_spec('google.colab') is not None
    except ModuleNotFoundError:
        return False


def is_github_ci() -> bool:
    """
    Determines if the current process is running in GitHub Actions CI.

    Returns:
        bool: True if the environment variable ``GITHUB_ACTIONS`` is set
        (Always "true" on GitHub Actions), False otherwise.
    """
    return os.environ.get('GITHUB_ACTIONS') is not None


def render_table(
    columns_data,
    columns_alignment,
    columns_headers=None,
    show_index=False,
    display_handle=None,
):
    """
    Renders a table either as an HTML (in Jupyter Notebook) or ASCII (in terminal),
    with aligned columns.

    Args:
        columns_data (list): List of lists, where each inner list represents a row of data.
        columns_alignment (list): Corresponding text alignment for each column (e.g., 'left', 'center', 'right').
        columns_headers (list): List of column headers.
        show_index (bool): Whether to show the index column.
    """

    # Use pandas DataFrame for Jupyter Notebook rendering
    if is_notebook():
        # Create DataFrame
        if columns_headers is None:
            df = pd.DataFrame(columns_data)
            df.columns = range(df.shape[1])  # Ensure numeric column labels
            columns_headers = df.columns.tolist()
            skip_headers = True
        else:
            df = pd.DataFrame(columns_data, columns=columns_headers)
            skip_headers = False

        # Force starting index from 1
        if show_index:
            df.index += 1

        # Replace None/NaN values with empty strings
        df.fillna('', inplace=True)

        # Formatters for data cell alignment and replacing None with empty string
        def make_formatter(align):
            return lambda x: f'<div style="text-align: {align};">{x}</div>'

        formatters = {col: make_formatter(align) for col, align in zip(columns_headers, columns_alignment)}

        # Convert DataFrame to HTML
        html = df.to_html(
            escape=False,
            index=show_index,
            formatters=formatters,
            border=0,
            header=not skip_headers,
        )

        # Add inline CSS to align the entire table to the left and show border
        html = html.replace(
            '<table class="dataframe">',
            '<table class="dataframe" '
            'style="'
            'border-collapse: collapse; '
            'border: 1px solid #515155; '
            'margin-left: 0.5em;'
            'margin-top: 0.5em;'
            'margin-bottom: 1em;'
            '">',
        )

        # Manually apply text alignment to headers
        if not skip_headers:
            for col, align in zip(columns_headers, columns_alignment):
                html = html.replace(f'<th>{col}', f'<th style="text-align: {align};">{col}')

        # Display or update the table in Jupyter Notebook
        if display_handle is not None:
            display_handle.update(HTML(html))
        else:
            display(HTML(html))

    # Use tabulate for terminal rendering
    else:
        if columns_headers is None:
            columns_headers = []

        indices = show_index
        if show_index:
            # Force starting index from 1
            indices = range(1, len(columns_data) + 1)

        table = tabulate(
            columns_data,
            headers=columns_headers,
            tablefmt='fancy_outline',
            numalign='left',
            stralign='left',
            showindex=indices,
        )

        print(table)


def render_cif(cif_text, paragraph_title) -> None:
    """
    Display the CIF text as a formatted table in Jupyter Notebook or terminal.
    """
    # Split into lines and replace empty ones with a '&nbsp;'
    # (non-breaking space) to force empty lines to be rendered in
    # full height in the table. This is only needed in Jupyter Notebook.
    if is_notebook():
        lines: List[str] = [line if line.strip() else '&nbsp;' for line in cif_text.splitlines()]
    else:
        lines: List[str] = [line for line in cif_text.splitlines()]

    # Convert each line into a single-column format for table rendering
    columns: List[List[str]] = [[line] for line in lines]

    # Print title paragraph
    print(paragraph_title)

    # Render the table using left alignment and no headers
    render_table(columns_data=columns, columns_alignment=['left'])


def tof_to_d(
    tof: np.ndarray,
    offset: float,
    linear: float,
    quad: float,
    quad_eps=1e-20,
) -> np.ndarray:
    """Convert time-of-flight (TOF) to d-spacing using a quadratic calibration.

    Model:
        TOF = offset + linear * d + quad * d²

    The function:
      - Uses a linear fallback when the quadratic term is effectively zero.
      - Solves the quadratic for d and selects the smallest positive, finite root.
      - Returns NaN where no valid solution exists.
      - Expects ``tof`` as a NumPy array; output matches its shape.

    Args:
        tof (np.ndarray): Time-of-flight values (µs). Must be a NumPy array.
        offset (float): Calibration offset (µs).
        linear (float): Linear calibration coefficient (µs/Å).
        quad (float): Quadratic calibration coefficient (µs/Å²).
        quad_eps (float, optional): Threshold to treat ``quad`` as zero. Defaults to 1e-20.

    Returns:
        np.ndarray: d-spacing values (Å), NaN where invalid.

    Raises:
        TypeError: If ``tof`` is not a NumPy array or coefficients are not real numbers.
    """
    # Type checks
    if not isinstance(tof, np.ndarray):
        raise TypeError(f"'tof' must be a NumPy array, got {type(tof).__name__}")
    for name, val in (('offset', offset), ('linear', linear), ('quad', quad), ('quad_eps', quad_eps)):
        if not isinstance(val, (int, float, np.integer, np.floating)):
            raise TypeError(f"'{name}' must be a real number, got {type(val).__name__}")

    # Output initialized to NaN
    d_out = np.full_like(tof, np.nan, dtype=float)

    # 1) If quadratic term is effectively zero, use linear formula:
    #    TOF ≈ offset + linear * d =>
    #    d ≈ (tof - offset) / linear
    if abs(quad) < quad_eps:
        if linear != 0.0:
            d = (tof - offset) / linear
            # Keep only positive, finite results
            valid = np.isfinite(d) & (d > 0)
            d_out[valid] = d[valid]
        # If B == 0 too, there's no solution; leave NaN
        return d_out

    # 2) If quadratic term is significant, solve the quadratic equation:
    #    TOF = offset + linear * d + quad * d² =>
    #    quad * d² + linear * d + (offset - tof) = 0
    discr = linear**2 - 4 * quad * (offset - tof)
    has_real_roots = discr >= 0

    if np.any(has_real_roots):
        sqrt_discr = np.sqrt(discr[has_real_roots])

        root_1 = (-linear + sqrt_discr) / (2 * quad)
        root_2 = (-linear - sqrt_discr) / (2 * quad)

        # Pick smallest positive, finite root per element
        roots = np.stack((root_1, root_2), axis=0)  # Stack roots for comparison
        roots = np.where(np.isfinite(roots) & (roots > 0), roots, np.nan)  # Replace non-finite or negative roots with NaN
        chosen = np.nanmin(roots, axis=0)  # Choose the smallest positive root or NaN if none are valid

        d_out[has_real_roots] = chosen

    return d_out


def twotheta_to_d(twotheta, wavelength):
    """
    Convert 2-theta to d-spacing using Bragg's law.

    Parameters:
        twotheta (float or np.ndarray): 2-theta angle in degrees.
        wavelength (float): Wavelength in Å.

    Returns:
        d (float or np.ndarray): d-spacing in Å.
    """
    # Convert twotheta from degrees to radians
    theta_rad = np.radians(twotheta / 2)

    # Calculate d-spacing using Bragg's law
    d = wavelength / (2 * np.sin(theta_rad))

    return d


def get_value_from_xye_header(file_path, key):
    """
    Extracts a floating point value from the first line of the file, corresponding to the given key.

    Parameters:
        file_path (str): Path to the input file.
        key (str): The key to extract ('DIFC' or 'two_theta').

    Returns:
        float: The extracted value.

    Raises:
        ValueError: If the key is not found.
    """
    pattern = rf'{key}\s*=\s*([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)'

    with open(file_path, 'r') as f:
        first_line = f.readline()

    match = re.search(pattern, first_line)
    if match:
        return float(match.group(1))
    else:
        raise ValueError(f'{key} not found in the header.')
