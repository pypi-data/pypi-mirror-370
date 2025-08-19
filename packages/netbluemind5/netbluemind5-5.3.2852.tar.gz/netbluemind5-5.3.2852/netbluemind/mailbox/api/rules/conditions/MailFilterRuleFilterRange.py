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

from netbluemind.mailbox.api.rules.conditions.MailFilterRuleFilter import MailFilterRuleFilter
from netbluemind.mailbox.api.rules.conditions.MailFilterRuleFilter import __MailFilterRuleFilterSerDer__


class MailFilterRuleFilterRange (MailFilterRuleFilter):
    def __init__(self):
        MailFilterRuleFilter.__init__(self)
        self.lowerBound = None
        self.upperBound = None
        self.inclusive = None
        pass


class __MailFilterRuleFilterRangeSerDer__:
    def __init__(self):
        pass

    def parse(self, value):
        if (value == None):
            return None
        instance = MailFilterRuleFilterRange()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        __MailFilterRuleFilterSerDer__().parseInternal(value, instance)
        lowerBoundValue = value['lowerBound']
        instance.lowerBound = serder.STRING.parse(lowerBoundValue)
        upperBoundValue = value['upperBound']
        instance.upperBound = serder.STRING.parse(upperBoundValue)
        inclusiveValue = value['inclusive']
        instance.inclusive = serder.BOOLEAN.parse(inclusiveValue)
        return instance

    def encode(self, value):
        if (value == None):
            return None
        instance = dict()
        self.encodeInternal(value, instance)
        return instance

    def encodeInternal(self, value, instance):
        __MailFilterRuleFilterSerDer__().encodeInternal(value, instance)

        lowerBoundValue = value.lowerBound
        instance["lowerBound"] = serder.STRING.encode(lowerBoundValue)
        upperBoundValue = value.upperBound
        instance["upperBound"] = serder.STRING.encode(upperBoundValue)
        inclusiveValue = value.inclusive
        instance["inclusive"] = serder.BOOLEAN.encode(inclusiveValue)
        return instance
