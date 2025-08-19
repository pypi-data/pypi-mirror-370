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

IGroup_VERSION = "5.3.2852"


class IGroup(BaseEndpoint):
    def __init__(self, apiKey, url, domainUid):
        self.url = url
        self.apiKey = apiKey
        self.base = url + '/groups/{domainUid}'
        self.domainUid_ = domainUid
        self.base = self.base.replace('{domainUid}', domainUid)

    def add(self, uid, members):
        postUri = "/{uid}/members"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        from netbluemind.group.api.Member import Member
        from netbluemind.group.api.Member import __MemberSerDer__
        __data__ = serder.ListSerDer(__MemberSerDer__()).encode(members)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.put(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def allUids(self):
        postUri = "/_alluids"
        __data__ = None
        __encoded__ = None
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        return self.handleResult__(serder.ListSerDer(serder.STRING), response)

    def byEmail(self, email):
        postUri = "/byEmail/{email}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{email}", email)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        from netbluemind.group.api.Group import Group
        from netbluemind.group.api.Group import __GroupSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__GroupSerDer__()), response)

    def byName(self, name):
        postUri = "/byName/{name}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{name}", name)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        from netbluemind.group.api.Group import Group
        from netbluemind.group.api.Group import __GroupSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__GroupSerDer__()), response)

    def create(self, uid, group):
        postUri = "/{uid}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        from netbluemind.group.api.Group import Group
        from netbluemind.group.api.Group import __GroupSerDer__
        __data__ = __GroupSerDer__().encode(group)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.put(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def createWithExtId(self, uid, extid, group):
        postUri = "/{uid}/{extid}/createwithextid"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        postUri = postUri.replace("{extid}", extid)
        from netbluemind.group.api.Group import Group
        from netbluemind.group.api.Group import __GroupSerDer__
        __data__ = __GroupSerDer__().encode(group)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.put(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def delete(self, uid):
        postUri = "/{uid}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {}

        response = requests.delete(self.base + postUri, params=queryParams, verify=False, headers={
                                   'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)

    def get(self, uid):
        postUri = "/{uid}"
        __data__ = None
        __encoded__ = None
        __data__ = serder.STRING.encode(uid)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        from netbluemind.group.api.Group import Group
        from netbluemind.group.api.Group import __GroupSerDer__
        return self.handleResult__(__GroupSerDer__(), response)

    def getByExtId(self, extid):
        postUri = "/_extid/{extid}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{extid}", extid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        from netbluemind.group.api.Group import Group
        from netbluemind.group.api.Group import __GroupSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__GroupSerDer__()), response)

    def getComplete(self, uid):
        postUri = "/{uid}/complete"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        from netbluemind.group.api.Group import Group
        from netbluemind.group.api.Group import __GroupSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__GroupSerDer__()), response)

    def getExpandedMembers(self, uid):
        postUri = "/{uid}/expandedmembers"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        from netbluemind.group.api.Member import Member
        from netbluemind.group.api.Member import __MemberSerDer__
        return self.handleResult__(serder.ListSerDer(__MemberSerDer__()), response)

    def getExpandedUserMembers(self, uid):
        postUri = "/{uid}/expandedusersmembers"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        from netbluemind.group.api.Member import Member
        from netbluemind.group.api.Member import __MemberSerDer__
        return self.handleResult__(serder.ListSerDer(__MemberSerDer__()), response)

    def getGroupsWithRoles(self, roles):
        postUri = "/_rolegroups"
        __data__ = None
        __encoded__ = None
        __data__ = serder.ListSerDer(serder.STRING).encode(roles)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        return self.handleResult__(serder.SetSerDer(serder.STRING), response)

    def getLight(self, uid):
        postUri = "/{uid}/light"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        from netbluemind.group.api.Group import Group
        from netbluemind.group.api.Group import __GroupSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__GroupSerDer__()), response)

    def getMembers(self, uid):
        postUri = "/{uid}/members"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        from netbluemind.group.api.Member import Member
        from netbluemind.group.api.Member import __MemberSerDer__
        return self.handleResult__(serder.ListSerDer(__MemberSerDer__()), response)

    def getParents(self, uid):
        postUri = "/{uid}/parents"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        from netbluemind.group.api.Group import Group
        from netbluemind.group.api.Group import __GroupSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__GroupSerDer__())), response)

    def getRoles(self, uid):
        postUri = "/{uid}/roles"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        return self.handleResult__(serder.SetSerDer(serder.STRING), response)

    def memberOf(self, uid):
        postUri = "/{uid}/groups"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        from netbluemind.group.api.Group import Group
        from netbluemind.group.api.Group import __GroupSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__GroupSerDer__())), response)

    def memberOfGroups(self, uid):
        postUri = "/{uid}/groupUids"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        return self.handleResult__(serder.ListSerDer(serder.STRING), response)

    def remove(self, uid, members):
        postUri = "/{uid}/members"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        from netbluemind.group.api.Member import Member
        from netbluemind.group.api.Member import __MemberSerDer__
        __data__ = serder.ListSerDer(__MemberSerDer__()).encode(members)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.delete(self.base + postUri, params=queryParams, verify=False, headers={
                                   'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def search(self, query):
        postUri = "/_search"
        __data__ = None
        __encoded__ = None
        from netbluemind.group.api.GroupSearchQuery import GroupSearchQuery
        from netbluemind.group.api.GroupSearchQuery import __GroupSearchQuerySerDer__
        __data__ = __GroupSearchQuerySerDer__().encode(query)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        from netbluemind.group.api.Group import Group
        from netbluemind.group.api.Group import __GroupSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__GroupSerDer__())), response)

    def setExtId(self, uid, arg1):
        postUri = "/{uid}/_extId"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        __data__ = serder.STRING.encode(arg1)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def setRoles(self, uid, roles):
        postUri = "/{uid}/roles"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        __data__ = serder.SetSerDer(serder.STRING).encode(roles)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def touch(self, uid, update_vcards):
        postUri = "/{uid}/_touch"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {'update_vcards': update_vcards}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def update(self, uid, group):
        postUri = "/{uid}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        from netbluemind.group.api.Group import Group
        from netbluemind.group.api.Group import __GroupSerDer__
        __data__ = __GroupSerDer__().encode(group)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IGroup_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)
