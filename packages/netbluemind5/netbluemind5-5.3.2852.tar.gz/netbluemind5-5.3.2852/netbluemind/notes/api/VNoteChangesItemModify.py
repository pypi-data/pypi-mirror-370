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


class VNoteChangesItemModify:
    def __init__(self):
        self.uid = None
        self.version = None
        self.value = None
        self.sendNotification = None
        pass


class __VNoteChangesItemModifySerDer__:
    def __init__(self):
        pass

    def parse(self, value):
        if (value == None):
            return None
        instance = VNoteChangesItemModify()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        uidValue = value['uid']
        instance.uid = serder.STRING.parse(uidValue)
        versionValue = value['version']
        instance.version = serder.LONG.parse(versionValue)
        from netbluemind.notes.api.VNote import VNote
        from netbluemind.notes.api.VNote import __VNoteSerDer__
        valueValue = value['value']
        instance.value = __VNoteSerDer__().parse(valueValue)
        sendNotificationValue = value['sendNotification']
        instance.sendNotification = serder.BOOLEAN.parse(sendNotificationValue)
        return instance

    def encode(self, value):
        if (value == None):
            return None
        instance = dict()
        self.encodeInternal(value, instance)
        return instance

    def encodeInternal(self, value, instance):

        uidValue = value.uid
        instance["uid"] = serder.STRING.encode(uidValue)
        versionValue = value.version
        instance["version"] = serder.LONG.encode(versionValue)
        from netbluemind.notes.api.VNote import VNote
        from netbluemind.notes.api.VNote import __VNoteSerDer__
        valueValue = value.value
        instance["value"] = __VNoteSerDer__().encode(valueValue)
        sendNotificationValue = value.sendNotification
        instance["sendNotification"] = serder.BOOLEAN.encode(
            sendNotificationValue)
        return instance
