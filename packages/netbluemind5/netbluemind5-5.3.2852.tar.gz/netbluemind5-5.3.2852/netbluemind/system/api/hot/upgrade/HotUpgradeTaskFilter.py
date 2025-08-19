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


class HotUpgradeTaskFilter:
    def __init__(self):
        self.operation = None
        self.statuses = None
        self.onlyRetryable = None
        self.onlyReady = None
        self.onlyMandatory = None
        self.mode = None
        pass


class __HotUpgradeTaskFilterSerDer__:
    def __init__(self):
        pass

    def parse(self, value):
        if (value == None):
            return None
        instance = HotUpgradeTaskFilter()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        operationValue = value['operation']
        instance.operation = serder.STRING.parse(operationValue)
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskStatus import HotUpgradeTaskStatus
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskStatus import __HotUpgradeTaskStatusSerDer__
        statusesValue = value['statuses']
        instance.statuses = serder.ListSerDer(
            __HotUpgradeTaskStatusSerDer__()).parse(statusesValue)
        onlyRetryableValue = value['onlyRetryable']
        instance.onlyRetryable = serder.BOOLEAN.parse(onlyRetryableValue)
        onlyReadyValue = value['onlyReady']
        instance.onlyReady = serder.BOOLEAN.parse(onlyReadyValue)
        onlyMandatoryValue = value['onlyMandatory']
        instance.onlyMandatory = serder.BOOLEAN.parse(onlyMandatoryValue)
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskExecutionMode import HotUpgradeTaskExecutionMode
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskExecutionMode import __HotUpgradeTaskExecutionModeSerDer__
        modeValue = value['mode']
        instance.mode = serder.ListSerDer(
            __HotUpgradeTaskExecutionModeSerDer__()).parse(modeValue)
        return instance

    def encode(self, value):
        if (value == None):
            return None
        instance = dict()
        self.encodeInternal(value, instance)
        return instance

    def encodeInternal(self, value, instance):

        operationValue = value.operation
        instance["operation"] = serder.STRING.encode(operationValue)
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskStatus import HotUpgradeTaskStatus
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskStatus import __HotUpgradeTaskStatusSerDer__
        statusesValue = value.statuses
        instance["statuses"] = serder.ListSerDer(
            __HotUpgradeTaskStatusSerDer__()).encode(statusesValue)
        onlyRetryableValue = value.onlyRetryable
        instance["onlyRetryable"] = serder.BOOLEAN.encode(onlyRetryableValue)
        onlyReadyValue = value.onlyReady
        instance["onlyReady"] = serder.BOOLEAN.encode(onlyReadyValue)
        onlyMandatoryValue = value.onlyMandatory
        instance["onlyMandatory"] = serder.BOOLEAN.encode(onlyMandatoryValue)
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskExecutionMode import HotUpgradeTaskExecutionMode
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskExecutionMode import __HotUpgradeTaskExecutionModeSerDer__
        modeValue = value.mode
        instance["mode"] = serder.ListSerDer(
            __HotUpgradeTaskExecutionModeSerDer__()).encode(modeValue)
        return instance
