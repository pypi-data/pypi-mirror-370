# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2024/1/5 16:25
# Author     ：Maxwell
# Description：
"""

import re
import json
from typing import Optional, Dict, List, Union


def extract_json_from_string(s: str) -> Optional[Union[Dict, List]]:
    if not s:
        return None

    json_pattern = re.compile(r"(\{[^{}]*}|$[^\[$]*])", re.DOTALL)
    candidates = []

    for match in json_pattern.finditer(s):
        candidate = match.group(0)
        try:
            if candidate.startswith("{") or candidate.startswith("["):
                candidates.append((match.start(), match.end(), candidate))
        except (IndexError, AttributeError):
            continue

    for start, end, candidate in candidates:
        if (
            candidate.startswith("{") and candidate.count("{") == candidate.count("}")
        ) or (
            candidate.startswith("[") and candidate.count("[") == candidate.count("]")
        ):
            try:
                parsed = json.loads(candidate)
                return parsed
            except json.JSONDecodeError:
                expanded = _expand_json_boundary(s, start, end)
                if expanded:
                    try:
                        return json.loads(expanded)
                    except json.JSONDecodeError:
                        continue
                continue

    return _robust_json_parse(s)


def _expand_json_boundary(s: str, start: int, end: int) -> Optional[str]:
    stack = []
    in_string = False
    escape = False

    for i in range(start, len(s)):
        c = s[i]

        if c == '"' and not escape:
            in_string = not in_string
        elif not in_string:
            if c == "{" or c == "[":
                stack.append(c)
            elif c == "}" and stack and stack[-1] == "{":
                stack.pop()
            elif c == "]" and stack and stack[-1] == "[":
                stack.pop()

        escape = c == "\\" and not escape

        if not stack and not in_string:
            return s[start : i + 1]

    return None


def _robust_json_parse(s: str) -> Optional[Union[Dict, List]]:
    stack = []
    in_string = False
    escape = False
    start_index = None
    structures = []

    for i, c in enumerate(s):
        if c == '"' and not escape:
            in_string = not in_string
        elif not in_string:
            if c == "{" or c == "[":
                if not stack:
                    start_index = i
                stack.append(c)
            elif c == "}" and stack and stack[-1] == "{":
                stack.pop()
                if not stack:
                    structures.append((start_index, i + 1))
            elif c == "]" and stack and stack[-1] == "[":
                stack.pop()
                if not stack:
                    structures.append((start_index, i + 1))

        escape = c == "\\" and not escape

    structures.sort(key=lambda x: x[1] - x[0], reverse=True)

    for start, end in structures:
        try:
            return json.loads(s[start:end])
        except json.JSONDecodeError:
            continue

    return None
