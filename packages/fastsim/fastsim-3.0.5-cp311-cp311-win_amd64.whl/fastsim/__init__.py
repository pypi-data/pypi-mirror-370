"""Python API for fastsim"""

import inspect
import re
import sys
from importlib.metadata import version
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast  # noqa: UP035

import numpy as np
import pandas as pd  # type: ignore[import-untyped]
import polars as pl

import fastsim

from . import utils  # type: ignore[attr-defined]  # noqa: F401
from .fastsim import *  # noqa: F403
from .fastsim import Cycle  # type: ignore[attr-defined]


def check_version_gte_311() -> bool:
    """Return true if python version is greater than or equal to 3.11"""
    v = sys.version
    m = re.match("(\\d)\\.(\\d{2})", v)
    m = cast(list[str], m)
    assert m[1] == "3"
    return int(m[2]) >= 11


if check_version_gte_311():
    # not available in older python versions
    from typing import Self
else:
    # available in older python versions
    from typing_extensions import Self  # noqa:UP035


def package_root() -> Path:
    """Return the package root directory."""
    return Path(__file__).parent


def resources_root() -> Path:
    """Return the resources root directory."""
    path = package_root() / "resources"
    return path


__version__ = version("fastsim")


def __array__(self):
    return np.array(self.tolist())


# creates a list of all python classes from rust structs that need variable_path_list() and
# history_path_list() added as methods
ACCEPTED_RUST_STRUCTS = [
    attr
    for attr in fastsim.__dir__()
    if not attr.startswith("__")
    and isinstance(getattr(fastsim, attr), type)
    and attr[0].isupper()
    and ("fastsim" in str(inspect.getmodule(getattr(fastsim, attr))))
]


def cyc_keys() -> list[str]:
    """Return cycle keys"""
    import json

    cyc = Cycle.from_resource("udds.csv")
    cyc_dict = json.loads(cyc.to_json())
    cyc_keys = [
        key for key, val in cyc_dict.items() if isinstance(val, list) and len(val) == cyc.len()
    ]

    return cyc_keys


CYC_KEYS = cyc_keys()

# TODO connect to crate features
data_formats = [
    "yaml",
    "msg_pack",
    # 'toml',
    "json",
]


def to_pydict(self, data_fmt: str = "msg_pack", flatten: bool = False) -> dict:
    """
    Return self converted to pure python dictionary with no nested Rust objects

    # Arguments
    - `flatten`: if True, returns dict without any hierarchy
    - `data_fmt`: data format for intermediate conversion step
    """
    data_fmt = data_fmt.lower()
    assert data_fmt in data_formats, f"`data_fmt` must be one of {data_formats}"
    match data_fmt:
        case "msg_pack":
            import msgpack  # type: ignore[import-untyped]

            pydict = msgpack.loads(self.to_msg_pack())
        case "yaml":
            from yaml import load  # type: ignore[import-untyped]

            try:
                from yaml import CLoader as Loader
            except ImportError:
                from yaml import Loader
            pydict = load(self.to_yaml(), Loader=Loader)
        case "json":
            from json import loads

            pydict = loads(self.to_json())

    if not flatten:
        return cast(dict[Any, Any], pydict)
    else:
        hist_len = get_hist_len(pydict)
        assert hist_len is not None, "Cannot be flattened"
        flat_dict = get_flattened(pydict, hist_len)
        return flat_dict


def get_hist_len(obj: dict) -> int | None:
    """Find nested `history` and gets lenth of first element"""
    # TODO: check if this is sufficiently recursive and if it's not, make it
    # recursive all the way down

    if "history" in obj:
        return len(next(iter(obj["history"].values())))

    elif (
        next(iter(k for k in obj if re.search("(history\\.\\w+)$", k) is not None), None)
        is not None
    ):
        return len(
            next(v for (k, v) in obj.items() if re.search("(history\\.\\w+)$", k) is not None),
        )

    for v in obj.values():
        if isinstance(v, dict):
            hist_len = get_hist_len(v)
            if hist_len is not None:
                return hist_len
    return None


def get_flattened(obj: dict | list, hist_len: int, prepend_str: str = "") -> dict:
    """
    Flatten and return dictionary, separating keys and indices with a `"."`

    # Arguments
    # - `obj`: object to flatten
    # -  hist_len: length of any lists storing history data
    # - `prepend_str`: prepend this to all keys in the returned `flat` dict
    """
    flat: dict = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = k if (prepend_str == "") else prepend_str + "." + k
            if isinstance(v, dict) or (isinstance(v, list) and len(v) != hist_len):
                flat.update(get_flattened(v, hist_len, prepend_str=new_key))
            else:
                flat[new_key] = v
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            new_key = i if (prepend_str == "") else prepend_str + "." + f"[{i}]"
            if isinstance(v, dict) or (isinstance(v, list) and len(v) != hist_len):
                flat.update(get_flattened(v, hist_len, prepend_str=new_key))
            else:
                flat[new_key] = v
    else:
        raise TypeError("`obj` should be `dict` or `list`")

    return flat


@classmethod  # type: ignore[misc]
def from_pydict(cls, pydict: dict, data_fmt: str = "msg_pack", skip_init: bool = False) -> Self:  # type: ignore[misc]
    """
    Instantiate Self from pure python dictionary

    # Arguments
    - `pydict`: dictionary to be converted to FASTSim object
    - `data_fmt`: data format for intermediate conversion step
    - `skip_init`: passed to `SerdeAPI` methods to control whether initialization
      is skipped
    """
    data_fmt = data_fmt.lower()
    assert data_fmt in data_formats, f"`data_fmt` must be one of {data_formats}"
    match data_fmt.lower():
        case "yaml":
            import yaml

            obj = cls.from_yaml(yaml.dump(pydict), skip_init=skip_init)
        case "msg_pack":
            import msgpack

            obj = cls.from_msg_pack(msgpack.packb(pydict), skip_init=skip_init)
        case "json":
            from json import dumps

            obj = cls.from_json(dumps(pydict), skip_init=skip_init)

    return obj


def to_dataframe(
    self,
    pandas: bool = False,
    allow_partial: bool = False,
) -> pd.DataFrame | pl.DataFrame:
    """
    Return time series results from fastsim object as a Polars or Pandas dataframe.

    # Arguments
    - `pandas`: returns pandas dataframe if True; otherwise, returns polars dataframe by default
    - `allow_partial`: tries to return dataframe of length equal to solved time
        steps if simulation fails early
    """
    obj_dict = self.to_pydict(flatten=True)
    history_keys = ["history.", "cyc."]
    hist_len = get_hist_len(obj_dict)
    assert hist_len is not None

    history_dict: dict[str, Any] = {}
    for k, v in obj_dict.items():
        hk_in_k = any(hk in k for hk in history_keys)
        if (hk_in_k and ("__len__" in dir(v))) and ((len(v) == hist_len) or allow_partial):
            history_dict[k] = v

    if allow_partial:
        cutoff = min(history_dict.values())

        df: pl.DataFrame | pd.DataFrame
        if not pandas:
            try:
                df = pl.DataFrame({col: val[:cutoff] for col, val in history_dict.items()})
            except Exception as err:
                raise Exception(f"{err}\n`save_interval` may not be uniform")
        else:
            try:
                df = pd.DataFrame({col: val[:cutoff] for col, val in history_dict.items()})
            except Exception as err:
                raise Exception(f"{err}\n`save_interval` may not be uniform")

    else:
        if not pandas:
            try:
                df = pl.DataFrame(history_dict)
            except Exception as err:
                raise Exception(
                    f"{err}\nTry passing `allow_partial=True` to `to_dataframe` or checking for "
                    + "consistent save intervals",
                )
        else:
            try:
                df = pd.DataFrame(history_dict)
            except Exception as err:
                raise Exception(
                    f"{err}\nTry passing `allow_partial=True` to `to_dataframe` or checking for "
                    + "consistent save intervals",
                )
    return df


# adds variable_path_list() and history_path_list() as methods to all classes in
# ACCEPTED_RUST_STRUCTS
for item in ACCEPTED_RUST_STRUCTS:
    setattr(getattr(fastsim, item), "to_pydict", to_pydict)
    setattr(getattr(fastsim, item), "from_pydict", from_pydict)
    setattr(getattr(fastsim, item), "to_dataframe", to_dataframe)
