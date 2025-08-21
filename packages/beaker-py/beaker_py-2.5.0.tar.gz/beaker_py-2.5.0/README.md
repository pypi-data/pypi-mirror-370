# Beaker-py [![](https://img.shields.io/pypi/v/beaker-py)](https://pypi.org/project/beaker-py/)

A lightweight pure-Python client for Beaker.

## Quick Links

- 📝 Docs and examples:
  - [API docs](https://beaker-py-docs.allen.ai/)
  - [Integration test examples](https://github.com/allenai/beaker/tree/main/bindings/python/src/integration_tests)
  - [v1 → v2 migration guide](https://github.com/allenai/beaker/blob/main/bindings/python/MIGRATION_GUIDE.md)
- 🌍 Ecosystem:
  - [beaker-gantry](https://github.com/allenai/beaker-gantry)
  - [beaker-run-action](https://github.com/allenai/beaker-run-action)

## Installing

### Installing with `pip`

**beaker-py** is available [on PyPI](https://pypi.org/project/beaker-py/). Just run

```bash
pip install beaker-py
```

### Installing from source

To install **beaker-py** from source, first clone [the repository](https://github.com/allenai/beaker):

```bash
git clone https://github.com/allenai/beaker.git
```

Then create or activate a Python virtual environment, and run:

```bash
cd beaker/bindings/python
make dev-install
```

## Quick start

If you've already configured the [Beaker command-line client](https://github.com/allenai/beaker/),
**beaker-py** will find and use the existing configuration file (usually located at `$HOME/.beaker/config.yml`) or `BEAKER_TOKEN` environment variable.

Then you can instantiate the Beaker client with the `.from_env()` class method:

```python
from beaker import Beaker

with Beaker.from_env() as beaker:
    ...
```

With the Python client, you can:

- Query [**Clusters**](https://beaker-docs.apps.allenai.org/concept/clusters.html) with `beaker.cluster.*` methods. For example:

  ```python
  beaker.cluster.get("ai2/jupiter-cirrascale-2")
  ```

- Manage [**Datasets**](https://beaker-docs.apps.allenai.org/concept/datasets.html) with `beaker.dataset.*` methods. For example:

  ```python
  beaker.dataset.create(dataset_name, source_dir)
  ```

- Manage [**Experiments**](https://beaker-docs.apps.allenai.org/concept/experiments.html) with `beaker.experiment.*` and `beaker.workload.*` methods. For example:

  ```python
  beaker.experiment.create(spec=spec, name=name)
  ```

- Manage [**Groups**](https://beaker-docs.apps.allenai.org/concept/groups.html) with `beaker.group.*` methods. For example:

  ```python
  beaker.group.create(name)
  ```

- Manage [**Images**](https://beaker-docs.apps.allenai.org/concept/images.html) with `beaker.image.*` methods. For example:

  ```python
  beaker.image.update(image, name=name)
  ```

- Manage [**Secrets**](https://beaker-docs.apps.allenai.org/concept/secrets.html) with `beaker.secret.*` methods. For example:

  ```python
  beaker.secret.write(name, value)
  ```

- Manage [**Workspaces**](https://beaker-docs.apps.allenai.org/concept/workspaces.html) with `beaker.workspace.*` methods. For example:

  ```python
  beaker.workspace.create("ai2/new_workspace")
  ```

- Track **Jobs** with `beaker.job.*` methods. For example:

  ```python
  beaker.job.logs(job, follow=True)
  ```

- Create and process [**Queues**](https://beaker-docs.apps.allenai.org/concept/queues.html) with `beaker.queue.*` methods. For example:

  ```python
  beaker.queue.create("my-work-queue", batch_size=4)
  ```

If you're coming from [v1 of beaker-py](https://github.com/allenai/beaker-py), consider reading the [migration guide](https://github.com/allenai/beaker/blob/main/bindings/python/MIGRATION_GUIDE.md).

### Example workflow

Launch and follow an experiment like [beaker-gantry](https://github.com/allenai/beaker-gantry) does:

```python
import time
from beaker import Beaker, BeakerExperimentSpec, BeakerJobPriority


with Beaker.from_env() as beaker:
    # Build experiment spec...
    spec = BeakerExperimentSpec.new(
        description="beaker-py test run",
        beaker_image="petew/hello-world",
        priority=BeakerJobPriority.low,
        preemptible=True,
    )

    # Create experiment workload...
    workload = beaker.experiment.create(spec=spec)

    # Wait for job to be created...
    while (job := beaker.workload.get_latest_job(workload)) is None:
        print("waiting for job to start...")
        time.sleep(1.0)

    # Follow logs...
    print("Job logs:")
    for job_log in beaker.job.logs(job, follow=True):
        print(job_log.message.decode())
```

See the [integration tests](https://github.com/allenai/beaker/tree/main/bindings/python/src/integration_tests) for more examples.

## Development

After [installing from source](#installing-from-source), you can run checks and tests locally with:

```bash
make checks
```

### Releases

At the moment releases need to be published manually by following these steps:

1. Ensure you've authenticated with [PyPI](https://pypi.org/) through a `~/.pypirc` file and have write permissions to the [beaker-py project](https://pypi.org/project/beaker-py/).
2. Ensure the target release version defined in `src/beaker/version.py` is correct, or change the version on the fly by adding the `Make` argument `BEAKER_PY_VERSION=X.X.X` to the command in the next step.
3. Ensure the CHANGELOG.md has a section at the top for the new release (`## vX.X.X - %Y-%m-%d`).
4. Run `make publish` for a stable release or `make publish-nightly` for a nightly pre-release.
