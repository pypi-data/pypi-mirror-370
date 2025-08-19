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


class HotUpgradeStepEvent:
    def __init__(self):
        self.step = None
        self.status = None
        self.message = None
        self.date = None
        pass


class __HotUpgradeStepEventSerDer__:
    def __init__(self):
        pass

    def parse(self, value):
        if (value == None):
            return None
        instance = HotUpgradeStepEvent()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        stepValue = value['step']
        instance.step = serder.STRING.parse(stepValue)
        from netbluemind.system.api.hot.upgrade.HotUpgradeStepEventStatus import HotUpgradeStepEventStatus
        from netbluemind.system.api.hot.upgrade.HotUpgradeStepEventStatus import __HotUpgradeStepEventStatusSerDer__
        statusValue = value['status']
        instance.status = __HotUpgradeStepEventStatusSerDer__().parse(statusValue)
        messageValue = value['message']
        instance.message = serder.STRING.parse(messageValue)
        dateValue = value['date']
        instance.date = serder.LONG.parse(dateValue)
        return instance

    def encode(self, value):
        if (value == None):
            return None
        instance = dict()
        self.encodeInternal(value, instance)
        return instance

    def encodeInternal(self, value, instance):

        stepValue = value.step
        instance["step"] = serder.STRING.encode(stepValue)
        from netbluemind.system.api.hot.upgrade.HotUpgradeStepEventStatus import HotUpgradeStepEventStatus
        from netbluemind.system.api.hot.upgrade.HotUpgradeStepEventStatus import __HotUpgradeStepEventStatusSerDer__
        statusValue = value.status
        instance["status"] = __HotUpgradeStepEventStatusSerDer__().encode(
            statusValue)
        messageValue = value.message
        instance["message"] = serder.STRING.encode(messageValue)
        dateValue = value.date
        instance["date"] = serder.LONG.encode(dateValue)
        return instance
