#
#  BEGIN LICENSE
#  Copyright (c) Blue Mind SAS, 2012-2016
#
#  This file is part of BlueMind. BlueMind is a messaging and collaborative
#  solution.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of either the GNU Affero General Public License as
#  published by the Free Software Foundation (version 3 of the License).
#
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  See LICENSE.txt
#  END LICENSE
#
import requests
import json
from netbluemind.python import serder
from netbluemind.python.client import BaseEndpoint

IChangesetCleanup_VERSION = "5.3.2852"


class IChangesetCleanup(BaseEndpoint):
    def __init__(self, apiKey, url, serverUid):
        self.url = url
        self.apiKey = apiKey
        self.base = url + '/changeset_cleanup/{serverUid}'
        self.serverUid_ = serverUid
        self.base = self.base.replace('{serverUid}', serverUid)

    def deleteOldDeletedChangesetItems(self, days):
        postUri = "/_delete_old_changeset_items"
        __data__ = None
        __encoded__ = None
        queryParams = {'days': days}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IChangesetCleanup_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)
