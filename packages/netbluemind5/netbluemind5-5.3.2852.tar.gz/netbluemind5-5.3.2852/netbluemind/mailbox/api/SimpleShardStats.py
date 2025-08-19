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


class SimpleShardStats:
    def __init__(self):
        self.indexName = None
        self.mailboxes = None
        self.aliases = None
        self.docCount = None
        self.deletedCount = None
        self.externalRefreshCount = None
        self.externalRefreshDuration = None
        self.size = None
        pass


class __SimpleShardStatsSerDer__:
    def __init__(self):
        pass

    def parse(self, value):
        if (value == None):
            return None
        instance = SimpleShardStats()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        indexNameValue = value['indexName']
        instance.indexName = serder.STRING.parse(indexNameValue)
        mailboxesValue = value['mailboxes']
        instance.mailboxes = serder.SetSerDer(
            serder.STRING).parse(mailboxesValue)
        aliasesValue = value['aliases']
        instance.aliases = serder.SetSerDer(serder.STRING).parse(aliasesValue)
        docCountValue = value['docCount']
        instance.docCount = serder.LONG.parse(docCountValue)
        deletedCountValue = value['deletedCount']
        instance.deletedCount = serder.LONG.parse(deletedCountValue)
        externalRefreshCountValue = value['externalRefreshCount']
        instance.externalRefreshCount = serder.LONG.parse(
            externalRefreshCountValue)
        externalRefreshDurationValue = value['externalRefreshDuration']
        instance.externalRefreshDuration = serder.LONG.parse(
            externalRefreshDurationValue)
        sizeValue = value['size']
        instance.size = serder.LONG.parse(sizeValue)
        return instance

    def encode(self, value):
        if (value == None):
            return None
        instance = dict()
        self.encodeInternal(value, instance)
        return instance

    def encodeInternal(self, value, instance):

        indexNameValue = value.indexName
        instance["indexName"] = serder.STRING.encode(indexNameValue)
        mailboxesValue = value.mailboxes
        instance["mailboxes"] = serder.SetSerDer(
            serder.STRING).encode(mailboxesValue)
        aliasesValue = value.aliases
        instance["aliases"] = serder.SetSerDer(
            serder.STRING).encode(aliasesValue)
        docCountValue = value.docCount
        instance["docCount"] = serder.LONG.encode(docCountValue)
        deletedCountValue = value.deletedCount
        instance["deletedCount"] = serder.LONG.encode(deletedCountValue)
        externalRefreshCountValue = value.externalRefreshCount
        instance["externalRefreshCount"] = serder.LONG.encode(
            externalRefreshCountValue)
        externalRefreshDurationValue = value.externalRefreshDuration
        instance["externalRefreshDuration"] = serder.LONG.encode(
            externalRefreshDurationValue)
        sizeValue = value.size
        instance["size"] = serder.LONG.encode(sizeValue)
        return instance
