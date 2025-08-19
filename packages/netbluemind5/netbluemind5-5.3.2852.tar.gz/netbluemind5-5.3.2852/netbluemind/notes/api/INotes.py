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

INotes_VERSION = "5.3.2852"


class INotes(BaseEndpoint):
    def __init__(self, apiKey, url):
        self.url = url
        self.apiKey = apiKey
        self.base = url + '/notes'

    def create(self, uid, descriptor):
        postUri = "/{uid}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        from netbluemind.core.container.model.ContainerDescriptor import ContainerDescriptor
        from netbluemind.core.container.model.ContainerDescriptor import __ContainerDescriptorSerDer__
        __data__ = __ContainerDescriptorSerDer__().encode(descriptor)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.put(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': INotes_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def delete(self, uid):
        postUri = "/{uid}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {}

        response = requests.delete(self.base + postUri, params=queryParams, verify=False, headers={
                                   'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': INotes_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def search(self, query):
        postUri = "/_search"
        __data__ = None
        __encoded__ = None
        from netbluemind.notes.api.VNotesQuery import VNotesQuery
        from netbluemind.notes.api.VNotesQuery import __VNotesQuerySerDer__
        __data__ = __VNotesQuerySerDer__().encode(query)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': INotes_VERSION}, data=__encoded__)
        from netbluemind.notes.api.VNote import VNote
        from netbluemind.notes.api.VNote import __VNoteSerDer__
        from netbluemind.core.container.model.ItemContainerValue import ItemContainerValue
        from netbluemind.core.container.model.ItemContainerValue import __ItemContainerValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemContainerValueSerDer__(__VNoteSerDer__())), response)
