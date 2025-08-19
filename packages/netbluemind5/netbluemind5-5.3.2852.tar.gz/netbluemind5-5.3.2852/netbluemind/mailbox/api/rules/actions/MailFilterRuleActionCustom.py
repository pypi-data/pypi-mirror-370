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

from netbluemind.mailbox.api.rules.actions.MailFilterRuleAction import MailFilterRuleAction
from netbluemind.mailbox.api.rules.actions.MailFilterRuleAction import __MailFilterRuleActionSerDer__


class MailFilterRuleActionCustom (MailFilterRuleAction):
    def __init__(self):
        MailFilterRuleAction.__init__(self)
        self.kind = None
        self.parameters = None
        pass


class __MailFilterRuleActionCustomSerDer__:
    def __init__(self):
        pass

    def parse(self, value):
        if (value == None):
            return None
        instance = MailFilterRuleActionCustom()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        __MailFilterRuleActionSerDer__().parseInternal(value, instance)
        kindValue = value['kind']
        instance.kind = serder.STRING.parse(kindValue)
        parametersValue = value['parameters']
        instance.parameters = serder.MapSerDer(
            serder.STRING).parse(parametersValue)
        return instance

    def encode(self, value):
        if (value == None):
            return None
        instance = dict()
        self.encodeInternal(value, instance)
        return instance

    def encodeInternal(self, value, instance):
        __MailFilterRuleActionSerDer__().encodeInternal(value, instance)

        kindValue = value.kind
        instance["kind"] = serder.STRING.encode(kindValue)
        parametersValue = value.parameters
        instance["parameters"] = serder.MapSerDer(
            serder.STRING).encode(parametersValue)
        return instance
