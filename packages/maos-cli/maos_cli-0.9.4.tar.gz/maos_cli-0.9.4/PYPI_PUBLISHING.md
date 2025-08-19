# Publishing MAOS-CLI to PyPI

## ✅ Completed Steps

1. **Package name verified**: `maos-cli` is available on PyPI
2. **Metadata updated**: pyproject.toml configured with proper info
3. **MANIFEST.in created**: Includes necessary files
4. **LICENSE added**: MIT License
5. **Build tools installed**: `build` and `twine` packages
6. **Distribution built**: Created wheel and source distribution

## 📦 Built Packages

Your distribution packages are ready in the `dist/` directory:
- `maos_cli-0.1.0-py3-none-any.whl` (205 KB) - Wheel distribution
- `maos_cli-0.1.0.tar.gz` (801 KB) - Source distribution

## 🚀 Next Steps to Publish

### Step 1: Create PyPI Account

1. Go to https://pypi.org/account/register/
2. Create your account
3. Verify your email
4. **IMPORTANT**: Enable 2FA (Two-Factor Authentication) - PyPI requires this!

### Step 2: Create API Token

1. Go to https://pypi.org/manage/account/token/
2. Create a new API token
3. Set scope to "Entire account" (for first upload)
4. **Save the token securely** - you'll only see it once!

The token will look like: `pypi-AgEIcHlwaS5vcmcCJGE4ZjY5YzQ3LTg4...`

### Step 3: Test with TestPyPI (Optional but Recommended)

TestPyPI is a separate instance for testing:

```bash
# Upload to TestPyPI first
python3 -m twine upload --repository testpypi dist/*

# When prompted:
# Username: __token__
# Password: [paste your TestPyPI token]

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ maos-cli
```

### Step 4: Upload to Production PyPI

```bash
# Upload to PyPI
cd "/Users/vincentsider/2-Projects/1-KEY PROJECTS/MOAS"
python3 -m twine upload dist/*

# When prompted:
# Username: __token__
# Password: [paste your PyPI API token starting with pypi-]
```

Or use the token directly:

```bash
python3 -m twine upload dist/* -u __token__ -p pypi-YOUR-API-TOKEN-HERE
```

### Step 5: Verify Installation

After successful upload (takes a few minutes to propagate):

```bash
# Install from PyPI
pipx install maos-cli

# Verify it works
maos --version
```

## 🔐 Security Best Practices

### Option A: Use keyring (Recommended)

```bash
# Store credentials securely
python3 -m keyring set https://upload.pypi.org/legacy/ __token__
# Enter your PyPI token when prompted

# Now upload without entering credentials
python3 -m twine upload dist/*
```

### Option B: Use .pypirc file

Create `~/.pypirc` with proper permissions:

```bash
cat > ~/.pypirc << EOF
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-TOKEN-HERE

[testpypi]
username = __token__
password = pypi-YOUR-TEST-TOKEN-HERE
EOF

# Set proper permissions
chmod 600 ~/.pypirc

# Now you can upload with:
python3 -m twine upload dist/*
```

## 📋 Pre-Upload Checklist

- [x] Package name available: `maos-cli`
- [x] Version set: `0.1.0`
- [x] Description clear and concise
- [x] README.md included for long description
- [x] LICENSE file present (MIT)
- [x] Python version requirement: `>=3.11`
- [x] Dependencies minimal (only essential ones)
- [x] Author info correct: Vincent Sider
- [x] URLs point to correct GitHub repo

## 🎉 After Publishing

1. **Your package page**: https://pypi.org/project/maos-cli/
2. **Update README**: Add PyPI badge and installation instructions
3. **Create GitHub Release**: Tag v0.1.0
4. **Announce**: Share on social media, Reddit, HackerNews, etc.

## 📈 Future Updates

To release a new version:

1. Update version in `pyproject.toml`
2. Clean old builds: `rm -rf dist/ build/`
3. Build new version: `python3 -m build`
4. Upload: `python3 -m twine upload dist/*`

## 🆘 Troubleshooting

### "Invalid or non-existent authentication"
- Make sure to use `__token__` as username (with underscores)
- Token must start with `pypi-`

### "Package already exists"
- The name is taken or you already uploaded this version
- Increment version number in pyproject.toml

### "Invalid metadata"
- Run `python3 -m twine check dist/*` to validate
- Fix any issues in pyproject.toml

## 📚 Resources

- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [PyPI Help](https://pypi.org/help/)
- [TestPyPI](https://test.pypi.org/)