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


class SharedContainer:
    def __init__(self):
        self.shared = None
        self.givenRights = None
        pass


class __SharedContainerSerDer__:
    def __init__(self):
        pass

    def parse(self, value):
        if (value == None):
            return None
        instance = SharedContainer()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.core.container.model.BaseContainerDescriptor import BaseContainerDescriptor
        from netbluemind.core.container.model.BaseContainerDescriptor import __BaseContainerDescriptorSerDer__
        sharedValue = value['shared']
        instance.shared = __BaseContainerDescriptorSerDer__().parse(sharedValue)
        from netbluemind.core.container.model.acl.AccessControlEntry import AccessControlEntry
        from netbluemind.core.container.model.acl.AccessControlEntry import __AccessControlEntrySerDer__
        givenRightsValue = value['givenRights']
        instance.givenRights = serder.SetSerDer(
            __AccessControlEntrySerDer__()).parse(givenRightsValue)
        return instance

    def encode(self, value):
        if (value == None):
            return None
        instance = dict()
        self.encodeInternal(value, instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.core.container.model.BaseContainerDescriptor import BaseContainerDescriptor
        from netbluemind.core.container.model.BaseContainerDescriptor import __BaseContainerDescriptorSerDer__
        sharedValue = value.shared
        instance["shared"] = __BaseContainerDescriptorSerDer__().encode(
            sharedValue)
        from netbluemind.core.container.model.acl.AccessControlEntry import AccessControlEntry
        from netbluemind.core.container.model.acl.AccessControlEntry import __AccessControlEntrySerDer__
        givenRightsValue = value.givenRights
        instance["givenRights"] = serder.SetSerDer(
            __AccessControlEntrySerDer__()).encode(givenRightsValue)
        return instance
