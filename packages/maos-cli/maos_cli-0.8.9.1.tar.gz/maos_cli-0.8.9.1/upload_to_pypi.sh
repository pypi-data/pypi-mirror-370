#!/bin/bash
# Upload MAOS to PyPI

cd "/Users/vincentsider/2-Projects/1-KEY PROJECTS/MOAS"

# Upload to PyPI
# Replace YOUR_TOKEN with the token you just copied
python3 -m twine upload dist/* \
  --username __token__ \
  --password pypi-AgEIcHlwaS5vcmcC... # <-- PASTE YOUR FULL TOKEN HERE

# Or you can run interactively and paste when prompted:
# python3 -m twine upload dist/*
# Username: __token__
# Password: [paste token]