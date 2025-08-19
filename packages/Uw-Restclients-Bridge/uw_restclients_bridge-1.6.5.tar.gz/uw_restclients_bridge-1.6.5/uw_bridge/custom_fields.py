# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interacte with Bridge custom_fields API.
You only need a single CustomFields object in your app.
"""

import logging
import json
from uw_bridge.models import BridgeCustomField


logger = logging.getLogger(__name__)
URL = "/api/author/custom_fields"


class CustomFields(object):

    def __init__(self, bridge):
        self.bridge = bridge
        self.fields = []
        self.name_id_map = {}
        self.id_name_map = {}
        self.get_custom_fields()

    def get_custom_fields(self):
        resp = self.bridge.get_resource(URL)
        resp_data = json.loads(resp)
        for field in resp_data["custom_fields"]:
            if field.get("id") is not None and field.get("name") is not None:
                cf = BridgeCustomField(field_id=field["id"],
                                       name=field["name"].lower())
                self.fields.append(cf)
                self.name_id_map[cf.name] = cf.field_id
                self.id_name_map[cf.field_id] = cf.name

    def get_fields(self):
        """
        return the list of BridgeCustomField objects
        """
        return self.fields

    def get_field_id(self, field_name):
        return self.name_id_map.get(field_name)

    def get_field_name(self, field_id):
        return self.id_name_map.get(field_id)

    def new_custom_field(self,
                         field_name,
                         field_value):
        """
        Return a new BridgeCustomField object
        to be used in a POST (add new), PATCH (update) request
        :param field_name: use field name defined in models.BridgeCustomField
        """
        return BridgeCustomField(field_id=self.get_field_id(field_name),
                                 name=field_name,
                                 value=field_value)

    def get_custom_field(self,
                         field_id,
                         value_id,
                         value):
        """
        Return a new BridgeCustomField object
        """
        return BridgeCustomField(field_id=field_id,
                                 name=self.get_field_name(field_id),
                                 value_id=value_id,
                                 value=value)
