# Releasing the CLI
1. Publish to PyPI
2. Update asyncy/homebrew-brew

## Publishing to PyPI
1. Ensure creds are present in ~/.pypirc
```
[distutils]
index-servers =
    pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = foo
password = bar
```
2. Run `python setup.py sdist`
3. Run `twine upload dist/asyncy-X.X.X.tar.gz` (if you don't have twine, run `pip install twine`)

## Updating asyncy/homebrew-brew
TODO
