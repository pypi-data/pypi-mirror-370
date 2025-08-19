![Build Status](https://gitlab.cern.ch/cms-dqmdc/libraries/dials-py/badges/develop/pipeline.svg)
![Coverage](https://gitlab.cern.ch/cms-dqmdc/libraries/dials-py/badges/develop/coverage.svg)
![Latest Release](https://gitlab.cern.ch/cms-dqmdc/libraries/dials-py/-/badges/release.svg)
[![PyPI version](https://badge.fury.io/py/cmsdials.png)](https://badge.fury.io/py/cmsdials)

# dials-py

The Python api client interface to DIALS service.

## Installation

To install dials-py, simply

```bash
$ pip install cmsdials
```

It is also possible to specify the following extras, to enable optional features:

```
pandas, tqdm
```

## Usage

Before interfacing with any route you need to generate valid credentials, it is possible to authenticate trough the `device authorization flow` or using the `client secret key` of any application registered in DIALS. Note that, the device flow is an interactively authentication procedure that is possible to distinguish users in DIALS backend and the client secret flow is not interactive and is not possible to distinguish users so it should only be used for automation scripts.

### Generating credentials with client secret

```python
from cmsdials.auth.secret_key import Credentials

creds = Credentials(token=".....")
```

### Generating credentials with device

#### Loading from AuthClient

```python
from cmsdials.auth.client import AuthClient
from cmsdials.auth.bearer import Credentials

auth = AuthClient()
token = auth.device_auth_flow()
creds = Credentials.from_authclient_token(token)
```

#### Loading from cached credentials file

Credentials are always cached once you authenticate at least one time, calling this method without having a cached credential file will automatically trigger the AuthClient device flow.

```python
from cmsdials.auth.bearer import Credentials

creds = Credentials.from_creds_file()
```

### Basic Example

```python
from cmsdials.auth.bearer import Credentials
from cmsdials import Dials
from cmsdials.filters import LumisectionHistogram1DFilters

creds = Credentials.from_creds_file()
dials = Dials(creds)

# Getting h1d data
data = dials.h1d.list_all(LumisectionHistogram1DFilters(me="PixelPhase1/Tracks/PXBarrel/charge_PXLayer_2"), max_pages=5)
```

### Workspace

Users are automatically routed to a workspace based on e-groups, but it is possible to overwrite this configuration and inspect data from others workspaces:

```python
dials = Dials(creds, workspace="jetmet")
```

## Available endpoints

This package interacts with DIALS api endpoints using underlying classes in `Dials` object.

### Retrieving a specific object using `get`

```python
dials.dataset_index.get(dataset_id=14677060)
dials.file_index.get(dataset_id=14677060, file_id=3393809397)
dials.h1d.get(dataset_id=14677060, run_number=367112, ls_number=10, me_id=1)
dials.h1d.get(dataset_id=14677060, run_number=367112, ls_number=10, me_id=96)
dials.lumi.get(dataset_id=14677060, run_number=367112, ls_number=10)
dials.run.get(dataset_id=14677060, run_number=367112)

# jetmet worskpace
dials.ml_models_index(model_id=1)
dials.ml_bad_lumisection(model_id=19, dataset_id=15102369, run_number=386951, ls_number=36)
```

### Retrieving a list of objects per page using `list`

It is possible to get a list of entries from those endpoint using the `list` and `list_all` methods, the `list` method will fetch only one page and the `list_all` will fetch all available pages:

```python
dials.dataset_index.list()
dials.file_index.list()
dials.h1d.list()
dials.h2d.list()
dials.lumi.list()
dials.run.list()
dials.ml_models_index.list()
dials.ml_bad_lumisection.list()
```

### Retrieving all available pages of a list of objects using `list_all`

> [!NOTE]
> Keep in mind that running `list_all` without any filter can take too much time, since you will be retrieving all rows in the database.

```python
dials.dataset_index.list_all()
dials.file_index.list_all()
dials.h1d.list_all()
dials.h2d.list_all()
dials.lumi.list_all()
dials.run.list_all()
dials.ml_models_index.list_all()
dials.ml_bad_lumisection.list_all()
```

If you don't need all available pages but just a subset of then, it is possible to specify a `max_pages` integer parameter:

```python
dials.run.list_all(..., max_pages=5)
```

### Using filters

Keep in mind that calling those methods without any filter can take a lot of time, because the underlying query will try to load the entire database table through multiple requests, then it is recommended to apply filters according to DIALS [live documentation](https://cmsdials-api.web.cern.ch/api/v1/swagger#/) using filter classes for each table:

```python
from cmsdials.filters import (
    FileIndexFilters,
    LumisectionHistogram1DFilters,
    LumisectionHistogram2DFilters,
    LumisectionFilters,
    RunFilters,
    MLBadLumisectionFilters
)

dials.dataset_index.list_all(DatasetIndexFilters(page_size=500))

dials.file_index.list(FileIndexFilters(dataset__regex="2024B"))

dials.h1d.list(LumisectionHistogram1DFilters(me="PixelPhase1/Tracks/PXBarrel/charge_PXLayer_2"))

dials.h2d.list_all(LumisectionHistogram2DFilters(me__regex="PXBarrel", ls_number=78, entries__gte=100), max_pages=5)

dials.lumi.list_all(LumisectionFilters(run_number=360392), max_pages=5)

dials.run.list_all(RunFilters(run_number__gte=360392, run_number__lte=365000), max_pages=5)

# jetmet workspace
dials.ml_models_index.list_all(MLModelsIndexFilters(active=True))

# jetmet workspace
dials.ml_bad_lumis.list_all(
    MLBadLumisectionFilters(
        page_size=500,
        model_id__in=[20,19],
        dataset_id__in=[15042670],
        run_number__in=[385801,385799,385764]
    )
)
```

### Dials MEs

It is possible to inspect the list of ingested MEs in DIALS listing the endpoint `mes` trough the method:

```python
dials.mes.list()
```

### Automatically convert paginated results to pandas DataFrame

You can enable this optional feature by installing the package with the `pandas` extra.

All `Paginated` metaclasses contain the method `to_pandas` that will automatically transform the `results` attribute of the metaclass into a pandas dataframe, for example:

```python
data = dials.h1d.list_all(LumisectionHistogram1DFilters(me="PixelPhase1/Tracks/PXBarrel/charge_PXLayer_2"), max_pages=5)
data.to_pandas()
```

### Indefinite progress bar when fetch multi-page result

You can enable this optional feature by installing the package with the `tqdm` extra.

Whenever you call a `list_all` method that fetches multiple pages a dynamic progress will be rendered to indicate duration and number of pages, for example:

```python
>>> dials.h2d.list_all(LumisectionHistogram2DFilters(me__regex="PXBarrel", ls_number=78, entries__gte=100), max_pages=5)
Progress: 100%|█████████████████████████████████████| 5/5 [00:02<00:00,  1.70it/s]
```

The total attribute of the bar is dynamically updated while fetching the pages.

## Retrying

In case of an unstable connection, DNS failures or service overload it is possible to configure any `get`, `list` and  `list_all` to retry the underlying requests using native `urllib3` retry class, for example:

```python
from urllib3.util import Retry

data = dials.h1d.get(dataset_id=14677060, run_number=367112, ls_number=10, me_id=1, retries=Retry(total=3, backoff_factor=0.1))
data = dials.h1d.list(retries=Retry(total=3, backoff_factor=0.1))
data = dials.h1d.list_all(LumisectionHistogram1DFilters(), max_pages=5, retries=Retry(total=5, backoff_factor=0.1))
```

## Resuming

When listing and endpoint for a long time, you may loose connection or the server can potentially return an error. By specifying `keep_failed` and using `resume_from` you can resume from an older response object, for example:

```python
from cmsdials.auth.client import AuthClient
from cmsdials.auth.bearer import Credentials
from cmsdials import Dials
from cmsdials.filters import LumisectionHistogram2DFilters

auth = AuthClient()
creds = Credentials.from_creds_file()
dials = Dials(creds, workspace="tracker")

data = dials.h2d.list_all(LumisectionHistogram2DFilters(me__regex="PXBarrel", ls_number=78, entries__gte=100), keep_failed=True)  # Code may broke inside this routine
print(len(data.results))  # 100
print(data.exc_type)
print(data.exc_formatted)

# After failing, run this again
data = dials.h2d.list_all(LumisectionHistogram2DFilters(me__regex="PXBarrel", ls_number=78, entries__gte=100), keep_failed=True, resume_from=data)  # Resume from failed object
print(len(data.results))  # 200
```

You may find it useful to resume from a partial response, i.e,

```python
data = dials.h2d.list_all(LumisectionHistogram2DFilters(me__regex="PXBarrel", ls_number=78, entries__gte=100), max_pages=10, keep_failed=True)  # Code may not break, however will fetch only 100 elements
print(len(data.results))  # 100

# After fetching first 100, fetch next 100
data = dials.h2d.list_all(LumisectionHistogram2DFilters(me__regex="PXBarrel", ls_number=78, entries__gte=100), max_pages=10, keep_failed=True, resume_from=data)  # Resume from partial object
print(len(data.results))  # 200
```

## Fetching ML certification json and ML golden-like json

The following examples are testable in the `jetmet` workspace:

```python
dials.ml_bad_lumis.cert_json(
    model_id__in=[20,19],
    dataset_id__in=[15042670],
    run_number__in=[385801,385799,385764]
)

dials.ml_bad_lumis.golden_json(
    model_id__in=[20,19],
    dataset_id__in=[15042670],
    run_number__in=[385801,385799,385764]
)
```

You may need to query the `ml_models_index` client to fetch the models ids you are interested and the `dataset-index` client to fetch the datasets ids. Take a look in the live documentation to check all possible filters.

Attention: Those endpoints doesn't return a Pydantic model, instead they are returning a plain json response. Consequently, the method `to_pandas` doesn't work on them.

## Usage with local DIALS

All classes that interface the DIALS service inherits the class `BaseAPIClient` which propagate the `base_url`, `route` and `version` attributes with production values. In order to use dials-py with a local version of DIALS it is possible to overwrite those attributes when instantiating the `AuthClient` and the `Dials` client, for example:

```python
from cmsdials.auth.client import AuthClient
from cmsdials.auth.bearer import Credentials
from cmsdials import Dials
from cmsdials.filters import LumisectionHistogram2DFilters

DEV_URL = "http://localhost:8000/"
DEV_CACHE_DIR = ".cache-dev"

auth = AuthClient(base_url=DEV_URL)
creds = Credentials.from_creds_file(cache_dir=DEV_CACHE_DIR, client=auth)  # Make sure to specify the auth client with overwritten values, using another cache_dir is recommended
dials = Dials(creds, base_url=DEV_URL)

dials.h2d.list_all(LumisectionHistogram2DFilters(me__regex="EEOT digi occupancy EE +", entries__gte=100, run_number__gte=360392, run_number__lte=365000), max_pages=5)
```

## Development

Install the dependencies and the package using `uv`:

```shell
uv sync --all-groups --extra pandas --extra tqdm
uv run pre-commit install
uv pip install -e .
```

### Running tests

The repository has some tests written to make sure DIALS responses are compatible with pydantic metaclasses, you can use pytest to run all tests but you need to specify a secret key to authenticate non-interactively against DIALS api:

```bash
SECRET_KEY=... uv run pytest tests
```

The secret key is an api client enabled secret key and can be obtained from the applications portal, any api client secret key whitelisted in DIALS can be used. The interactive authentication flow should be tested manually, an example for this can be found in [this line](/tests/integration/test_auth_client.py#L33).

If testing against a local version of DIALS you need to specify the BASE_URL:

```bash
SECRET_KEY=... BASE_URL=http://localhost:8000 uv run pytest tests
```

#### Tox

Tox is pre-configured in `tox.ini`, so you can run the following to test against multiple python versions locally:

```bash
SECRET_KEY=... uv run tox
```

**[asdf](https://asdf-vm.com/) users**

tox requires multiple versions of Python to be installed. Using `asdf`, you have multiple versions installed, but they aren’t normally exposed to the current shell. You can use the following command to expose multiple versions of Python in the current directory:

```bash
asdf set python 3.12.9 3.11.10 3.10.13 3.9.19
```

This will use `3.12.9` by default (if you just run `python`), but it will also put `python3.11`, `python3.10` and `python3.9` symlinks in your path so you can run those too (which is exactly what tox is looking for).

### Releasing the package on PyPI

The package is available in PyPI at [cmsdials](https://pypi.org/project/cmsdials/), under the [cmsdqm](https://pypi.org/org/cms-dqm/) organization. You'll need at leat Mantainer rights to be able to push new versions.

#### CI

Do not worry. The GitLab CI is configured to automatically publish the package on PyPI and the release notes in GitLab whever a tag is pushed to the repo.

> [!NOTE]
> For this to work the CI/CD variables named `UV_PUBLISH_TOKEN`, `GITLAB_TOKEN` should be registered in gitlab. The `UV_PUBLISH_TOKEN` is a api token access of CMSDQM organization and the `GITLAB_TOKEN` is a Project Access Token with api read/write rights, which is needed to read merge requests using the `glab-cli`.
> https://gitlab.cern.ch/cms-dqmdc/libraries/dials-py/-/settings/access_tokens

#### Manual

If you want to follow the manual approach, you need to first build and then publish.

##### Build

You can use uv to build the package using:

```bash
uv build
```

The build system will automatically update the package version based on the git tag of the current commit.

##### Publish

Provided you have already generate a PyPI api token in your account or in CMDQM org, you can publish using:

```bash
UV_PUBLISH_TOKEN=... uv publish
```
