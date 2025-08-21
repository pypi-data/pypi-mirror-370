# SPDX-FileCopyrightText: 2025-present The CSL-Reference Team <https://github.com/Fusion-Power-Plant-Framework/csl-reference>
#
# SPDX-License-Identifier: MIT
"""Testing tools."""

import contextlib
import warnings
from collections.abc import Iterator

import pytest


@contextlib.contextmanager
def assert_no_warnings() -> Iterator[None]:
    """
    Assert that no warnings occur within a scope.

    This function should be used as a context manager.
    """
    with warnings.catch_warnings(record=True) as warn_records:
        yield
    if warn_records:
        warn_record = warn_records[0]
        pytest.fail(
            "warning emitted where one shouldn't have been:\n"
            + warnings.formatwarning(
                message=warn_record.message,
                category=warn_record.category,
                filename=warn_record.filename,
                lineno=warn_record.lineno,
                line=warn_record.line,
            )
        )
