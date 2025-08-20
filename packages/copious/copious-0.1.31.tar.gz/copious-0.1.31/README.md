# Copious

A handy tool that make your day to day programming much easier. 

The name comes from the latin word cornucopia.

## Development

Install dev deps:

```bash
pip install -r requirements.txt
```

### Minimal dependency set (lowest supported versions)

To compute and validate the lowest compatible versions of runtime dependencies:

```bash
# Generate constraints/requirements-min.txt using uv (preferred)
bash scripts/generate_min_requirements.sh

# Install runtime deps with the minimal constraints and run tests
pip install -r requirements.runtime.in -c constraints/requirements-min.txt
pip install -e .
pytest -q
```

Notes:
- Floors for Python 3.10 are in `constraints/floors-py310.txt` to avoid ancient, incompatible packages. Adjust per Python version if needed.
- CI runs tests against latest and the minimal set to ensure ongoing compatibility.
