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


class MailFilterRuleCondition:
    def __init__(self):
        self.operator = None
        self.filter = None
        self.conditions = None
        self.clientProperties = None
        self.negate = None
        pass


class __MailFilterRuleConditionSerDer__:
    def __init__(self):
        pass

    def parse(self, value):
        if (value == None):
            return None
        instance = MailFilterRuleCondition()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.mailbox.api.rules.conditions.MailFilterRuleConditionOperator import MailFilterRuleConditionOperator
        from netbluemind.mailbox.api.rules.conditions.MailFilterRuleConditionOperator import __MailFilterRuleConditionOperatorSerDer__
        operatorValue = value['operator']
        instance.operator = __MailFilterRuleConditionOperatorSerDer__().parse(operatorValue)
        from netbluemind.mailbox.api.rules.conditions.MailFilterRuleFilter import MailFilterRuleFilter
        from netbluemind.mailbox.api.rules.conditions.MailFilterRuleFilter import __MailFilterRuleFilterSerDer__
        filterValue = value['filter']
        instance.filter = __MailFilterRuleFilterSerDer__().parse(filterValue)
        from netbluemind.mailbox.api.rules.conditions.MailFilterRuleCondition import MailFilterRuleCondition
        from netbluemind.mailbox.api.rules.conditions.MailFilterRuleCondition import __MailFilterRuleConditionSerDer__
        conditionsValue = value['conditions']
        instance.conditions = serder.ListSerDer(
            __MailFilterRuleConditionSerDer__()).parse(conditionsValue)
        clientPropertiesValue = value['clientProperties']
        instance.clientProperties = serder.MapSerDer(
            serder.STRING).parse(clientPropertiesValue)
        negateValue = value['negate']
        instance.negate = serder.BOOLEAN.parse(negateValue)
        return instance

    def encode(self, value):
        if (value == None):
            return None
        instance = dict()
        self.encodeInternal(value, instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.mailbox.api.rules.conditions.MailFilterRuleConditionOperator import MailFilterRuleConditionOperator
        from netbluemind.mailbox.api.rules.conditions.MailFilterRuleConditionOperator import __MailFilterRuleConditionOperatorSerDer__
        operatorValue = value.operator
        instance["operator"] = __MailFilterRuleConditionOperatorSerDer__().encode(
            operatorValue)
        from netbluemind.mailbox.api.rules.conditions.MailFilterRuleFilter import MailFilterRuleFilter
        from netbluemind.mailbox.api.rules.conditions.MailFilterRuleFilter import __MailFilterRuleFilterSerDer__
        filterValue = value.filter
        instance["filter"] = __MailFilterRuleFilterSerDer__().encode(filterValue)
        from netbluemind.mailbox.api.rules.conditions.MailFilterRuleCondition import MailFilterRuleCondition
        from netbluemind.mailbox.api.rules.conditions.MailFilterRuleCondition import __MailFilterRuleConditionSerDer__
        conditionsValue = value.conditions
        instance["conditions"] = serder.ListSerDer(
            __MailFilterRuleConditionSerDer__()).encode(conditionsValue)
        clientPropertiesValue = value.clientProperties
        instance["clientProperties"] = serder.MapSerDer(
            serder.STRING).encode(clientPropertiesValue)
        negateValue = value.negate
        instance["negate"] = serder.BOOLEAN.encode(negateValue)
        return instance
