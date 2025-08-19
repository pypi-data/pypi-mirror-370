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

IMailConversationActions_VERSION = "5.3.2852"


class IMailConversationActions(BaseEndpoint):
    def __init__(self, apiKey, url, conversationContainer, replicatedMailboxUid):
        self.url = url
        self.apiKey = apiKey
        self.base = url + \
            '/mail_conversation/{conversationContainer}/{replicatedMailboxUid}'
        self.conversationContainer_ = conversationContainer
        self.base = self.base.replace(
            '{conversationContainer}', conversationContainer)
        self.replicatedMailboxUid_ = replicatedMailboxUid
        self.base = self.base.replace(
            '{replicatedMailboxUid}', replicatedMailboxUid)

    def addFlag(self, flagUpdate):
        postUri = "/_addFlag"
        __data__ = None
        __encoded__ = None
        from netbluemind.backend.mail.api.flags.ConversationFlagUpdate import ConversationFlagUpdate
        from netbluemind.backend.mail.api.flags.ConversationFlagUpdate import __ConversationFlagUpdateSerDer__
        __data__ = __ConversationFlagUpdateSerDer__().encode(flagUpdate)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.put(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailConversationActions_VERSION}, data=__encoded__)
        from netbluemind.core.container.api.Ack import Ack
        from netbluemind.core.container.api.Ack import __AckSerDer__
        return self.handleResult__(__AckSerDer__(), response)

    def copy(self, targetMailboxUid, conversationUids):
        postUri = "/copy/{targetMailboxUid}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{targetMailboxUid}", targetMailboxUid)
        __data__ = serder.ListSerDer(serder.STRING).encode(conversationUids)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailConversationActions_VERSION}, data=__encoded__)
        from netbluemind.core.container.model.ItemIdentifier import ItemIdentifier
        from netbluemind.core.container.model.ItemIdentifier import __ItemIdentifierSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemIdentifierSerDer__()), response)

    def deleteFlag(self, flagUpdate):
        postUri = "/_deleteFlag"
        __data__ = None
        __encoded__ = None
        from netbluemind.backend.mail.api.flags.ConversationFlagUpdate import ConversationFlagUpdate
        from netbluemind.backend.mail.api.flags.ConversationFlagUpdate import __ConversationFlagUpdateSerDer__
        __data__ = __ConversationFlagUpdateSerDer__().encode(flagUpdate)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.put(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailConversationActions_VERSION}, data=__encoded__)
        from netbluemind.core.container.api.Ack import Ack
        from netbluemind.core.container.api.Ack import __AckSerDer__
        return self.handleResult__(__AckSerDer__(), response)

    def importItems(self, folderDestinationId, mailboxItems):
        postUri = "/importItems/{folderDestinationId}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{folderDestinationId}", folderDestinationId)
        from netbluemind.backend.mail.api.flags.ImportMailboxConversationSet import ImportMailboxConversationSet
        from netbluemind.backend.mail.api.flags.ImportMailboxConversationSet import __ImportMailboxConversationSetSerDer__
        __data__ = __ImportMailboxConversationSetSerDer__().encode(mailboxItems)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.put(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailConversationActions_VERSION}, data=__encoded__)
        from netbluemind.backend.mail.api.ImportMailboxItemsStatus import ImportMailboxItemsStatus
        from netbluemind.backend.mail.api.ImportMailboxItemsStatus import __ImportMailboxItemsStatusSerDer__
        return self.handleResult__(__ImportMailboxItemsStatusSerDer__(), response)

    def move(self, targetMailboxUid, conversationUids):
        postUri = "/move/{targetMailboxUid}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{targetMailboxUid}", targetMailboxUid)
        __data__ = serder.ListSerDer(serder.STRING).encode(conversationUids)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailConversationActions_VERSION}, data=__encoded__)
        from netbluemind.core.container.model.ItemIdentifier import ItemIdentifier
        from netbluemind.core.container.model.ItemIdentifier import __ItemIdentifierSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemIdentifierSerDer__()), response)

    def multipleDeleteById(self, conversationUids):
        postUri = "/_multipleDelete"
        __data__ = None
        __encoded__ = None
        __data__ = serder.ListSerDer(serder.STRING).encode(conversationUids)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailConversationActions_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)
