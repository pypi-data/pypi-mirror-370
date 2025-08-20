# coding=utf-8
from typing import Any

import subprocess

from ut_log.log import Log

TyClsName = Any
TyModName = Any
TyPacName = Any
TyPacModName = Any
TyFncName = Any
TnFloat = None | float


class Systemctl:

    @staticmethod
    def get_last_stop_ts_s(service_name) -> TnFloat:
        """
        show module name of function
        """
        _property = "InactiveExitTimestampMonotonic"
        _cmds = ["systemctl", "show", service_name, f"--property={_property}"]
        try:
            # Run the systemctl command to get service details
            result = subprocess.run(
                _cmds,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, check=True
            )
            _output = result.stdout.strip()
            # Extract the start timestamp from the output
            if _output.startswith(f"{_property}="):
                _ts_µs = _output.split("=", 1)[1]
                if not _ts_µs:
                    _msg = f"Last stop ts of service: {service_name} is undefined"
                    Log.error(_msg)
                    return None
                elif _ts_µs == '0':
                    _msg = f"Last stop ts of service: {service_name} is '0'"
                    Log.error(_msg)
                    return None

                _msg = f"Last stop ts in µs: {_ts_µs} of service: {service_name}"
                Log.debug(_msg)
                _ts_s: float = int(_ts_µs) / 1_000_000
                _msg = f"Last stop ts in s: {_ts_s} of service: {service_name}"
                Log.debug(_msg)
                return _ts_s
            else:
                _msg = "Last stop ts not available or service was not running."
                Log.error(_msg)
                return None
                # raise Exception(msg)
        except subprocess.CalledProcessError as e:
            _msg = f"Error retrieving service information: {e}"
            raise Exception(_msg)

    @staticmethod
    def get_start_ts(service_name):
        """
        show module name of function
        """
        _property = "ExecMainStartTimestamp"
        _cmds = ["systemctl", "show", service_name, f"--property={_property}"]
        try:
            # Run the systemctl command to get service details
            result = subprocess.run(
                _cmds,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, check=True
            )
            _output = result.stdout.strip()
            # Extract the start timestamp from the output
            if _output.startswith(f"{_property}="):
                _ts_µs = _output.split("=", 1)[1]
                if not _ts_µs:
                    _msg = f"Start ts of service: {service_name} is undefined"
                    Log.error(_msg)
                    return None
                elif _ts_µs == '0':
                    _msg = f"Start ts of service: {service_name} is '0'"
                    Log.error(_msg)
                    return None

                _msg = f"Start ts in µs: {_ts_µs} of service: {service_name}"
                Log.debug(_msg)
                _ts_s: float = int(_ts_µs) / 1_000_000
                _msg = f"Start ts in s: {_ts_s} of service: {service_name}"
                Log.debug(_msg)
                return _ts_s
            else:
                _msg = "Start ts not available or service was not running."
                Log.error(_msg)
                return None
                # raise Exception(msg)
        except subprocess.CalledProcessError as e:
            _msg = f"Error retrieving service information: {e}"
            raise Exception(_msg)
