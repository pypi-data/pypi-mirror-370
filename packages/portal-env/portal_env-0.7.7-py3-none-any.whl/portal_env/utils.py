import subprocess
from typing import List

import numpy as np
import gymnasium as gym
import ast
import re


class EnvNotSupportedError(Exception):
    pass


def handle_raw_integer(x):
    """
    Apparently, portal modifies the original data type of the integer and converts it to np.ndarray.
    This utility function converts it back to int.
    :param x:
    :return:
    """
    if isinstance(x, np.ndarray):
        assert x.size == 1 and x.dtype == np.int64
        return x.item()
    else:
        assert isinstance(x, int)
        return x


def docker_image_exists(image_name: str) -> bool:
    try:
        subprocess.run(
            ["docker", "image", "inspect", image_name],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False


def ensure_docker_network_exists(network_name: str):
    try:
        # Check if the network exists
        subprocess.run(
            ["docker", "network", "inspect", network_name],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        # Create the network if it doesn't exist
        subprocess.run(["docker", "network", "create", network_name], check=True)


# TODO: Improve this function.
# TODO: Write tests for this function.
def parse_gym_space(space_str: str) -> gym.Space:
    space_str = space_str.strip()

    # Discrete(n) or Discrete(n, start=s)
    if space_str.startswith("Discrete"):
        match = re.fullmatch(r"Discrete\((\d+)(?:, start=(\d+))?\)", space_str)
        if match:
            n = int(match.group(1))
            start = int(match.group(2)) if match.group(2) else 0
            return gym.spaces.Discrete(n, start=start)

    # MultiBinary(n)
    if space_str.startswith("MultiBinary"):
        match = re.fullmatch(r"MultiBinary\((\d+)\)", space_str)
        if match:
            return gym.spaces.MultiBinary(int(match.group(1)))

    # MultiDiscrete([nvec], start=[start])
    if space_str.startswith("MultiDiscrete"):
        match = re.fullmatch(r"MultiDiscrete\((\[.*?\])(?:, start=(\[.*?\]))?\)", space_str)
        if match:
            nvec = ast.literal_eval(match.group(1))
            start = ast.literal_eval(match.group(2)) if match.group(2) else np.zeros_like(nvec)
            return gym.spaces.MultiDiscrete(nvec=nvec, start=start)

    # Box(low, high, shape, dtype)
    if space_str.startswith("Box"):
        shape_regex = r"(\(\s*\d+,\s*(\d+\s*(,\s*\d+\s*)*)?\))"
        non_shape_regex = r"(.*?)"
        match = re.fullmatch(rf"Box\(({shape_regex}|{non_shape_regex}), ({shape_regex}|{non_shape_regex}), {shape_regex}, (.*?)\)", space_str)
        if match:
            low = resolve_low_high(match.group(1))
            high = resolve_low_high(match.group(6))
            shape = ast.literal_eval(match.group(11))
            dtype_str = match.group(14).strip()
            dtype = resolve_dtype(dtype_str)
            return gym.spaces.Box(low=low, high=high, shape=shape, dtype=dtype)

    # Tuple(Space1, Space2, ...)
    if space_str.startswith("Tuple"):
        inner = space_str[len("Tuple("):-1]
        elements = split_top_level_commas(inner)
        return gym.spaces.Tuple([parse_gym_space(e.strip()) for e in elements])

    # Dict('key1': Space1, ...)
    if space_str.startswith("Dict"):
        inner = space_str[len("Dict("):-1]
        items = split_top_level_commas(inner)
        result = {}
        for item in items:
            key, val = item.split(":", 1)
            key = ast.literal_eval(key.strip())
            val = parse_gym_space(val.strip())
            result[key] = val
        return gym.spaces.Dict(result)

    raise ValueError(f"Unsupported Gym space string: {space_str}")

def split_top_level_commas(s: str) -> List[str]:
    """
    Splits a string by top-level commas, ignoring those inside parentheses.
    For example: "Discrete(2), Box(0,1,(2,),np.float32)" => ["Discrete(2)", "Box(0,1,(2,),np.float32)"]
    """
    parts = []
    depth = 0
    last = 0
    for i, c in enumerate(s):
        if c in "([{": depth += 1
        elif c in ")]}": depth -= 1
        elif c == "," and depth == 0:
            parts.append(s[last:i])
            last = i + 1
    parts.append(s[last:])
    return parts

def resolve_dtype(dtype_str: str) -> np.dtype:
    """Resolves dtype string to actual NumPy dtype, adding `np.` if needed."""
    try:
        # Try evaluating fully qualified dtype (e.g. np.uint8)
        return eval(dtype_str)
    except NameError:
        # Fallback: try using np.<dtype_str> (e.g. 'uint8' -> np.uint8)
        try:
            return getattr(np, dtype_str)
        except AttributeError:
            raise ValueError(f"Unknown dtype: {dtype_str}")

def resolve_low_high(value: str):
    if value == '-inf':
        return -np.inf
    elif value == 'inf':
        return np.inf
    else:
        try:
            return ast.literal_eval(value)
        except ValueError:
            try:
                return getattr(np, value)
            except AttributeError:
                raise ValueError(f"Unknown dtype: {value}")

