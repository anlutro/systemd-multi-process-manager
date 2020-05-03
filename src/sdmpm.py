#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys


class UserError(Exception):
    pass


class SystemctlException(Exception):
    def __init__(self, retcode, cmd, stderr):
        msg = "systemctl %s failed with error code %d" % (cmd[1:], retcode)
        super().__init__(msg)
        self.retcode = retcode
        self.cmd = cmd
        self.stderr = stderr.strip()


def systemctl(args, *, user=False, capture_output=False):
    cmd = ["systemctl", "--no-legend", "--no-pager"]
    if user:
        cmd.append("--user")
    proc = subprocess.Popen(
        cmd + args,
        stdout=subprocess.PIPE if capture_output else None,
        encoding="utf-8",
    )
    stdout, stderr = proc.communicate()
    proc.wait()
    if capture_output:
        return stdout


def get_active_units(service, *, user=False):
    # check that the unit file exists
    unit_files = systemctl(
        ["list-unit-files", "--", service + "@.service"], user=user, capture_output=True
    )
    if not unit_files.strip():
        raise UserError(
            "no systemd unit file with name " + service + "@.service found!"
        )

    units = systemctl(
        ["list-units", "--all", "--", service + "@*.service"],
        user=user,
        capture_output=True,
    )
    return sorted([l.split()[0] for l in units.splitlines()])


def get_enabled_units(service, *, user=False):
    units = []
    # TODO: is hard-coding multi-user okay?
    svc_path = (
        os.path.expanduser("~/.config/systemd/user/multi-user.target.wants")
        if user
        else "/etc/systemd/system/multi-user.target.wants/"
    )
    for f in os.listdir(svc_path):
        if f.startswith(service + "@"):
            units.append(f)
    return sorted(units)


def scale_service(service, num_procs, *, user=False):
    if not isinstance(num_procs, int) or num_procs < 0:
        raise ValueError("num_procs must be an integer, 0 or greater")

    units = get_active_units(service, user=user)

    # units look like: example@1.service
    current_unit_numbers = {int(s.split("@")[1].split(".")[0]) for s in units}
    wanted_unit_numbers = set(range(1, num_procs + 1))

    if len(units) > num_procs:
        systemctl_cmd = "disable"
        service_nums = current_unit_numbers - wanted_unit_numbers
    elif len(units) < num_procs:
        systemctl_cmd = "enable"
        service_nums = wanted_unit_numbers - current_unit_numbers
    else:
        print("correct number of units running, not doing anything")
        return

    service_nums = sorted([str(i) for i in service_nums])

    print(
        "%d units running, wanted %d - will %s service numbers: %s"
        % (len(units), num_procs, systemctl_cmd, ", ".join(service_nums))
    )
    services = [(service + "@" + s) for s in service_nums]

    systemctl([systemctl_cmd, "--quiet", "--now"] + services, user=user)


def control_active_units(cmd, service, *, user=False):
    units = get_active_units(service, user=user)
    if not units:
        units = get_enabled_units(service, user=user)
    if not units:
        print("no units found for", service)
        return

    systemctl([cmd] + units, user=user)


def control_units(cmd, service, *, user=False):
    units = get_enabled_units(service, user=user)

    systemctl([cmd] + units, user=user)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", action="store_true")

    cmd = parser.add_subparsers(dest="cmd")
    scale_p = cmd.add_parser("scale")
    status_p = cmd.add_parser("status")
    start_p = cmd.add_parser("start")
    stop_p = cmd.add_parser("stop")
    restart_p = cmd.add_parser("restart")
    enable_p = cmd.add_parser("enable")
    disable_p = cmd.add_parser("disable")
    for p in (scale_p, status_p, restart_p, stop_p, start_p, enable_p, disable_p):
        p.add_argument("service")

    scale_p.add_argument("num_procs", type=int)

    args = parser.parse_args(argv)

    try:
        if args.cmd == "scale":
            scale_service(args.service, args.num_procs, user=args.user)
        elif args.cmd in ("status", "stop", "restart"):
            control_active_units(args.cmd, args.service, user=args.user)
        elif args.cmd in ("start", "enable", "disable"):
            control_units(args.cmd, args.service, user=args.user)
        elif args.cmd is None:
            parser.print_help()
        else:
            print("unknown command or not implemented:", args.cmd)
            sys.exit(1)
    except SystemctlException as exc:
        print(exc)
        print("cmd:", exc.cmd)
        if exc.stderr:
            print("stderr:\n" + exc.stderr)
        sys.exit(2)
    except UserError as exc:
        print(exc)
        sys.exit(3)


if __name__ == "__main__":
    main()
