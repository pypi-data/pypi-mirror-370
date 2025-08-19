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

ITodoListsMgmt_VERSION = "5.3.2852"


class ITodoListsMgmt(BaseEndpoint):
    def __init__(self, apiKey, url):
        self.url = url
        self.apiKey = apiKey
        self.base = url + '/mgmt/todolists'

    def create(self, containerUid, descriptor, isDefault):
        postUri = "/{containerUid}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{containerUid}", containerUid)
        from netbluemind.core.container.model.ContainerDescriptor import ContainerDescriptor
        from netbluemind.core.container.model.ContainerDescriptor import __ContainerDescriptorSerDer__
        __data__ = __ContainerDescriptorSerDer__().encode(descriptor)
        __encoded__ = json.dumps(__data__)
        queryParams = {'isDefault': isDefault}

        response = requests.put(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': ITodoListsMgmt_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def getComplete(self, containerUid):
        postUri = "/{containerUid}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{containerUid}", containerUid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': ITodoListsMgmt_VERSION}, data=__encoded__)
        from netbluemind.core.container.model.ContainerDescriptor import ContainerDescriptor
        from netbluemind.core.container.model.ContainerDescriptor import __ContainerDescriptorSerDer__
        return self.handleResult__(__ContainerDescriptorSerDer__(), response)

    def reindex(self, containerUid):
        postUri = "/{containerUid}/_reindex"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{containerUid}", containerUid)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': ITodoListsMgmt_VERSION}, data=__encoded__)
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)

    def reindexAll(self):
        postUri = "/_reindex"
        __data__ = None
        __encoded__ = None
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': ITodoListsMgmt_VERSION}, data=__encoded__)
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)

    def update(self, containerUid, descriptor):
        postUri = "/{containerUid}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{containerUid}", containerUid)
        from netbluemind.core.container.model.ContainerDescriptor import ContainerDescriptor
        from netbluemind.core.container.model.ContainerDescriptor import __ContainerDescriptorSerDer__
        __data__ = __ContainerDescriptorSerDer__().encode(descriptor)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': ITodoListsMgmt_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)
