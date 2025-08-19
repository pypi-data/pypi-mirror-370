# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from commonconf import override_settings
from dateutil.parser import parse


fdao_bridge_override = override_settings(RESTCLIENTS_BRIDGE_DAO_CLASS='Mock')
ldao_bridge_override = override_settings(RESTCLIENTS_BRIDGE_DAO_CLASS='Live')


def parse_date(date_str):
    if date_str is not None:
        return parse(date_str)
    return None


def date_to_str(dt):
    # datetime.datetime.isoformat
    return dt.isoformat() if dt is not None else None
