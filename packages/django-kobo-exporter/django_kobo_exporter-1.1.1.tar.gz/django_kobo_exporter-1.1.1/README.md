# django-kobo-exporter

Prometheus exporter for [kobo](https://github.com/release-engineering/kobo) hub.

![tests](https://github.com/release-engineering/django-kobo-exporter/actions/workflows/tox-tests.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/django-kobo-exporter.svg)](https://badge.fury.io/py/django-kobo-exporter)

<!--TOC-->

- [django-kobo-exporter](#django-kobo-exporter)
  - [Overview](#overview)
  - [Usage](#usage)
  - [License](#license)

<!--TOC-->

## Overview

The [kobo](https://github.com/release-engineering/kobo) framework provides, among
other things, a Django-based "hub" web service which is used to manage tasks and
workers.

django-kobo-exporter is a Django app which may be installed to a kobo hub in
order to add a [prometheus](https://prometheus.io/)-compatible metrics endpoint
exposing kobo metrics.

## Usage

1. Ensure `django-kobo-exporter` is installed, e.g.

```
pip install django-kobo-exporter
```

2. In your app's settings, add `kobo_exporter` to `INSTALLED_APPS`, e.g.

```python
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'kobo.django.auth',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'kobo.django.xmlrpc',
    'kobo.hub',
    # added here
    'kobo_exporter',
    # your app's own stuff below...
    ...,
]
```

3. Mount `kobo_exporter.urls` somewhere in your project.

`/kobo_exporter/` is recommended; for example, in your root urlpatterns:

```python
from django.urls import include, path

urlpatterns = [
    # ... snip ...
    path('kobo_exporter/', include('kobo_exporter.urls')),
    # ... snip ...
]
```

4. Access metrics at `<your_service>/kobo_exporter/metrics`.

The metrics endpoint will provide basic information on workers,
as in example:

```
# HELP kobo_worker_enabled 1 if worker is enabled
# TYPE kobo_worker_enabled gauge
kobo_worker_enabled{worker="localhost"} 1.0
kobo_worker_enabled{worker="pub-dev-pubd7"} 1.0
# HELP kobo_worker_ready 1 if worker is ready
# TYPE kobo_worker_ready gauge
kobo_worker_ready{worker="localhost"} 1.0
kobo_worker_ready{worker="pub-dev-pubd7"} 1.0
# HELP kobo_worker_load Current load of worker (sum of task weights)
# TYPE kobo_worker_load gauge
kobo_worker_load{worker="localhost"} 0.0
kobo_worker_load{worker="pub-dev-pubd7"} 0.0
# HELP kobo_worker_max_load Maximum permitted load of worker
# TYPE kobo_worker_max_load gauge
kobo_worker_max_load{worker="localhost"} 60.0
kobo_worker_max_load{worker="pub-dev-pubd7"} 60.0
# HELP kobo_worker_open_tasks Current number of OPEN tasks for worker
# TYPE kobo_worker_open_tasks gauge
kobo_worker_open_tasks{worker="localhost"} 0.0
kobo_worker_open_tasks{worker="pub-dev-pubd7"} 0.0
# HELP kobo_worker_last_seen_seconds Time of worker's last communication with hub
# TYPE kobo_worker_last_seen_seconds gauge
kobo_worker_last_seen_seconds{worker="localhost"} 1.625644554e+09
kobo_worker_last_seen_seconds{worker="pub-dev-pubd7"} 0.0
```


## License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
