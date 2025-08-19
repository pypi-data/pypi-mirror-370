# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
This module directly interacts with Bridge web services on
It will log the https requests and responses.
Be sure to set the logging configuration if you use the LiveDao!
"""

import logging
from restclients_core.exceptions import DataFailureException
from uw_bridge.dao import Bridge_DAO


logger = logging.getLogger(__name__)


class Bridge(object):
    DHEADER = {
        "Content-Type": "application/json",
        'Accept': 'application/json'}
    GHEADER = {'Accept': 'application/json'}
    PHEADER = {
        "Content-Type": "application/json",
        'Accept': 'application/json',
        'Connection': 'keep-alive'}

    def __init__(self):
        self.dao = Bridge_DAO()
        self.req_url = None

    def delete_resource(self, url):
        response = self.dao.deleteURL(url, self.DHEADER)
        req_data = "DELETE {0}".format(url)
        self._log_resp(req_data, response)

        if response.status != 204:
            # 204 is a successful deletion
            self._raise_exception(req_data, url, response)

        return response

    def get_resource(self, url):
        self.req_url = url
        response = self.dao.getURL(url, self.GHEADER)
        req_data = "GET {0}".format(url)
        self._log_resp(req_data, response)

        if response.status != 200:
            self._raise_exception(req_data, url, response)

        return response.data

    def patch_resource(self, url, body):
        """
        Patch resource with the given json body
        :returns: http response data
        """
        self.req_url = url
        response = self.dao.patchURL(url, self.PHEADER, body)
        req_data = "PATCH {0}: {1}".format(url, body)
        self._log_resp(req_data, response)

        if response.status != 200:
            self._raise_exception(req_data, url, response)

        return response.data

    def post_resource(self, url, body):
        """
        Post resource with the given json body
        :returns: http response data
        """
        self.req_url = url
        response = self.dao.postURL(url, self.PHEADER, body)
        req_data = "POST {0}: {1}".format(url, body)
        self._log_resp(req_data, response)

        if response.status != 200 and response.status != 201:
            self._raise_exception(req_data, url, response)

        return response.data

    def put_resource(self, url, body):
        """
        Update the entire resource
        Bridge PUT seems to have the same effect as PATCH currently.
        """
        self.req_url = url
        response = self.dao.putURL(url, self.PHEADER, body)
        req_data = "PUT {0}: {1}".format(url, body)
        self._log_resp(req_data, response)

        if response.status != 200:
            self._raise_exception(req_data, url, response)

        return response.data

    def _log_resp(self, req_data, response):
        logger.debug(" {0} ===> STATUS: {1:d}, DATA: {2}".format(
            req_data, response.status, response.data))

    def _raise_exception(self, req_data, url, response):
        if response.status == 404:
            logger.warning(
                " {0} ===> {1}".format(req_data, response.status))
        else:
            logger.error(" {0} ===> {1}, {2}".format(
                req_data, response.status, response.data))
        raise DataFailureException(url, response.status, response.data)
