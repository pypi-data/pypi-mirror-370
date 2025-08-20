from __future__ import print_function

import difflib
import os
import sys
from contextlib import contextmanager

import pytest
from kobo.hub.models import Worker

pytestmark = pytest.mark.django_db

BASELINE_DIR = os.path.join(os.path.dirname(__file__), "baseline")
UPDATE_BASELINES = os.environ.get("KOBO_EXPORTER_UPDATE_BASELINES") == "1"
OPEN_NAME = "__builtin__.open" if sys.version_info < (3,) else "builtins.open"


def fake_worker(*args, **kwargs):
    out = Worker(*args, **kwargs)
    out.save = super(Worker, out).save
    return out


def canonicalize_metrics(lines):
    families = []

    current_family = None

    while lines:
        help_line = lines.pop(0)
        assert help_line.startswith("# HELP")
        type_line = lines.pop(0)
        assert type_line.startswith("# TYPE")

        headers = [help_line, type_line]
        metrics = []
        while lines:
            line = lines.pop(0)
            if line.startswith("#"):
                # next metric family starting, put the line back
                lines.insert(0, line)
                break
            metrics.append(line)

        current_family = headers + sorted(metrics)
        families.append(current_family)

    families.sort(key=lambda family: family[0])

    out = []
    for f in families:
        out.extend([line for line in f])

    return out


@pytest.fixture
def assert_equal_to_baseline(client, request):
    name = request.node.name
    filename = os.path.join(BASELINE_DIR, name + ".txt")

    def fn():
        response = client.get("/kobo_exporter/metrics")

        # It should succeed
        assert response.status_code == 200

        # It should report exactly this content type.
        assert (
            response.get("Content-Type") == "text/plain; version=0.0.4; charset=utf-8"
        )

        if os.path.exists(filename):
            # Load expected data from baseline file if we can.
            with open(filename, "r") as baseline:
                expected_lines = baseline.readlines()
        else:
            expected_lines = ["<no data>\n"]

        actual_lines = response.content.decode("utf-8").splitlines()
        actual_lines = [line + "\n" for line in actual_lines]

        actual_lines = canonicalize_metrics(actual_lines)

        if actual_lines != expected_lines:
            diff = "".join(difflib.unified_diff(expected_lines, actual_lines))
            if UPDATE_BASELINES:
                print(diff)
                print("Updating baseline", filename)
                with open(filename, "wt") as f:
                    f.write("".join(actual_lines))
            else:
                raise AssertionError("Output differs from expected:\n%s" % diff)

    return fn


def test_metrics_empty(assert_equal_to_baseline):
    """Metrics generates OK when there are no workers."""

    # DB should be empty, let's just sanity check
    assert Worker.objects.count() == 0

    assert_equal_to_baseline()


def test_metrics_typical_no_last_seen(assert_equal_to_baseline):
    """Metrics generates OK in typical case where some workers exist and last_seen is unknown."""

    w1 = fake_worker(
        name="worker1",
        enabled=False,
        ready=True,
        current_load=123,
        max_load=456,
        task_count=789,
        worker_key="abc123",
    )
    w2 = fake_worker(
        name="worker2",
        enabled=True,
        ready=False,
        current_load=0,
        max_load=1,
        task_count=0,
        worker_key="abc124",
    )
    w1.save()
    w2.save()

    assert_equal_to_baseline()


def test_metrics_with_last_seen(assert_equal_to_baseline, monkeypatch):
    """Metrics generates OK in typical case with known last_seen."""

    w1 = fake_worker(
        name="worker1",
        enabled=False,
        ready=True,
        current_load=123,
        max_load=456,
        task_count=789,
        worker_key="abc123",
    )
    w2 = fake_worker(
        name="worker2",
        enabled=True,
        ready=False,
        current_load=0,
        max_load=1,
        task_count=0,
        worker_key="abc124",
    )

    # Force an update of last_seen to a known timestamp.
    real_open = open

    @contextmanager
    def fake_open(filename, *args, **kwargs):
        with real_open(filename, *args, **kwargs) as f:
            yield f
        os.utime(filename, (1626743511, 1626743511))

    with monkeypatch.context() as m:
        m.setattr(OPEN_NAME, fake_open)
        w1.update_last_seen()
        w2.update_last_seen()
        w1.save()
        w2.save()

    assert_equal_to_baseline()
