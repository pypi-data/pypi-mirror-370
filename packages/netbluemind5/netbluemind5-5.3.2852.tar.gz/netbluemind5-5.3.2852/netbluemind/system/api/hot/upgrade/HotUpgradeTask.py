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


class HotUpgradeTask:
    def __init__(self):
        self.id = None
        self.operation = None
        self.parameters = None
        self.status = None
        self.failure = None
        self.upgraderId = None
        self.createdAt = None
        self.updatedAt = None
        self.executionMode = None
        self.retryCount = None
        self.retryDelaySeconds = None
        self.reportFailure = None
        self.mandatory = None
        self.events = None
        pass


class __HotUpgradeTaskSerDer__:
    def __init__(self):
        pass

    def parse(self, value):
        if (value == None):
            return None
        instance = HotUpgradeTask()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        idValue = value['id']
        instance.id = serder.INT.parse(idValue)
        operationValue = value['operation']
        instance.operation = serder.STRING.parse(operationValue)
        parametersValue = value['parameters']
        instance.parameters = serder.STRING.parse(parametersValue)
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskStatus import HotUpgradeTaskStatus
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskStatus import __HotUpgradeTaskStatusSerDer__
        statusValue = value['status']
        instance.status = __HotUpgradeTaskStatusSerDer__().parse(statusValue)
        failureValue = value['failure']
        instance.failure = serder.INT.parse(failureValue)
        upgraderIdValue = value['upgraderId']
        instance.upgraderId = serder.STRING.parse(upgraderIdValue)
        createdAtValue = value['createdAt']
        instance.createdAt = serder.DATE.parse(createdAtValue)
        updatedAtValue = value['updatedAt']
        instance.updatedAt = serder.DATE.parse(updatedAtValue)
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskExecutionMode import HotUpgradeTaskExecutionMode
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskExecutionMode import __HotUpgradeTaskExecutionModeSerDer__
        executionModeValue = value['executionMode']
        instance.executionMode = __HotUpgradeTaskExecutionModeSerDer__().parse(executionModeValue)
        retryCountValue = value['retryCount']
        instance.retryCount = serder.INT.parse(retryCountValue)
        retryDelaySecondsValue = value['retryDelaySeconds']
        instance.retryDelaySeconds = serder.INT.parse(retryDelaySecondsValue)
        reportFailureValue = value['reportFailure']
        instance.reportFailure = serder.BOOLEAN.parse(reportFailureValue)
        mandatoryValue = value['mandatory']
        instance.mandatory = serder.BOOLEAN.parse(mandatoryValue)
        from netbluemind.system.api.hot.upgrade.HotUpgradeStepEvent import HotUpgradeStepEvent
        from netbluemind.system.api.hot.upgrade.HotUpgradeStepEvent import __HotUpgradeStepEventSerDer__
        eventsValue = value['events']
        instance.events = serder.ListSerDer(
            __HotUpgradeStepEventSerDer__()).parse(eventsValue)
        return instance

    def encode(self, value):
        if (value == None):
            return None
        instance = dict()
        self.encodeInternal(value, instance)
        return instance

    def encodeInternal(self, value, instance):

        idValue = value.id
        instance["id"] = serder.INT.encode(idValue)
        operationValue = value.operation
        instance["operation"] = serder.STRING.encode(operationValue)
        parametersValue = value.parameters
        instance["parameters"] = serder.STRING.encode(parametersValue)
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskStatus import HotUpgradeTaskStatus
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskStatus import __HotUpgradeTaskStatusSerDer__
        statusValue = value.status
        instance["status"] = __HotUpgradeTaskStatusSerDer__().encode(statusValue)
        failureValue = value.failure
        instance["failure"] = serder.INT.encode(failureValue)
        upgraderIdValue = value.upgraderId
        instance["upgraderId"] = serder.STRING.encode(upgraderIdValue)
        createdAtValue = value.createdAt
        instance["createdAt"] = serder.DATE.encode(createdAtValue)
        updatedAtValue = value.updatedAt
        instance["updatedAt"] = serder.DATE.encode(updatedAtValue)
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskExecutionMode import HotUpgradeTaskExecutionMode
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskExecutionMode import __HotUpgradeTaskExecutionModeSerDer__
        executionModeValue = value.executionMode
        instance["executionMode"] = __HotUpgradeTaskExecutionModeSerDer__().encode(
            executionModeValue)
        retryCountValue = value.retryCount
        instance["retryCount"] = serder.INT.encode(retryCountValue)
        retryDelaySecondsValue = value.retryDelaySeconds
        instance["retryDelaySeconds"] = serder.INT.encode(
            retryDelaySecondsValue)
        reportFailureValue = value.reportFailure
        instance["reportFailure"] = serder.BOOLEAN.encode(reportFailureValue)
        mandatoryValue = value.mandatory
        instance["mandatory"] = serder.BOOLEAN.encode(mandatoryValue)
        from netbluemind.system.api.hot.upgrade.HotUpgradeStepEvent import HotUpgradeStepEvent
        from netbluemind.system.api.hot.upgrade.HotUpgradeStepEvent import __HotUpgradeStepEventSerDer__
        eventsValue = value.events
        instance["events"] = serder.ListSerDer(
            __HotUpgradeStepEventSerDer__()).encode(eventsValue)
        return instance
