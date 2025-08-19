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


class RepairConfig:
    def __init__(self):
        self.opIdentifiers = None
        self.dry = None
        self.logToCoreLog = None
        self.verbose = None
        pass


class __RepairConfigSerDer__:
    def __init__(self):
        pass

    def parse(self, value):
        if (value == None):
            return None
        instance = RepairConfig()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        opIdentifiersValue = value['opIdentifiers']
        instance.opIdentifiers = serder.SetSerDer(
            serder.STRING).parse(opIdentifiersValue)
        dryValue = value['dry']
        instance.dry = serder.BOOLEAN.parse(dryValue)
        logToCoreLogValue = value['logToCoreLog']
        instance.logToCoreLog = serder.BOOLEAN.parse(logToCoreLogValue)
        verboseValue = value['verbose']
        instance.verbose = serder.BOOLEAN.parse(verboseValue)
        return instance

    def encode(self, value):
        if (value == None):
            return None
        instance = dict()
        self.encodeInternal(value, instance)
        return instance

    def encodeInternal(self, value, instance):

        opIdentifiersValue = value.opIdentifiers
        instance["opIdentifiers"] = serder.SetSerDer(
            serder.STRING).encode(opIdentifiersValue)
        dryValue = value.dry
        instance["dry"] = serder.BOOLEAN.encode(dryValue)
        logToCoreLogValue = value.logToCoreLog
        instance["logToCoreLog"] = serder.BOOLEAN.encode(logToCoreLogValue)
        verboseValue = value.verbose
        instance["verbose"] = serder.BOOLEAN.encode(verboseValue)
        return instance
