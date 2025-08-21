# ewoksxrpd

Workflows for data processing for SAXS/WAXS

## Getting started

Install the [ewoksxrpd](https://ewoksxrpd.readthedocs.io/en/latest/) Python package

```
pip install ewoksxrpd
```
## How to use

Run an example workflow

```bash
python examples/job.py
```

Run an example workflow with GUI

```bash
ewoks execute examples/xrpd_workflow.json --engine=orange --data-root-uri=/tmp --data-scheme nexus
```

or for an installation with the system python

```bash
python3 -m ewoks execute examples/xrpd_workflow.json --engine=orange --data-root-uri=/tmp --data-scheme nexus
```

Produce the example data

```bash
pytest --examples
```

## Documentation

https://ewoksxrpd.readthedocs.io/
