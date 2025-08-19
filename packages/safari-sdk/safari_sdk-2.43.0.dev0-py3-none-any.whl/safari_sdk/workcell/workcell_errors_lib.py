"""Workcell errors definitions."""

import dataclasses
from safari_sdk.workcell import workcell_recovery_schemes_lib


@dataclasses.dataclass
class WorkcellErrors:
  error_identifier_regex: str
  error_recovery_scheme: workcell_recovery_schemes_lib.RecoveryScheme


test_error = WorkcellErrors(
    error_identifier_regex=r"Testing Workcell Error Recovery",
    error_recovery_scheme=workcell_recovery_schemes_lib.test_recovery_scheme,
)


# Empty errors list for platforms that don't have any workcell errors.
EMPTY_ERRORS_LIST: list[WorkcellErrors] = []
