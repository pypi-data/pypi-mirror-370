# 📦 Uploading Skimly Python Package to PyPI

## Prerequisites

1. **PyPI Account**: You need a PyPI account at https://pypi.org/account/register/
2. **API Token**: Generate an API token at https://pypi.org/manage/account/token/

## Setup

1. **Edit `.pypirc` file**:
   ```bash
   # Replace pypi-YOUR_API_TOKEN_HERE with your actual token
   nano .pypirc
   ```

2. **Your `.pypirc` should look like**:
   ```ini
   [distutils]
   index-servers =
       pypi
       testpypi

   [pypi]
   repository = https://upload.pypi.org/legacy/
   username = __token__
   password = pypi-AgEIcHlwaS5vcmcCJDk2YTdlOWYyLWI0ODAtNGJlMC05ZTg3LTJlM2RiMmZkMzNhMQACDlsxLFsic2tpbWx5Il1dAAIsWzIsWyJjNDU1Mzc3ZS1iYWNkLTRiN2ItODMxNS1jYzIzNzdiZTZkZWMiXV0AAAYgGWXlk41kQ4tOXU9VRClAVSg2GkDIsYtJ-GWahlKZNBspython
   ```

## Upload Methods

### Method 1: Automated Script (Recommended)
```bash
./upload_to_pypi.sh
```

### Method 2: Manual Commands
```bash
# Build the package
python -m build

# Check package validity
python -m twine check dist/*

# Upload to PyPI
python -m twine upload dist/*
```

## What Gets Uploaded

- **Source Distribution**: `skimly-0.1.1.tar.gz`
- **Wheel Distribution**: `skimly-0.1.1-py3-none-any.whl`

## Verification

After upload, verify at:
- https://pypi.org/project/skimly/
- https://pypi.org/project/skimly/0.1.1/

## Installation Test

```bash
pip install --upgrade skimly
python -c "from skimly import SkimlyClient; print('✅ Package installed successfully!')"
```

## Troubleshooting

- **403 Forbidden**: Check your API token in `.pypirc`
- **Authentication Failed**: Ensure token starts with `pypi-`
- **Package Already Exists**: Increment version in `pyproject.toml`

## Next Steps

After successful upload:
1. Update documentation to reflect new version
2. Tag the release in git: `git tag v0.1.1`
3. Push tags: `git push --tags`
