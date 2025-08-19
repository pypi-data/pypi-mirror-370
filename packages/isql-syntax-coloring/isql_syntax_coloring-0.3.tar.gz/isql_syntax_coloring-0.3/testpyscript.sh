export TEST_PYPI_TOKEN='pypi-AgENdGVzdC5weXBpLm9yZwIkZTQ4OWY2MjUtZjcyZC00MzNhLTg2NTMtNDhjMjBmYjE1YWM4AAIqWzMsImQ0OTQ1NmNkLWRhMjItNDNjMS1hMmIyLTQ4NzQ2ZDg1ZTEzMCJdAAAGIEI4m0qkT2RxFSBk2vlxgThbkG-omF7XNPiROKU4IuS2'

# 2 · Upload just the freshly‑built files in dist/
python -m twine upload \
        --repository-url https://test.pypi.org/legacy/ \
        -u __token__ -p "$TEST_PYPI_TOKEN" \
        dist/*