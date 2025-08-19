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

IInternalContainersByLocation_VERSION = "5.3.2852"


class IInternalContainersByLocation(BaseEndpoint):
    def __init__(self, apiKey, url, location):
        self.url = url
        self.apiKey = apiKey
        self.base = url + '/containers/{location}/_by_location'
        self.location_ = location
        self.base = self.base.replace('{location}', location)

    def listByType(self, query):
        postUri = "/list_by_type"
        __data__ = None
        __encoded__ = None
        from netbluemind.core.container.api.ContainerQuery import ContainerQuery
        from netbluemind.core.container.api.ContainerQuery import __ContainerQuerySerDer__
        __data__ = __ContainerQuerySerDer__().encode(query)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IInternalContainersByLocation_VERSION}, data=__encoded__)
        from netbluemind.core.container.model.BaseContainerDescriptor import BaseContainerDescriptor
        from netbluemind.core.container.model.BaseContainerDescriptor import __BaseContainerDescriptorSerDer__
        return self.handleResult__(serder.ListSerDer(__BaseContainerDescriptorSerDer__()), response)
