# Development

This is an example of a workflow that describes the development process.

- Clone EasyDiffraction library repository
  ```bash
  git clone https://github.com/easyscience/diffraction-lib
  ```
- Go to the cloned directory
  ```bash
  cd diffraction-lib
  ```
- Checkout/switch to the `develop` branch
  ```bash
  git checkout develop
  ```
- Create a new branch from the current one
  ```bash
  git checkout -b new-feature
  ```
- Create Python environment and activate it
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- Upgrade PIP - package installer for Python
  ```bash
  python -m pip install --upgrade pip
  ```
- Install easydiffraction from root with `dev` extras for development,
  `visualization` extras for Jupyter notebooks and `docs` extras for building
  documentation
  ```bash
  pip install '.[dev,visualization,docs]'
  ```
- Install pycrysfml (pyenv python 3.12, macOS 14, Apple Silicon):
  ```bash
  # Install from local wheel
  pip install deps/pycrysfml-0.1.6-py312-none-macosx_14_0_arm64.whl
  # Try to import the module
  python -c "from pycrysfml import cfml_py_utilities"
  # If previous step failed, check the linked libraries
  otool -L .venv/lib/python3.12/site-packages/pycrysfml/crysfml08lib.so
  # If the library is linked to the wrong Python version, you can fix it with:
  install_name_tool -change `python3-config --prefix`/Python `python3-config --prefix`/lib/libpython3.12.dylib .venv/lib/python3.12/site-packages/pycrysfml/crysfml08lib.so
  # Check again the linked Python library
  otool -L .venv/lib/python3.12/site-packages/pycrysfml/crysfml08lib.so
  # Try to import the module again
  python -c "from pycrysfml import cfml_py_utilities"
  ```
- Install CBLAS library, required for using the Pair Distribution Function
  feature. This step is required only on Windows.
  ```bash
  # Install from the conda-forge channel
  conda install libcblas -c conda-forge
  # Try to import the module
  python -c "import diffpy.pdffit2"
  ```
- Make changes in the code
  ```bash
  ...
  ```
- Check the validity of pyproject.toml
  ```bash
  validate-pyproject pyproject.toml
  ```
- Run Ruff - Python linter and code formatter (configuration is in
  pyproject.toml)<br/> Linting (overwriting files)
  ```bash
  ruff check . --fix
  ```
  Formatting (overwriting files)
  ```bash
  ruff format .
  ```
- Install and run Prettier - code formatter for Markdown, YAML, TOML, etc. files
  (configuration in prettierrc.toml)<br/> Formatting (overwriting files)
  ```bash
  npm install --no-save --no-audit --no-fund 'prettier@>=3.3.3' 'prettier-plugin-toml@>=0.13.0'
  npx prettier . --write --config=prettierrc.toml
  ```
- Run python unit tests
  ```bash
  export PYTHONPATH="$(pwd)/src${PYTHONPATH:+:$PYTHONPATH}"
  python -m pytest tests/unit_tests/ --color=yes
  ```
- Run python functional tests
  ```bash
  export PYTHONPATH="$(pwd)/src${PYTHONPATH:+:$PYTHONPATH}"
  python -m pytest tests/functional_tests/ --color=yes -n auto
  ```
- Run tutorials as python scripts
  ```bash
  export PYTHONPATH="$(pwd)/src${PYTHONPATH:+:$PYTHONPATH}"
  find tutorials/ -name "*.py" | xargs -n 1 -P 0 python
  ```
- Run tutorials/_.py to _.ipynb
  ```bash
  jupytext tutorials/*.py --from py:percent --to ipynb
  nbstripout tutorials/*.ipynb
  ```
- Run tutorials as Jupyter Notebooks
  ```bash
  export PYTHONPATH="$(pwd)/src${PYTHONPATH:+:$PYTHONPATH}"
  python -m pytest --nbmake tutorials/ --nbmake-timeout=600 --color=yes -n auto
  ```
- Add extra files to build documentation (from `../assets-docs/` and
  `../assets-branding/` directories)

  ```bash
  cp -R ../assets-docs/docs/assets/ docs/assets/
  cp -R ../assets-docs/includes/ includes/
  cp -R ../assets-docs/overrides/ overrides/

  mkdir -p docs/assets/images/
  cp ../assets-branding/easydiffraction/hero/dark.png docs/assets/images/hero_dark.png
  cp ../assets-branding/easydiffraction/hero/light.png docs/assets/images/hero_light.png
  cp ../assets-branding/easydiffraction/logos/dark.svg docs/assets/images/logo_dark.svg
  cp ../assets-branding/easydiffraction/logos/light.svg docs/assets/images/logo_light.svg
  cp ../assets-branding/easydiffraction/icons/color.png docs/assets/images/favicon.png

  mkdir -p overrides/.icons/
  cp ../assets-branding/easydiffraction/icons/bw.svg overrides/.icons/easydiffraction.svg
  cp ../assets-branding/easyscience-org/icons/eso-icon_bw.svg overrides/.icons/easyscience.svg

  jupytext tutorials/*.py --from py:percent --to ipynb
  nbstripout tutorials/*.ipynb
  cp tutorials/*.ipynb docs/tutorials/
  cp -R tutorials/data docs/tutorials/

  python tools/create_mkdocs-yml.py
  ```

- Build documentation with MkDocs - static site generator
  ```bash
  export JUPYTER_PLATFORM_DIRS=1
  export PYTHONWARNINGS="ignore::RuntimeWarning"
  export PYTHONPATH="$(pwd)/src${PYTHONPATH:+:$PYTHONPATH}"
  mkdocs serve
  ```
- Test the documentation locally (built in the `site/` directory). E.g., on
  macOS, open the site in the default browser via the terminal
  ```console
  open http://127.0.0.1:8000
  ```
- Clean up after building documentation
  ```console
  rm -rf site/
  rm -rf docs/assets/
  rm -rf docs/tutorials/*.py
  rm -rf docs/tutorials/*.ipynb
  rm -rf includes/
  rm -rf overrides/
  rm -rf node_modules/
  rm mkdocs.yml
  ```
- Commit changes
  ```console
  git add .
  git commit -m "Add new feature"
  ```
- Push the new branch to a remote repository
  ```console
  git push -u origin new-feature
  ```
