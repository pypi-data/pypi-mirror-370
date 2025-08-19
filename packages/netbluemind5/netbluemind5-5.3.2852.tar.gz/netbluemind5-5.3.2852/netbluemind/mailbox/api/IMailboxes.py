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

IMailboxes_VERSION = "5.3.2852"


class IMailboxes(BaseEndpoint):
    def __init__(self, apiKey, url, domainUid):
        self.url = url
        self.apiKey = apiKey
        self.base = url + '/mailboxes/{domainUid}'
        self.domainUid_ = domainUid
        self.base = self.base.replace('{domainUid}', domainUid)

    def addDomainRule(self, rule):
        postUri = "/_rules"
        __data__ = None
        __encoded__ = None
        from netbluemind.mailbox.api.rules.MailFilterRule import MailFilterRule
        from netbluemind.mailbox.api.rules.MailFilterRule import __MailFilterRuleSerDer__
        __data__ = __MailFilterRuleSerDer__().encode(rule)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.put(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        return self.handleResult__(serder.LONG, response)

    def addMailboxRule(self, mailboxUid, rule):
        postUri = "/{mailboxUid}/_rules"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{mailboxUid}", mailboxUid)
        from netbluemind.mailbox.api.rules.MailFilterRule import MailFilterRule
        from netbluemind.mailbox.api.rules.MailFilterRule import __MailFilterRuleSerDer__
        __data__ = __MailFilterRuleSerDer__().encode(rule)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.put(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        return self.handleResult__(serder.LONG, response)

    def addMailboxRuleRelative(self, mailboxUid, position, anchorId, rule):
        postUri = "/{mailboxUid}/_rules/{position}/{anchorId}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{mailboxUid}", mailboxUid)
        postUri = postUri.replace("{position}", position)
        postUri = postUri.replace("{anchorId}", anchorId)
        from netbluemind.mailbox.api.rules.MailFilterRule import MailFilterRule
        from netbluemind.mailbox.api.rules.MailFilterRule import __MailFilterRuleSerDer__
        __data__ = __MailFilterRuleSerDer__().encode(rule)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.put(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        return self.handleResult__(serder.LONG, response)

    def byEmail(self, email):
        postUri = "/_byemail"
        __data__ = None
        __encoded__ = None
        queryParams = {'email': email}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        from netbluemind.mailbox.api.Mailbox import Mailbox
        from netbluemind.mailbox.api.Mailbox import __MailboxSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__MailboxSerDer__()), response)

    def byName(self, name):
        postUri = "/_byname"
        __data__ = None
        __encoded__ = None
        queryParams = {'name': name}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        from netbluemind.mailbox.api.Mailbox import Mailbox
        from netbluemind.mailbox.api.Mailbox import __MailboxSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__MailboxSerDer__()), response)

    def byRouting(self, email):
        postUri = "/_byRouting"
        __data__ = None
        __encoded__ = None
        queryParams = {'email': email}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        return self.handleResult__(serder.ListSerDer(serder.STRING), response)

    def byType(self, email):
        postUri = "/_byType"
        __data__ = None
        __encoded__ = None
        queryParams = {'email': email}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        return self.handleResult__(serder.ListSerDer(serder.STRING), response)

    def create(self, uid, mailbox):
        postUri = "/{uid}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        from netbluemind.mailbox.api.Mailbox import Mailbox
        from netbluemind.mailbox.api.Mailbox import __MailboxSerDer__
        __data__ = __MailboxSerDer__().encode(mailbox)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.put(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def delete(self, uid):
        postUri = "/{uid}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {}

        response = requests.delete(self.base + postUri, params=queryParams, verify=False, headers={
                                   'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def deleteDomainRule(self, id):
        postUri = "/_rules/{id}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{id}", id)
        queryParams = {}

        response = requests.delete(self.base + postUri, params=queryParams, verify=False, headers={
                                   'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def deleteMailboxRule(self, mailboxUid, id):
        postUri = "/{mailboxUid}/_rules/{id}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{mailboxUid}", mailboxUid)
        postUri = postUri.replace("{id}", id)
        queryParams = {}

        response = requests.delete(self.base + postUri, params=queryParams, verify=False, headers={
                                   'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def getComplete(self, uid):
        postUri = "/{uid}/complete"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        from netbluemind.mailbox.api.Mailbox import Mailbox
        from netbluemind.mailbox.api.Mailbox import __MailboxSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__MailboxSerDer__()), response)

    def getDomainFilter(self):
        postUri = "/_filter"
        __data__ = None
        __encoded__ = None
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        from netbluemind.mailbox.api.MailFilter import MailFilter
        from netbluemind.mailbox.api.MailFilter import __MailFilterSerDer__
        return self.handleResult__(__MailFilterSerDer__(), response)

    def getDomainRule(self, id):
        postUri = "/_rules/{id}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{id}", id)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        from netbluemind.mailbox.api.rules.MailFilterRule import MailFilterRule
        from netbluemind.mailbox.api.rules.MailFilterRule import __MailFilterRuleSerDer__
        return self.handleResult__(__MailFilterRuleSerDer__(), response)

    def getDomainRules(self):
        postUri = "/_rules"
        __data__ = None
        __encoded__ = None
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        from netbluemind.mailbox.api.rules.MailFilterRule import MailFilterRule
        from netbluemind.mailbox.api.rules.MailFilterRule import __MailFilterRuleSerDer__
        return self.handleResult__(serder.ListSerDer(__MailFilterRuleSerDer__()), response)

    def getMailboxAccessControlList(self, mailboxUid):
        postUri = "/{mailboxUid}/_acls"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{mailboxUid}", mailboxUid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        from netbluemind.core.container.model.acl.AccessControlEntry import AccessControlEntry
        from netbluemind.core.container.model.acl.AccessControlEntry import __AccessControlEntrySerDer__
        return self.handleResult__(serder.ListSerDer(__AccessControlEntrySerDer__()), response)

    def getMailboxConfig(self, uid):
        postUri = "/{uid}/_config"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        from netbluemind.mailbox.api.MailboxConfig import MailboxConfig
        from netbluemind.mailbox.api.MailboxConfig import __MailboxConfigSerDer__
        return self.handleResult__(__MailboxConfigSerDer__(), response)

    def getMailboxDelegationRule(self, mailboxUid):
        postUri = "/{mailboxUid}/_delegationRule"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{mailboxUid}", mailboxUid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        from netbluemind.mailbox.api.rules.DelegationRule import DelegationRule
        from netbluemind.mailbox.api.rules.DelegationRule import __DelegationRuleSerDer__
        return self.handleResult__(__DelegationRuleSerDer__(), response)

    def getMailboxFilter(self, mailboxUid):
        postUri = "/{mailboxUid}/_filter"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{mailboxUid}", mailboxUid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        from netbluemind.mailbox.api.MailFilter import MailFilter
        from netbluemind.mailbox.api.MailFilter import __MailFilterSerDer__
        return self.handleResult__(__MailFilterSerDer__(), response)

    def getMailboxForwarding(self, mailboxUid):
        postUri = "/{mailboxUid}/_forwarding"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{mailboxUid}", mailboxUid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        from netbluemind.mailbox.api.MailFilterForwarding import MailFilterForwarding
        from netbluemind.mailbox.api.MailFilterForwarding import __MailFilterForwardingSerDer__
        return self.handleResult__(__MailFilterForwardingSerDer__(), response)

    def getMailboxQuota(self, uid):
        postUri = "/{uid}/_quota"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        from netbluemind.mailbox.api.MailboxQuota import MailboxQuota
        from netbluemind.mailbox.api.MailboxQuota import __MailboxQuotaSerDer__
        return self.handleResult__(__MailboxQuotaSerDer__(), response)

    def getMailboxRule(self, mailboxUid, id):
        postUri = "/{mailboxUid}/_rules/{id}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{mailboxUid}", mailboxUid)
        postUri = postUri.replace("{id}", id)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        from netbluemind.mailbox.api.rules.MailFilterRule import MailFilterRule
        from netbluemind.mailbox.api.rules.MailFilterRule import __MailFilterRuleSerDer__
        return self.handleResult__(__MailFilterRuleSerDer__(), response)

    def getMailboxRules(self, mailboxUid):
        postUri = "/{mailboxUid}/_rules"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{mailboxUid}", mailboxUid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        from netbluemind.mailbox.api.rules.MailFilterRule import MailFilterRule
        from netbluemind.mailbox.api.rules.MailFilterRule import __MailFilterRuleSerDer__
        return self.handleResult__(serder.ListSerDer(__MailFilterRuleSerDer__()), response)

    def getMailboxRulesByClient(self, mailboxUid, client):
        postUri = "/{mailboxUid}/_rulesByClient"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{mailboxUid}", mailboxUid)
        queryParams = {'client': client}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        from netbluemind.mailbox.api.rules.MailFilterRule import MailFilterRule
        from netbluemind.mailbox.api.rules.MailFilterRule import __MailFilterRuleSerDer__
        return self.handleResult__(serder.ListSerDer(__MailFilterRuleSerDer__()), response)

    def getMailboxVacation(self, mailboxUid):
        postUri = "/{mailboxUid}/_vacation"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{mailboxUid}", mailboxUid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        from netbluemind.mailbox.api.MailFilterVacation import MailFilterVacation
        from netbluemind.mailbox.api.MailFilterVacation import __MailFilterVacationSerDer__
        return self.handleResult__(__MailFilterVacationSerDer__(), response)

    def getUnreadMessagesCount(self):
        postUri = "/_unread"
        __data__ = None
        __encoded__ = None
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        return self.handleResult__(serder.INT, response)

    def list(self):
        postUri = "/_list"
        __data__ = None
        __encoded__ = None
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        from netbluemind.mailbox.api.Mailbox import Mailbox
        from netbluemind.mailbox.api.Mailbox import __MailboxSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__MailboxSerDer__())), response)

    def listUids(self):
        postUri = "/_listUids"
        __data__ = None
        __encoded__ = None
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        return self.handleResult__(serder.ListSerDer(serder.STRING), response)

    def moveMailboxRule(self, mailboxUid, id, direction):
        postUri = "/{mailboxUid}/_rules/{id}/{direction}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{mailboxUid}", mailboxUid)
        postUri = postUri.replace("{id}", id)
        postUri = postUri.replace("{direction}", direction)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def moveMailboxRuleRelative(self, mailboxUid, id, position, anchorId):
        postUri = "/{mailboxUid}/_rules/{id}/{position}/{anchorId}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{mailboxUid}", mailboxUid)
        postUri = postUri.replace("{id}", id)
        postUri = postUri.replace("{position}", position)
        postUri = postUri.replace("{anchorId}", anchorId)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def multipleGet(self, uids):
        postUri = "/_mget"
        __data__ = None
        __encoded__ = None
        __data__ = serder.ListSerDer(serder.STRING).encode(uids)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        from netbluemind.mailbox.api.Mailbox import Mailbox
        from netbluemind.mailbox.api.Mailbox import __MailboxSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__MailboxSerDer__())), response)

    def setDomainFilter(self, filter):
        postUri = "/_filter"
        __data__ = None
        __encoded__ = None
        from netbluemind.mailbox.api.MailFilter import MailFilter
        from netbluemind.mailbox.api.MailFilter import __MailFilterSerDer__
        __data__ = __MailFilterSerDer__().encode(filter)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def setMailboxAccessControlList(self, mailboxUid, accessControlEntries):
        postUri = "/{mailboxUid}/_acls"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{mailboxUid}", mailboxUid)
        from netbluemind.core.container.model.acl.AccessControlEntry import AccessControlEntry
        from netbluemind.core.container.model.acl.AccessControlEntry import __AccessControlEntrySerDer__
        __data__ = serder.ListSerDer(
            __AccessControlEntrySerDer__()).encode(accessControlEntries)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def setMailboxDelegationRule(self, mailboxUid, delegationRule):
        postUri = "/{mailboxUid}/_delegationRule"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{mailboxUid}", mailboxUid)
        from netbluemind.mailbox.api.rules.DelegationRule import DelegationRule
        from netbluemind.mailbox.api.rules.DelegationRule import __DelegationRuleSerDer__
        __data__ = __DelegationRuleSerDer__().encode(delegationRule)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def setMailboxFilter(self, mailboxUid, filter):
        postUri = "/{mailboxUid}/_filter"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{mailboxUid}", mailboxUid)
        from netbluemind.mailbox.api.MailFilter import MailFilter
        from netbluemind.mailbox.api.MailFilter import __MailFilterSerDer__
        __data__ = __MailFilterSerDer__().encode(filter)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def setMailboxForwarding(self, mailboxUid, forwarding):
        postUri = "/{mailboxUid}/_forwarding"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{mailboxUid}", mailboxUid)
        from netbluemind.mailbox.api.MailFilterForwarding import MailFilterForwarding
        from netbluemind.mailbox.api.MailFilterForwarding import __MailFilterForwardingSerDer__
        __data__ = __MailFilterForwardingSerDer__().encode(forwarding)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def setMailboxVacation(self, mailboxUid, vacation):
        postUri = "/{mailboxUid}/_vacation"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{mailboxUid}", mailboxUid)
        from netbluemind.mailbox.api.MailFilterVacation import MailFilterVacation
        from netbluemind.mailbox.api.MailFilterVacation import __MailFilterVacationSerDer__
        __data__ = __MailFilterVacationSerDer__().encode(vacation)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def update(self, uid, mailbox):
        postUri = "/{uid}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        from netbluemind.mailbox.api.Mailbox import Mailbox
        from netbluemind.mailbox.api.Mailbox import __MailboxSerDer__
        __data__ = __MailboxSerDer__().encode(mailbox)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def updateDomainRule(self, id, rule):
        postUri = "/_rules/{id}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{id}", id)
        from netbluemind.mailbox.api.rules.MailFilterRule import MailFilterRule
        from netbluemind.mailbox.api.rules.MailFilterRule import __MailFilterRuleSerDer__
        __data__ = __MailFilterRuleSerDer__().encode(rule)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)

    def updateMailboxRule(self, mailboxUid, id, rule):
        postUri = "/{mailboxUid}/_rules/{id}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{mailboxUid}", mailboxUid)
        postUri = postUri.replace("{id}", id)
        from netbluemind.mailbox.api.rules.MailFilterRule import MailFilterRule
        from netbluemind.mailbox.api.rules.MailFilterRule import __MailFilterRuleSerDer__
        __data__ = __MailFilterRuleSerDer__().encode(rule)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailboxes_VERSION}, data=__encoded__)
        return self.handleResult__(None, response)
