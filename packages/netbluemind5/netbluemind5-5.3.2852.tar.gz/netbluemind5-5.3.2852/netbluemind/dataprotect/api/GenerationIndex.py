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


class GenerationIndex:
    def __init__(self):
        self.entryUid = None
        self.displayName = None
        self.email = None
        self.path = None
        self.dataLocation = None
        self.kind = None
        pass


class __GenerationIndexSerDer__:
    def __init__(self):
        pass

    def parse(self, value):
        if (value == None):
            return None
        instance = GenerationIndex()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        entryUidValue = value['entryUid']
        instance.entryUid = serder.STRING.parse(entryUidValue)
        displayNameValue = value['displayName']
        instance.displayName = serder.STRING.parse(displayNameValue)
        emailValue = value['email']
        instance.email = serder.STRING.parse(emailValue)
        pathValue = value['path']
        instance.path = serder.STRING.parse(pathValue)
        dataLocationValue = value['dataLocation']
        instance.dataLocation = serder.STRING.parse(dataLocationValue)
        from netbluemind.directory.api.BaseDirEntryKind import BaseDirEntryKind
        from netbluemind.directory.api.BaseDirEntryKind import __BaseDirEntryKindSerDer__
        kindValue = value['kind']
        instance.kind = __BaseDirEntryKindSerDer__().parse(kindValue)
        return instance

    def encode(self, value):
        if (value == None):
            return None
        instance = dict()
        self.encodeInternal(value, instance)
        return instance

    def encodeInternal(self, value, instance):

        entryUidValue = value.entryUid
        instance["entryUid"] = serder.STRING.encode(entryUidValue)
        displayNameValue = value.displayName
        instance["displayName"] = serder.STRING.encode(displayNameValue)
        emailValue = value.email
        instance["email"] = serder.STRING.encode(emailValue)
        pathValue = value.path
        instance["path"] = serder.STRING.encode(pathValue)
        dataLocationValue = value.dataLocation
        instance["dataLocation"] = serder.STRING.encode(dataLocationValue)
        from netbluemind.directory.api.BaseDirEntryKind import BaseDirEntryKind
        from netbluemind.directory.api.BaseDirEntryKind import __BaseDirEntryKindSerDer__
        kindValue = value.kind
        instance["kind"] = __BaseDirEntryKindSerDer__().encode(kindValue)
        return instance
