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


class VNoteChanges:
    def __init__(self):
        self.add = None
        self.modify = None
        self.delete = None
        pass


class __VNoteChangesSerDer__:
    def __init__(self):
        pass

    def parse(self, value):
        if (value == None):
            return None
        instance = VNoteChanges()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.notes.api.VNoteChangesItemAdd import VNoteChangesItemAdd
        from netbluemind.notes.api.VNoteChangesItemAdd import __VNoteChangesItemAddSerDer__
        addValue = value['add']
        instance.add = serder.ListSerDer(
            __VNoteChangesItemAddSerDer__()).parse(addValue)
        from netbluemind.notes.api.VNoteChangesItemModify import VNoteChangesItemModify
        from netbluemind.notes.api.VNoteChangesItemModify import __VNoteChangesItemModifySerDer__
        modifyValue = value['modify']
        instance.modify = serder.ListSerDer(
            __VNoteChangesItemModifySerDer__()).parse(modifyValue)
        from netbluemind.notes.api.VNoteChangesItemDelete import VNoteChangesItemDelete
        from netbluemind.notes.api.VNoteChangesItemDelete import __VNoteChangesItemDeleteSerDer__
        deleteValue = value['delete']
        instance.delete = serder.ListSerDer(
            __VNoteChangesItemDeleteSerDer__()).parse(deleteValue)
        return instance

    def encode(self, value):
        if (value == None):
            return None
        instance = dict()
        self.encodeInternal(value, instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.notes.api.VNoteChangesItemAdd import VNoteChangesItemAdd
        from netbluemind.notes.api.VNoteChangesItemAdd import __VNoteChangesItemAddSerDer__
        addValue = value.add
        instance["add"] = serder.ListSerDer(
            __VNoteChangesItemAddSerDer__()).encode(addValue)
        from netbluemind.notes.api.VNoteChangesItemModify import VNoteChangesItemModify
        from netbluemind.notes.api.VNoteChangesItemModify import __VNoteChangesItemModifySerDer__
        modifyValue = value.modify
        instance["modify"] = serder.ListSerDer(
            __VNoteChangesItemModifySerDer__()).encode(modifyValue)
        from netbluemind.notes.api.VNoteChangesItemDelete import VNoteChangesItemDelete
        from netbluemind.notes.api.VNoteChangesItemDelete import __VNoteChangesItemDeleteSerDer__
        deleteValue = value.delete
        instance["delete"] = serder.ListSerDer(
            __VNoteChangesItemDeleteSerDer__()).encode(deleteValue)
        return instance
