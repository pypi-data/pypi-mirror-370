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


class MailFilterRuleFilterContains (MailFilterRuleFilter):
    def __init__(self):
        MailFilterRuleFilter.__init__(self)
        self.comparator = None
        self.modifier = None
        self.values = None
        pass


class __MailFilterRuleFilterContainsSerDer__:
    def __init__(self):
        pass

    def parse(self, value):
        if (value == None):
            return None
        instance = MailFilterRuleFilterContains()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        __MailFilterRuleFilterSerDer__().parseInternal(value, instance)
        from netbluemind.mailbox.api.rules.conditions.MailFilterRuleFilterContainsComparator import MailFilterRuleFilterContainsComparator
        from netbluemind.mailbox.api.rules.conditions.MailFilterRuleFilterContainsComparator import __MailFilterRuleFilterContainsComparatorSerDer__
        comparatorValue = value['comparator']
        instance.comparator = __MailFilterRuleFilterContainsComparatorSerDer__().parse(
            comparatorValue)
        from netbluemind.mailbox.api.rules.conditions.MailFilterRuleFilterContainsModifier import MailFilterRuleFilterContainsModifier
        from netbluemind.mailbox.api.rules.conditions.MailFilterRuleFilterContainsModifier import __MailFilterRuleFilterContainsModifierSerDer__
        modifierValue = value['modifier']
        instance.modifier = __MailFilterRuleFilterContainsModifierSerDer__().parse(modifierValue)
        valuesValue = value['values']
        instance.values = serder.ListSerDer(serder.STRING).parse(valuesValue)
        return instance

    def encode(self, value):
        if (value == None):
            return None
        instance = dict()
        self.encodeInternal(value, instance)
        return instance

    def encodeInternal(self, value, instance):
        __MailFilterRuleFilterSerDer__().encodeInternal(value, instance)

        from netbluemind.mailbox.api.rules.conditions.MailFilterRuleFilterContainsComparator import MailFilterRuleFilterContainsComparator
        from netbluemind.mailbox.api.rules.conditions.MailFilterRuleFilterContainsComparator import __MailFilterRuleFilterContainsComparatorSerDer__
        comparatorValue = value.comparator
        instance["comparator"] = __MailFilterRuleFilterContainsComparatorSerDer__(
        ).encode(comparatorValue)
        from netbluemind.mailbox.api.rules.conditions.MailFilterRuleFilterContainsModifier import MailFilterRuleFilterContainsModifier
        from netbluemind.mailbox.api.rules.conditions.MailFilterRuleFilterContainsModifier import __MailFilterRuleFilterContainsModifierSerDer__
        modifierValue = value.modifier
        instance["modifier"] = __MailFilterRuleFilterContainsModifierSerDer__().encode(
            modifierValue)
        valuesValue = value.values
        instance["values"] = serder.ListSerDer(
            serder.STRING).encode(valuesValue)
        return instance
