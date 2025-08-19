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

IWebAppData_VERSION = "5.3.2852"


class IWebAppData(BaseEndpoint):
    def __init__(self, apiKey, url, containerUid):
        self.url = url
        self.apiKey = apiKey
        self.base = url + '/webappdata/{containerUid}'
        self.containerUid_ = containerUid
        self.base = self.base.replace('{containerUid}', containerUid)

    def allUids(self):
        postUri = "/_alluids"
        __data__ = None
        __encoded__ = None
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IWebAppData_VERSION}, data=__encoded__)
        return self.handleResult__(serder.ListSerDer(serder.STRING), response)

    def changeset(self, since):
        postUri = "/_changeset"
        __data__ = None
        __encoded__ = None
        queryParams = {'since': since}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IWebAppData_VERSION}, data=__encoded__)
        from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
        from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
        return self.handleResult__(__ContainerChangesetSerDer__(serder.STRING), response)

    def changesetById(self, since):
        postUri = "/_changesetById"
        __data__ = None
        __encoded__ = None
        queryParams = {'since': since}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IWebAppData_VERSION}, data=__encoded__)
        from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
        from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
        return self.handleResult__(__ContainerChangesetSerDer__(serder.LONG), response)

    def create(self, uid, arg1):
        postUri = "/uid/{uid}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        from netbluemind.webappdata.api.WebAppData import WebAppData
        from netbluemind.webappdata.api.WebAppData import __WebAppDataSerDer__
        __data__ = __WebAppDataSerDer__().encode(arg1)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.put(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IWebAppData_VERSION}, data=__encoded__)
        from netbluemind.core.container.api.Ack import Ack
        from netbluemind.core.container.api.Ack import __AckSerDer__
        return self.handleResult__(__AckSerDer__(), response)

    def delete(self, uid):
        postUri = "/uid/{uid}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {}

        response = requests.delete(self.base + postUri, params=queryParams, verify=False, headers={
                                   'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IWebAppData_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def deleteAll(self):
        postUri = "/_deleteAll"
        __data__ = None
        __encoded__ = None
        queryParams = {}

        response = requests.delete(self.base + postUri, params=queryParams, verify=False, headers={
                                   'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IWebAppData_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def filteredChangesetById(self, since, arg1):
        postUri = "/_filteredChangesetById"
        __data__ = None
        __encoded__ = None
        from netbluemind.core.container.model.ItemFlagFilter import ItemFlagFilter
        from netbluemind.core.container.model.ItemFlagFilter import __ItemFlagFilterSerDer__
        __data__ = __ItemFlagFilterSerDer__().encode(arg1)
        __encoded__ = json.dumps(__data__)
        queryParams = {'since': since}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IWebAppData_VERSION}, data=__encoded__)
        from netbluemind.core.container.model.ItemVersion import ItemVersion
        from netbluemind.core.container.model.ItemVersion import __ItemVersionSerDer__
        from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
        from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
        return self.handleResult__(__ContainerChangesetSerDer__(__ItemVersionSerDer__()), response)

    def getByKey(self, key):
        postUri = "/key/{key}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{key}", key)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IWebAppData_VERSION}, data=__encoded__)
        from netbluemind.webappdata.api.WebAppData import WebAppData
        from netbluemind.webappdata.api.WebAppData import __WebAppDataSerDer__
        return self.handleResult__(__WebAppDataSerDer__(), response)

    def getComplete(self, uid):
        postUri = "/uid/{uid}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IWebAppData_VERSION}, data=__encoded__)
        from netbluemind.webappdata.api.WebAppData import WebAppData
        from netbluemind.webappdata.api.WebAppData import __WebAppDataSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__WebAppDataSerDer__()), response)

    def getCompleteById(self, id):
        postUri = "/{id}/completeById"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{id}", id)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IWebAppData_VERSION}, data=__encoded__)
        from netbluemind.webappdata.api.WebAppData import WebAppData
        from netbluemind.webappdata.api.WebAppData import __WebAppDataSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__WebAppDataSerDer__()), response)

    def getVersion(self):
        postUri = "/_version"
        __data__ = None
        __encoded__ = None
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IWebAppData_VERSION}, data=__encoded__)
        return self.handleResult__(serder.LONG, response)

    def itemChangelog(self, uid, arg1):
        postUri = "/{uid}/_itemchangelog"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        __data__ = serder.LONG.encode(arg1)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IWebAppData_VERSION}, data=__encoded__)
        from netbluemind.core.container.model.ItemChangelog import ItemChangelog
        from netbluemind.core.container.model.ItemChangelog import __ItemChangelogSerDer__
        return self.handleResult__(__ItemChangelogSerDer__(), response)

    def multipleGet(self, arg0):
        postUri = "/uid/_mget"
        __data__ = None
        __encoded__ = None
        __data__ = serder.ListSerDer(serder.STRING).encode(arg0)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IWebAppData_VERSION}, data=__encoded__)
        from netbluemind.webappdata.api.WebAppData import WebAppData
        from netbluemind.webappdata.api.WebAppData import __WebAppDataSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__WebAppDataSerDer__())), response)

    def multipleGetById(self, arg0):
        postUri = "/_mgetById"
        __data__ = None
        __encoded__ = None
        __data__ = serder.ListSerDer(serder.LONG).encode(arg0)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IWebAppData_VERSION}, data=__encoded__)
        from netbluemind.webappdata.api.WebAppData import WebAppData
        from netbluemind.webappdata.api.WebAppData import __WebAppDataSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__WebAppDataSerDer__())), response)

    def update(self, uid, arg1):
        postUri = "/uid/{uid}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        from netbluemind.webappdata.api.WebAppData import WebAppData
        from netbluemind.webappdata.api.WebAppData import __WebAppDataSerDer__
        __data__ = __WebAppDataSerDer__().encode(arg1)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IWebAppData_VERSION}, data=__encoded__)
        from netbluemind.core.container.api.Ack import Ack
        from netbluemind.core.container.api.Ack import __AckSerDer__
        return self.handleResult__(__AckSerDer__(), response)
