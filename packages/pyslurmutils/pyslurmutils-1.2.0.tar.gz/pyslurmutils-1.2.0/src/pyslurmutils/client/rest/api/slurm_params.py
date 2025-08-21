import datetime
from typing import Tuple, Any, Dict, Union, List

_VersionType = Tuple[int, int, int]


def timedelta_in_minutes(version: _VersionType, delta_time: Any) -> Any:
    if isinstance(delta_time, str):
        try:
            hours, minutes, seconds = map(int, delta_time.split(":"))
            delta = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
        except Exception:
            # Wrong string format. Try submitting the Slurm job anyway.
            pass
        else:
            delta_time = delta.total_seconds() / 60.0
    if isinstance(delta_time, int):
        return integral_number(version, delta_time)
    if isinstance(delta_time, float):
        return integral_number(version, delta_time + 0.5)
    return delta_time


def environment(
    version: _VersionType, environment: Dict[str, Any]
) -> Union[Dict[str, str], List[str]]:
    if version < (0, 0, 39):
        return {k: str(v) for k, v in environment.items()}
    else:
        return [f"{k}={v}" for k, v in environment.items()]


def integral_number(version: _VersionType, number: Any) -> Any:
    if not isinstance(number, int):
        try:
            number = int(number)
        except Exception:
            return number
    return {"number": number, "set": True, "infinite": False}
