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

IUserCalendarViews_VERSION = "5.3.2852"


class IUserCalendarViews(BaseEndpoint):
    def __init__(self, apiKey, url, domainUid, userUid):
        self.url = url
        self.apiKey = apiKey
        self.base = url + '/users/{domainUid}/{userUid}/calendar-views'
        self.domainUid_ = domainUid
        self.base = self.base.replace('{domainUid}', domainUid)
        self.userUid_ = userUid
        self.base = self.base.replace('{userUid}', userUid)

    def changeset(self, since):
        postUri = "/_changeset"
        __data__ = None
        __encoded__ = None
        queryParams = {'since': since}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IUserCalendarViews_VERSION}, data=__encoded__)
        from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
        from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
        return self.handleResult__(__ContainerChangesetSerDer__(serder.STRING), response)

    def changesetById(self, since):
        postUri = "/_changesetById"
        __data__ = None
        __encoded__ = None
        queryParams = {'since': since}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IUserCalendarViews_VERSION}, data=__encoded__)
        from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
        from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
        return self.handleResult__(__ContainerChangesetSerDer__(serder.LONG), response)

    def create(self, uid, view):
        postUri = "/{uid}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        from netbluemind.calendar.api.CalendarView import CalendarView
        from netbluemind.calendar.api.CalendarView import __CalendarViewSerDer__
        __data__ = __CalendarViewSerDer__().encode(view)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.put(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IUserCalendarViews_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def delete(self, uid):
        postUri = "/{uid}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {}

        response = requests.delete(self.base + postUri, params=queryParams, verify=False, headers={
                                   'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IUserCalendarViews_VERSION}, data=__encoded__)
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
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IUserCalendarViews_VERSION}, data=__encoded__)
        from netbluemind.core.container.model.ItemVersion import ItemVersion
        from netbluemind.core.container.model.ItemVersion import __ItemVersionSerDer__
        from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
        from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
        return self.handleResult__(__ContainerChangesetSerDer__(__ItemVersionSerDer__()), response)

    def getComplete(self, uid):
        postUri = "/{uid}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IUserCalendarViews_VERSION}, data=__encoded__)
        from netbluemind.calendar.api.CalendarView import CalendarView
        from netbluemind.calendar.api.CalendarView import __CalendarViewSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__CalendarViewSerDer__()), response)

    def getCompleteById(self, id):
        postUri = "/{id}/completeById"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{id}", id)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IUserCalendarViews_VERSION}, data=__encoded__)
        from netbluemind.calendar.api.CalendarView import CalendarView
        from netbluemind.calendar.api.CalendarView import __CalendarViewSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__CalendarViewSerDer__()), response)

    def getVersion(self):
        postUri = "/_version"
        __data__ = None
        __encoded__ = None
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IUserCalendarViews_VERSION}, data=__encoded__)
        return self.handleResult__(serder.LONG, response)

    def list(self):
        postUri = "/_list"
        __data__ = None
        __encoded__ = None
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IUserCalendarViews_VERSION}, data=__encoded__)
        from netbluemind.calendar.api.CalendarView import CalendarView
        from netbluemind.calendar.api.CalendarView import __CalendarViewSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        from netbluemind.core.api.ListResult import ListResult
        from netbluemind.core.api.ListResult import __ListResultSerDer__
        return self.handleResult__(__ListResultSerDer__(__ItemValueSerDer__(__CalendarViewSerDer__())), response)

    def multipleGet(self, uids):
        postUri = "/_mget"
        __data__ = None
        __encoded__ = None
        __data__ = serder.ListSerDer(serder.STRING).encode(uids)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IUserCalendarViews_VERSION}, data=__encoded__)
        from netbluemind.calendar.api.CalendarView import CalendarView
        from netbluemind.calendar.api.CalendarView import __CalendarViewSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__CalendarViewSerDer__())), response)

    def multipleGetById(self, arg0):
        postUri = "/_mgetById"
        __data__ = None
        __encoded__ = None
        __data__ = serder.ListSerDer(serder.LONG).encode(arg0)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IUserCalendarViews_VERSION}, data=__encoded__)
        from netbluemind.calendar.api.CalendarView import CalendarView
        from netbluemind.calendar.api.CalendarView import __CalendarViewSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__CalendarViewSerDer__())), response)

    def setDefault(self, uid):
        postUri = "/{uid}/_asdefault"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IUserCalendarViews_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def update(self, uid, view):
        postUri = "/{uid}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        from netbluemind.calendar.api.CalendarView import CalendarView
        from netbluemind.calendar.api.CalendarView import __CalendarViewSerDer__
        __data__ = __CalendarViewSerDer__().encode(view)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IUserCalendarViews_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def updates(self, changes):
        postUri = "/_mupdates"
        __data__ = None
        __encoded__ = None
        from netbluemind.calendar.api.CalendarViewChanges import CalendarViewChanges
        from netbluemind.calendar.api.CalendarViewChanges import __CalendarViewChangesSerDer__
        __data__ = __CalendarViewChangesSerDer__().encode(changes)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.put(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IUserCalendarViews_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)
