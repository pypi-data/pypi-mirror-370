# shirotsubaki

This package is being developed to help generate beautiful reports.  
[Documentation](https://shirotsubaki.readthedocs.io/en/latest/)

### Installation (for Users)

#### From PyPI

You can install the release version from [PyPI](https://pypi.org/project/shirotsubaki/).
```
pip install shirotsubaki
```

#### From Local Source Code

If you want to use the latest version that has not been released, clone this repository and install from the local directory.

```
git clone git@github.com:CookieBox26/shirotsubaki.git
cd shirotsubaki
pip install .
```

### Development Guide (for Developers)

Please run the following commands.

```
git clone git@github.com:CookieBox26/shirotsubaki.git
cd shirotsubaki
# make some changes to the code
pytest  # Please test locally
vi docs/reference.md  # Please update documentation
mkdocs serve  # Please preview documentation locally
```
If you have run the command above, you can view the documentation at http://localhost:8000/.  
If you are not an administrator, please open a pull request at this point.

### Build and upload the distribution archives (for administrator only)

Please run the following commands. More details are [here](https://packaging.python.org/en/latest/tutorials/packaging-projects/).

```
pip install --upgrade build
pip install --upgrade twine
pip install --upgrade pkginfo  # This might be needed

python -m build
python -m twine upload dist/*
```
