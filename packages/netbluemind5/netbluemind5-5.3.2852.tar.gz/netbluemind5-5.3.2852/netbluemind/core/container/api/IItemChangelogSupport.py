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

IItemChangelogSupport_VERSION = "5.3.2852"


class IItemChangelogSupport(BaseEndpoint):
    def __init__(self, apiKey, url):
        self.url = url
        self.apiKey = apiKey
        self.base = url + ''

    def itemChangelog(self, uid, since):
        postUri = "/{uid}/_itemchangelog"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        __data__ = serder.LONG.encode(since)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IItemChangelogSupport_VERSION}, data=__encoded__)
        from netbluemind.core.container.model.ItemChangelog import ItemChangelog
        from netbluemind.core.container.model.ItemChangelog import __ItemChangelogSerDer__
        return self.handleResult__(__ItemChangelogSerDer__(), response)
