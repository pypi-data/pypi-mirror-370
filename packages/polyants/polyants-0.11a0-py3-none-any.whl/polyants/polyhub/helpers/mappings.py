""" This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Created on Mar 27, 2025

@author: pymancer@gmail.com (polyanalitika.ru)
"""

from polyants.polyhub.constants import (
    REPORTS_ROOT,
    DAGSTER_ALERTS_ROOT,
    DAGSTER_REPORTS_ROOT,
    DAGSTER_SKIPPER_ROOT,
    ALERT_HOSTNAME,
    REPORT_HOSTNAME,
    BACK_HOSTNAME,
    SKIPPER_HOSTNAME,
    SWAP_ROOT,
    DAGSTER_SWAP_ROOT,
)
from polyants.polyhub.enums import AlertFormat, ReportInstanceFormat

ALERT_REPORT_FORMATS = {
    AlertFormat.TXT: ReportInstanceFormat.TXT,
    AlertFormat.HTML: ReportInstanceFormat.HTML,
    AlertFormat.MD: ReportInstanceFormat.HTML,
    ReportInstanceFormat.TXT: AlertFormat.TXT,
    ReportInstanceFormat.HTML: AlertFormat.HTML,
}

ROOTS = {
    BACK_HOSTNAME: REPORTS_ROOT,
    ALERT_HOSTNAME: DAGSTER_ALERTS_ROOT,
    REPORT_HOSTNAME: DAGSTER_REPORTS_ROOT,
    SKIPPER_HOSTNAME: DAGSTER_SKIPPER_ROOT,
}

SWAPS = {
    BACK_HOSTNAME: SWAP_ROOT,
    ALERT_HOSTNAME: DAGSTER_SWAP_ROOT,
    REPORT_HOSTNAME: DAGSTER_SWAP_ROOT,
    SKIPPER_HOSTNAME: DAGSTER_SWAP_ROOT,
}
