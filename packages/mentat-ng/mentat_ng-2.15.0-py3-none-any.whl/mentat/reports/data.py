#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains data representation classes for reporting.
"""

__author__ = "Jakub Judiny <Jakub.Judiny@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from mentat.datatype.sqldb import GroupModel


@dataclass
class ReportingProperties:
    """
    Represents basic properties of the current reporting run.

    Attributes:
        group (GroupModel): Group for which the reports are generated.
        severity (str): Severity for which to perform reporting.
        lower_time_bound (datetime): Lower reporting time threshold.
        upper_time_bound (datetime): Upper reporting time threshold.
        template_vars (Optional[dict]): Dictionary containing additional template variables.
        has_test_data (bool): Switch to use test data for reporting.
        is_shadow (bool): If it is shadow reporting (True), or normal reporting (False).
        is_target (bool): If the reporting is target-based (True) or source-based (False).
    """

    group: GroupModel
    severity: str
    lower_time_bound: datetime
    upper_time_bound: datetime
    template_vars: Optional[dict] = None
    has_test_data: bool = False
    is_shadow: bool = False
    is_target: bool = False

    def get_current_section(self) -> str:
        section = "Shadow" if self.is_shadow else ""
        section += "Target" if self.is_target else "Source"
        return section

    def _get_reporting_window_size(self) -> str:
        """
        Returns string of the difference between upper and lower time bound.
        """
        return str(self.upper_time_bound - self.lower_time_bound)

    def to_log_text(self) -> str:
        """
        Returns text representation of the most important properties of the reporting.
        This can be used e.g. for logging purposes.
        """
        severity_type = "target" if self.is_target else "source"
        reporting_type = "shadow" if self.is_shadow else "normal"
        return (
            f"{severity_type} severity '{self.severity}' and time interval "
            f"{self.lower_time_bound.isoformat()} -> {self.upper_time_bound.isoformat()} "
            f"({self._get_reporting_window_size()}). ({reporting_type} reporting)"
        )

    def get_event_search_parameters(self) -> dict[str, Any]:
        """
        Returns search parameters for event searching based on the
        reporting properties represented by this data class.
        """
        parameters: dict[str, Any] = {
            "st_from": self.lower_time_bound,
            "st_to": self.upper_time_bound,
        }

        # Shadow reports are also generated from Test data.
        if not self.has_test_data and not self.is_shadow:
            parameters.update(
                {
                    "categories": ["Test"],
                    "not_categories": True,
                }
            )

        if not self.is_target:
            parameters.update(
                {
                    "groups": [self.group.name],
                    "severities": [self.severity],
                    "shadow_reporting": self.is_shadow,
                }
            )
        else:
            parameters.update(
                {
                    "target_groups": [self.group.name],
                    "target_severities": [self.severity],
                    "shadow_reporting_target": self.is_shadow,
                }
            )

        return parameters
