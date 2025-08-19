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
from netbluemind.python import serder


class DelegationRule:
    def __init__(self):
        self.delegatorCalendarUid = None
        self.delegateUids = None
        self.delegatorUid = None
        self.keepCopy = None
        self.readOnly = None
        pass


class __DelegationRuleSerDer__:
    def __init__(self):
        pass

    def parse(self, value):
        if (value == None):
            return None
        instance = DelegationRule()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        delegatorCalendarUidValue = value['delegatorCalendarUid']
        instance.delegatorCalendarUid = serder.STRING.parse(
            delegatorCalendarUidValue)
        delegateUidsValue = value['delegateUids']
        instance.delegateUids = serder.ListSerDer(
            serder.STRING).parse(delegateUidsValue)
        delegatorUidValue = value['delegatorUid']
        instance.delegatorUid = serder.STRING.parse(delegatorUidValue)
        keepCopyValue = value['keepCopy']
        instance.keepCopy = serder.BOOLEAN.parse(keepCopyValue)
        readOnlyValue = value['readOnly']
        instance.readOnly = serder.BOOLEAN.parse(readOnlyValue)
        return instance

    def encode(self, value):
        if (value == None):
            return None
        instance = dict()
        self.encodeInternal(value, instance)
        return instance

    def encodeInternal(self, value, instance):

        delegatorCalendarUidValue = value.delegatorCalendarUid
        instance["delegatorCalendarUid"] = serder.STRING.encode(
            delegatorCalendarUidValue)
        delegateUidsValue = value.delegateUids
        instance["delegateUids"] = serder.ListSerDer(
            serder.STRING).encode(delegateUidsValue)
        delegatorUidValue = value.delegatorUid
        instance["delegatorUid"] = serder.STRING.encode(delegatorUidValue)
        keepCopyValue = value.keepCopy
        instance["keepCopy"] = serder.BOOLEAN.encode(keepCopyValue)
        readOnlyValue = value.readOnly
        instance["readOnly"] = serder.BOOLEAN.encode(readOnlyValue)
        return instance
