# Upload MAOS v0.1.1 to PyPI

You need to run this command manually in your terminal:

```bash
cd "/Users/vincentsider/2-Projects/1-KEY PROJECTS/MOAS"
python3 -m twine upload dist/*
```

When prompted:
- **Username:** `__token__`
- **Password:** [paste your PyPI token that starts with `pypi-`]

## What's fixed in v0.1.1:
- Fixed import error: changed `from src.storage...` to `from maos.storage...`
- This fixes the ModuleNotFoundError when running `maos --version`

## After uploading:
1. Wait 1-2 minutes for PyPI to update
2. Upgrade your installation: `pipx upgrade maos-cli`
3. Test it works: `maos --version`

The files ready to upload:
- `dist/maos_cli-0.1.1-py3-none-any.whl`
- `dist/maos_cli-0.1.1.tar.gz`