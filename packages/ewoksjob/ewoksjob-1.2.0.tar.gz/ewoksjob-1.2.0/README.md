# ewoksjob

Utilities for job scheduling of [ewoks](https://ewoks.readthedocs.io/) workflows.

Ewoksjob provides an ewoks interface for asynchronous and distributed scheduling of [ewoks](https://ewoks.readthedocs.io/) from python.

Note that *ewoksjob* distributes the execution of workflows while [ewoksdask](https://ewoks.readthedocs.io/)
distributes the execution of tasks in a workflow. So in the context of workflows, job scheduling exists on two levels.

The primary clients that need to schedule workflows are
* [Ewoksserver](https://gitlab.esrf.fr/workflow/ewoks/ewoksserver): web backend for ewoks.
* [Bliss](https://gitlab.esrf.fr/bliss/bliss): the ESRF beamline control system.
* [Daiquiri](https://gitlab.esrf.fr/ui/daiquiri): web backend for Bliss.

## Installation

Install on the client side

```bash
pip install ewoksjob
```

Install on the worker side

```bash
pip install ewoksjob[worker]
```

## Getting started

Start a worker pool that can execute ewoks graphs

```bash
ewoksjob worker
```

Start a workflow on the client side

```python
from ewoksjob.client import submit

workflow = {"graph": {"id": "mygraph"}}
future = submit(args=(workflow,))
result = future.result(timeout=None)
```

Note that both environments need to be able to import `celeryconfig` which
contains celery configuration (mainly the message broker and result backend URL's).

## Hello world example

Clone the git repository and start a worker pool

```bash
scripts/worker.sh --sql
```

Submit workflows

```bash
scripts/runjobs.sh --sql
```

## Tests

```bash
pytest --pyargs ewoksjob
```

To run the redis tests you need `redis-server` (e.g. `conda install redis-server`).

## Documentation

https://ewoksjob.readthedocs.io/
