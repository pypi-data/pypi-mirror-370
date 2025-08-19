# ATLAS Rucio policy package

## How to deploy a new version
- Increment the version in `pyproject.toml`
- Go to [Code > Tags](https://gitlab.cern.ch/atlas-adc-ddm/rucio-policy-package/-/tags) and [create a new tag](https://gitlab.cern.ch/atlas-adc-ddm/rucio-policy-package/-/tags/new)
- Name the tag like the version (e.g. `0.6.0`)
- Once the tag has been created, a [deployment pipeline](https://gitlab.cern.ch/atlas-adc-ddm/rucio-policy-package/-/pipelines) will start.
- Check the outcome of the pipeline: if successful, it will provide a link in the logs to the latest policy package version, uploaded to PyPI.

## Resources
- [Rucio documentation for policy packages](https://rucio.github.io/documentation/operator/policy_packages/)
