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


class MailFilterRule:
    def __init__(self):
        self.id = None
        self.client = None
        self.type = None
        self.trigger = None
        self.deferred = None
        self.active = None
        self.name = None
        self.clientProperties = None
        self.conditions = None
        self.actions = None
        self.stop = None
        pass


class __MailFilterRuleSerDer__:
    def __init__(self):
        pass

    def parse(self, value):
        if (value == None):
            return None
        instance = MailFilterRule()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        idValue = value['id']
        instance.id = serder.LONG.parse(idValue)
        clientValue = value['client']
        instance.client = serder.STRING.parse(clientValue)
        from netbluemind.mailbox.api.rules.MailFilterRuleType import MailFilterRuleType
        from netbluemind.mailbox.api.rules.MailFilterRuleType import __MailFilterRuleTypeSerDer__
        typeValue = value['type']
        instance.type = __MailFilterRuleTypeSerDer__().parse(typeValue)
        from netbluemind.mailbox.api.rules.MailFilterRuleTrigger import MailFilterRuleTrigger
        from netbluemind.mailbox.api.rules.MailFilterRuleTrigger import __MailFilterRuleTriggerSerDer__
        triggerValue = value['trigger']
        instance.trigger = __MailFilterRuleTriggerSerDer__().parse(triggerValue)
        deferredValue = value['deferred']
        instance.deferred = serder.BOOLEAN.parse(deferredValue)
        activeValue = value['active']
        instance.active = serder.BOOLEAN.parse(activeValue)
        nameValue = value['name']
        instance.name = serder.STRING.parse(nameValue)
        clientPropertiesValue = value['clientProperties']
        instance.clientProperties = serder.MapSerDer(
            serder.STRING).parse(clientPropertiesValue)
        from netbluemind.mailbox.api.rules.conditions.MailFilterRuleCondition import MailFilterRuleCondition
        from netbluemind.mailbox.api.rules.conditions.MailFilterRuleCondition import __MailFilterRuleConditionSerDer__
        conditionsValue = value['conditions']
        instance.conditions = serder.ListSerDer(
            __MailFilterRuleConditionSerDer__()).parse(conditionsValue)
        from netbluemind.mailbox.api.rules.actions.MailFilterRuleAction import MailFilterRuleAction
        from netbluemind.mailbox.api.rules.actions.MailFilterRuleAction import __MailFilterRuleActionSerDer__
        actionsValue = value['actions']
        instance.actions = serder.ListSerDer(
            __MailFilterRuleActionSerDer__()).parse(actionsValue)
        stopValue = value['stop']
        instance.stop = serder.BOOLEAN.parse(stopValue)
        return instance

    def encode(self, value):
        if (value == None):
            return None
        instance = dict()
        self.encodeInternal(value, instance)
        return instance

    def encodeInternal(self, value, instance):

        idValue = value.id
        instance["id"] = serder.LONG.encode(idValue)
        clientValue = value.client
        instance["client"] = serder.STRING.encode(clientValue)
        from netbluemind.mailbox.api.rules.MailFilterRuleType import MailFilterRuleType
        from netbluemind.mailbox.api.rules.MailFilterRuleType import __MailFilterRuleTypeSerDer__
        typeValue = value.type
        instance["type"] = __MailFilterRuleTypeSerDer__().encode(typeValue)
        from netbluemind.mailbox.api.rules.MailFilterRuleTrigger import MailFilterRuleTrigger
        from netbluemind.mailbox.api.rules.MailFilterRuleTrigger import __MailFilterRuleTriggerSerDer__
        triggerValue = value.trigger
        instance["trigger"] = __MailFilterRuleTriggerSerDer__().encode(
            triggerValue)
        deferredValue = value.deferred
        instance["deferred"] = serder.BOOLEAN.encode(deferredValue)
        activeValue = value.active
        instance["active"] = serder.BOOLEAN.encode(activeValue)
        nameValue = value.name
        instance["name"] = serder.STRING.encode(nameValue)
        clientPropertiesValue = value.clientProperties
        instance["clientProperties"] = serder.MapSerDer(
            serder.STRING).encode(clientPropertiesValue)
        from netbluemind.mailbox.api.rules.conditions.MailFilterRuleCondition import MailFilterRuleCondition
        from netbluemind.mailbox.api.rules.conditions.MailFilterRuleCondition import __MailFilterRuleConditionSerDer__
        conditionsValue = value.conditions
        instance["conditions"] = serder.ListSerDer(
            __MailFilterRuleConditionSerDer__()).encode(conditionsValue)
        from netbluemind.mailbox.api.rules.actions.MailFilterRuleAction import MailFilterRuleAction
        from netbluemind.mailbox.api.rules.actions.MailFilterRuleAction import __MailFilterRuleActionSerDer__
        actionsValue = value.actions
        instance["actions"] = serder.ListSerDer(
            __MailFilterRuleActionSerDer__()).encode(actionsValue)
        stopValue = value.stop
        instance["stop"] = serder.BOOLEAN.encode(stopValue)
        return instance
