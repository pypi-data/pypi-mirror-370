# Publishing Guide for mssql_mcp_server_ishaan

## Package Information
- **Package Name**: `mssql_mcp_server_ishaan`
- **Version**: 0.1.0
- **Author**: Ishaan
- **Built Files**: 
  - `mssql_mcp_server_ishaan-0.1.0.tar.gz` (source distribution)
  - `mssql_mcp_server_ishaan-0.1.0-py3-none-any.whl` (wheel distribution)

## Prerequisites

1. **Create PyPI Account**: 
   - Go to https://pypi.org/account/register/
   - Create an account and verify your email

2. **Create TestPyPI Account** (recommended for testing):
   - Go to https://test.pypi.org/account/register/
   - Create an account and verify your email

3. **Generate API Tokens**:
   - For PyPI: Go to https://pypi.org/manage/account/token/
   - For TestPyPI: Go to https://test.pypi.org/manage/account/token/
   - Create tokens with "Entire account" scope

## Publishing Steps

### Step 1: Test on TestPyPI (Recommended)

```bash
# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip3 install --index-url https://test.pypi.org/simple/ mssql_mcp_server_ishaan
```

### Step 2: Publish to PyPI

```bash
# Upload to PyPI
twine upload dist/*
```

### Step 3: Verify Installation

```bash
# Install from PyPI
pip3 install mssql_mcp_server_ishaan

# Test the installation
python3 -c "import mssql_mcp_server_ishaan; print('Package imported successfully!')"
```

## Authentication

When running `twine upload`, you'll be prompted for:
- **Username**: `__token__`
- **Password**: Your API token (starts with `pypi-`)

Alternatively, you can configure authentication in `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-testpypi-api-token-here
```

## Usage After Installation

Once published and installed, users can:

1. **Install the package**:
   ```bash
   pip3 install mssql_mcp_server_ishaan
   ```

2. **Run as a module**:
   ```bash
   python3 -m mssql_mcp_server_ishaan
   ```

3. **Use the command-line script**:
   ```bash
   mssql_mcp_server_ishaan
   ```

4. **Configure in Claude Desktop** (update `claude_desktop_config.json`):
   ```json
   {
     "mcpServers": {
       "mssql": {
         "command": "python3",
         "args": ["-m", "mssql_mcp_server_ishaan"],
         "env": {
           "MSSQL_CONNECTION_STRING": "your-connection-string"
         }
       }
     }
   }
   ```

## Updating the Package

To release a new version:

1. Update the version in `pyproject.toml`
2. Run the build script: `python3 setup_package.py`
3. Upload the new version: `twine upload dist/*`

## Troubleshooting

- **403 Forbidden**: Check your API token and permissions
- **400 Bad Request**: Package name might already exist or have invalid metadata
- **File already exists**: You're trying to upload a version that already exists

## Notes

- Package names on PyPI are case-insensitive and treat hyphens/underscores as equivalent
- Once uploaded, you cannot delete or modify a release (you can only "yank" it)
- Consider using semantic versioning (e.g., 0.1.0, 0.1.1, 0.2.0)
