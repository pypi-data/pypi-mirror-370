export PYPI_TOKEN='pypi-AgEIcHlwaS5vcmcCJDA3NTZhMTE1LTZhMDQtNDMxMC04NTIzLTRlZTdlZjVmODI0ZQACKlszLCJjZjhlNjQzMi1iOTYwLTRiM2YtYWM5MC00Y2E2OWIzMzhjYWEiXQAABiALWd8yYJAfS1EVPrzlOO6bPf_eozcsGdE3a6Rtuj3YJQ'
python -m twine upload \
    -u __token__ \
    -p "$PYPI_TOKEN" \
    dist/*