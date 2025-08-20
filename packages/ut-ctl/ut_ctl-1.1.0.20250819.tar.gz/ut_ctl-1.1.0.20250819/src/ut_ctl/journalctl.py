# coding=utf-8
from typing import Any

from datetime import datetime
import re
import subprocess

from ut_log.log import LogEq, Log

TyAny = Any
TnFloat = None | float


class Journalctl:

    @staticmethod
    def get_last_stop_ts_µs(service_name: str) -> TnFloat:
        """
        get last stop timestamp in micro seconds of service
        """
        try:
            # Get the service logs
            _cmds = ["journalctl", "-u", service_name, "--no-pager", "--reverse"]
            _result = subprocess.run(
                _cmds, capture_output=True, text=True
            )
            _current_year = datetime.now().year
            _logs = _result.stdout.splitlines()
            _ts_pattern = r'\b[A-Za-z]{3} \d{2} \d{2}:\d{2}:\d{2}\b'
            for _log in _logs:
                if "Stopped" in _log:
                    # Return the timestamp of the first "Stopped" log entry
                    _match = re.search(_ts_pattern, _log)
                    if _match:
                        _ts = _match.group()  # Extract the matched string
                        _ts = f"{_current_year} {_ts}"
                    else:
                        _msg = f"Last stop ts of service: {service_name} not found in log: {_log}"
                        Log.error(_msg)
                        return None
                    # Parse the string into a datetime object
                    _ts_date_object = datetime.strptime(_ts, "%Y %b %d %H:%M:%S")
                    # Convert the datetime object to a timestamp of micro seconds
                    _ts_µs = _ts_date_object.timestamp()
                    LogEq.debug("_log", _log)
                    LogEq.debug("_ts", _ts)
                    LogEq.debug("_ts_µs", _ts_µs)
                    return _ts_µs
            _msg = f"Last stop ts of service: {service_name} not found in logs"
            Log.error(_msg)
            return None
        except Exception:
            raise

    @classmethod
    def get_last_stop_ts_s(cls, service_name: str) -> TnFloat:
        """
        get last stop timestamp in seconds of service
        """
        _ts_µs = cls.get_last_stop_ts_µs(service_name)
        if not _ts_µs:
            return _ts_µs
        return _ts_µs / 1_000_000
