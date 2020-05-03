import os
import random
import string
import subprocess
import sys

import ward

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../src")
import sdmpm


test_service_file = """
[Unit]
Description=Test Service

[Service]
ExecStart=/bin/sleep 60
Restart=always

[Install]
WantedBy=multi-user.target
"""


@ward.fixture
def test_service():
    random_str = "".join(random.choice(string.ascii_lowercase) for _ in range(4))
    service_name = "test-" + random_str
    service_path = os.path.expanduser(
        "~/.config/systemd/user/" + service_name + "@.service"
    )
    service_dir = os.path.dirname(service_path)
    if not os.path.exists(service_dir):
        os.makedirs(service_dir)
    with open(service_path, "wt") as fh:
        fh.write(test_service_file)
    try:
        yield service_name
    finally:
        pass
        services = [l.split()[0] for l in _list_units(service_name).splitlines()]
        if services:
            subprocess.call(
                ["systemctl", "--quiet", "--user", "disable", "--now", "--"] + services
            )
        os.remove(service_path)


def _list_units(svc):
    return subprocess.check_output(
        [
            "systemctl",
            "--no-legend",
            "--no-pager",
            "--user",
            "list-units",
            "--all",
            "--",
            svc + "@*.service",
        ]
    )


@ward.test("can scale services")
def _(svc=test_service):
    for i in (1, 2, 4, 2, 0):
        sdmpm.scale_service(svc, i, user=True)
        assert len(_list_units(svc).splitlines()) == i


@ward.test("can control services")
def _(svc=test_service):
    sdmpm.scale_service(svc, 2, user=True)
    assert len(_list_units(svc).splitlines()) == 2
    sdmpm.control_units("stop", svc, user=True)
    assert len(_list_units(svc).splitlines()) == 0
    sdmpm.control_units("start", svc, user=True)
    assert len(_list_units(svc).splitlines()) == 2
