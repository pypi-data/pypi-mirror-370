export PYPI_TOKEN='pypi-AgEIcHlwaS5vcmcCJDFmM2E0YmQ5LTI5NTAtNDM0Mi1hZmRmLTZlOWJiNjlmN2NiOQACKlszLCJjZjhlNjQzMi1iOTYwLTRiM2YtYWM5MC00Y2E2OWIzMzhjYWEiXQAABiAodWQJBLLjVbkJq4pY1h7YlQrpIytU1zEceiIRxdvDtg'
python -m twine upload \
    -u __token__ \
    -p "$PYPI_TOKEN" \
    dist/*