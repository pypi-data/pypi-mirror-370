# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interacte with Bridge Users API.
You only need a single Users object in your app.
"""

import json
import logging
import re
from uw_bridge.custom_fields import CustomFields
from uw_bridge.models import BridgeUser
from uw_bridge.user_roles import UserRoles
from uw_bridge.util import parse_date
from uw_bridge import Bridge


logger = logging.getLogger(__name__)
ADMIN_URL_PREFIX = "/api/admin/users"
AUTHOR_URL_PREFIX = "/api/author/users"
GET_USER_INCLUDES = ['custom_fields', 'course_summary', 'manager']
RESTORE_INCLUDES = ['custom_fields', 'manager']
PAGE_MAX_ENTRY = 1000
RESTORE_SUFFIX = "restore"


def admin_id_url(bridge_id):
    url = ADMIN_URL_PREFIX
    if bridge_id:
        url = "{0}/{1:d}".format(url, bridge_id)
    return url


def admin_uid_url(uwnetid):
    url = ADMIN_URL_PREFIX
    if uwnetid is not None:
        url = "{0}/uid%3A{1}%40uw%2Eedu".format(url, uwnetid)
    return url


def author_id_url(bridge_id):
    url = AUTHOR_URL_PREFIX
    if bridge_id:
        url = "{0}/{1:d}".format(url, bridge_id)
    return url


def author_uid_url(uwnetid):
    url = AUTHOR_URL_PREFIX
    if uwnetid is not None:
        url = "{0}/uid%3A{1}%40uw%2Eedu".format(url, uwnetid)
    return url


def includes_to_query_params(includes):
    return '&'.join("includes%5B%5D={0}".format(e) for e in includes)


def get_all_users_url(includes, role_id):
    if includes is None:
        url = "{0}?includes%5B%5D=".format(author_uid_url(None))
    else:
        url = "{0}?{1}".format(author_uid_url(None),
                               includes_to_query_params(includes))
    if role_id is not None:
        url = "{0}&role={1}".format(url, role_id)

    return "{0}&limit={1}".format(url, PAGE_MAX_ENTRY)


def restore_user_url(base_url):
    return "{0}/{1}?{2}".format(base_url, RESTORE_SUFFIX,
                                includes_to_query_params(RESTORE_INCLUDES))


class BridgeAccounts(Bridge):

    def __init__(self):
        super(BridgeAccounts, self).__init__()
        self.custom_fields = CustomFields(self)
        self.user_roles = UserRoles(self)

    def add_user(self, bridge_user):
        """
        Add the given bridge_user
        :param bridge_user: the BridgeUser object to be created
        Return the BridgeUser object created
        """
        url = admin_uid_url(None)
        body = json.dumps(bridge_user.to_json_post(), separators=(',', ':'))
        resp = self.post_resource(url, body)
        return self._get_obj_from_list("add_user ({0})".format(bridge_user),
                                       self._process_json_resp_data(resp))

    def _upd_uid_req_body(self, new_uwnetid):
        return "{0}{1}@uw.edu{2}".format(
            '{"user":{"uid":"', new_uwnetid, '"}}')

    def change_uid(self, bridge_id, new_uwnetid):
        """
        :param bridge_id: integer
        :param no_custom_fields: specify if you want custom_fields
                                 in the response.
        Return a BridgeUser object
        """
        url = author_id_url(bridge_id)
        resp = self.patch_resource(url, self._upd_uid_req_body(new_uwnetid))
        return self._get_obj_from_list("change_uid({0})".format(new_uwnetid),
                                       self._process_json_resp_data(resp))

    def replace_uid(self, old_uwnetid, new_uwnetid):
        """
        :param old_uwnetid, new_uwnetid: UwNetID strings
        :param no_custom_fields: specify if you want custom_fields
                                 in the response.
        Return a BridgeUser object
        """
        url = author_uid_url(old_uwnetid)
        resp = self.patch_resource(url, self._upd_uid_req_body(new_uwnetid))
        return self._get_obj_from_list(
            "replace_uid({0}->{1})".format(old_uwnetid, new_uwnetid),
            self._process_json_resp_data(resp))

    def delete_user(self, uwnetid):
        """
        Return True when the HTTP repsonse status is 204 -
        the user is deleted successfully
        """
        resp = self.delete_resource(admin_uid_url(uwnetid))
        return resp.status == 204

    def delete_user_by_id(self, bridge_id):
        """
        :param bridge_id: integer
        Return True when the HTTP repsonse status is 204 -
        the user is deleted successfully
        """
        resp = self.delete_resource(admin_id_url(bridge_id))
        return resp.status == 204

    def get_user(self, uwnetid):
        """
        Return a BridgeUser object
        """
        url = "{0}?{1}".format(author_uid_url(uwnetid),
                               includes_to_query_params(GET_USER_INCLUDES))
        resp = self.get_resource(url)
        return self._get_obj_from_list(
            "get_user by netid('{0}')".format(uwnetid),
            self._process_json_resp_data(resp))

    def get_user_by_id(self, bridge_id,
                       include_deleted=False):
        """
        :param bridge_id: integer
        :param include_deleted: specify if you want to include
                                terminated user record in the response.
        Return a BridgeUser object
        """
        url = "{0}?{1}".format(author_id_url(bridge_id),
                               includes_to_query_params(GET_USER_INCLUDES))
        if include_deleted:
            url = "{0}&{1}".format(url, "with_deleted=true")

        resp = self.get_resource(url)
        return self._get_obj_from_list(
            "get_user by bridge_id('{0}')".format(bridge_id),
            self._process_json_resp_data(resp))

    def get_all_users(self, includes=None, role_id=None):
        """
        :param includes: specify the additioanl data you want in the response.
        :param role_id: filter users by role_id
         Valid value is one of 'account_admin', 'admin', 'author', etc
        Return a list of BridgeUser objects of the active user records.
        """
        resp = self.get_resource(get_all_users_url(includes, role_id))
        return self._process_json_resp_data(resp)

    def restore_user(self, uwnetid):
        """
        :param includes: specify the additioanl data you want in the response.
         Valid value is: ['custom_fields', 'course_summary', 'manager']
        Return a BridgeUser object
        """
        url = restore_user_url(author_uid_url(uwnetid))
        resp = self.post_resource(url, '{}')
        return self._get_obj_from_list(
            "restore_user by netid({0})".format(uwnetid),
            self._process_json_resp_data(resp))

    def restore_user_by_id(self, bridge_id):
        """
        :param bridge_id: integer
        :param includes: specify the additioanl data you want in the response.
         Valid value is: ['custom_fields', 'course_summary', 'manager']
        return a BridgeUser object
        """
        url = restore_user_url(author_id_url(bridge_id))
        resp = self.post_resource(url, '{}')
        return self._get_obj_from_list(
            "restore_user by bridge_id({0})".format(bridge_id),
            self._process_json_resp_data(resp))

    def update_user(self, bridge_user):
        """
        Update only the user attributes provided.
        Return a BridgeUser object
        """
        if bridge_user.has_bridge_id():
            url = author_id_url(bridge_user.bridge_id)
        else:
            url = author_uid_url(bridge_user.netid)
        body = json.dumps(bridge_user.to_json_patch(), separators=(',', ':'))
        resp = self.patch_resource(url, body)
        return self._get_obj_from_list(
            "update_user ({0})".format(bridge_user.to_json()),
            self._process_json_resp_data(resp))

    def update_user_roles(self, bridge_user):
        """
        Update the all the permission roles for the bridge_user.
        Return a BridgeUser object
        """
        if bridge_user.has_bridge_id():
            url = admin_id_url(bridge_user.bridge_id)
        else:
            url = admin_uid_url(bridge_user.netid)
        url = "{0}/roles/batch".format(url)
        body = json.dumps({"roles": bridge_user.roles_to_json()})
        resp = self.put_resource(url, body)
        return self._get_obj_from_list(
            "update_user_roles {0}, {1}".format(bridge_user.netid, body),
            self._process_json_resp_data(resp))

    def _process_json_resp_data(self, resp):
        """
        process the response and return a list of BridgeUser
        """
        bridge_users = []
        while True:
            resp_data = json.loads(resp)
            link_url = None
            if (resp_data.get("meta") is not None and
                    resp_data["meta"].get("next") is not None):
                link_url = resp_data["meta"]["next"]

            try:
                bridge_users = self._process_apage(resp_data, bridge_users)
            except Exception as err:
                logger.error("{0} in {1}".format(str(err), resp_data))

            if link_url is None:
                break
            resp = self.get_resource(link_url)
        return bridge_users

    def _process_apage(self, resp_data, bridge_users):
        custom_fields_value_dict = self._get_custom_fields_dict(
            resp_data.get("linked"))
        # a dict of {custom_field_value_id: BridgeCustomField}

        for user_data in resp_data.get("users"):
            try:
                user = BridgeUser(
                    bridge_id=int(user_data["id"]),
                    netid=re.sub('@uw.edu', '', user_data["uid"]),
                    email=user_data.get("email", ""),
                    full_name=user_data.get("full_name", ""),
                    first_name=user_data.get("first_name"),
                    last_name=user_data.get("last_name"),
                    department=user_data.get("department"),
                    job_title=user_data.get("job_title"),
                    locale=user_data.get("locale", "en"),
                    hired_at=parse_date(user_data.get("hire_date")),
                    is_manager=user_data.get("is_manager"),
                    unsubscribed=user_data.get("unsubscribed"),
                    deleted_at=parse_date(user_data.get("deleted_at")),
                    logged_in_at=parse_date(user_data.get("loggedInAt")),
                    updated_at=parse_date(user_data.get("updated_at")),
                    next_due_date=parse_date(user_data.get("next_due_date")),
                    completed_courses_count=user_data.get(
                        "completed_courses_count", -1))

                if user_data.get("manager_id") is not None:
                    user.manager_id = int(user_data["manager_id"])

                if (user_data.get("links") is not None and
                        len(user_data["links"]) > 0 and
                        "custom_field_values" in user_data["links"]):
                    values = user_data["links"]["custom_field_values"]
                    for custom_field_value in values:
                        if custom_field_value in custom_fields_value_dict:
                            custom_field = custom_fields_value_dict[
                                custom_field_value]
                            user.custom_fields[custom_field.name] =\
                                custom_field

                if user_data.get("roles") is not None:
                    for role_data in user_data["roles"]:
                        user.roles.append(
                            self.user_roles.new_user_role_by_id(role_data))
                bridge_users.append(user)
            except Exception as err:
                logger.error("{0} in {1}".format(str(err), user_data))
        return bridge_users

    def _get_custom_fields_dict(self, linked_data):
        """
        :except KeyError:
        """
        custom_fields_value_dict = {}
        # a dict of {value_id: BridgeCustomField}

        if (len(linked_data) == 0 or
                linked_data.get("custom_field_values") is None):
            return custom_fields_value_dict

        for value in linked_data["custom_field_values"]:
            custom_field = self.custom_fields.get_custom_field(
                value["links"]["custom_field"]["id"],
                value["id"], value["value"])
            custom_fields_value_dict[custom_field.value_id] = custom_field
        return custom_fields_value_dict

    def _get_obj_from_list(self, action, rlist):
        if len(rlist) == 0:
            return None

        if len(rlist) > 1:
            logger.error(
                "{0} returns multiple Bridge user accounts: {1}".format(
                    action, [u.to_json() for u in rlist]))
        return rlist[0]
