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

from netbluemind.mailbox.api.SimpleShardStats import SimpleShardStats
from netbluemind.mailbox.api.SimpleShardStats import __SimpleShardStatsSerDer__


class ShardStats (SimpleShardStats):
    def __init__(self):
        SimpleShardStats.__init__(self)
        self.topMailbox = None
        self.state = None
        pass


class __ShardStatsSerDer__:
    def __init__(self):
        pass

    def parse(self, value):
        if (value == None):
            return None
        instance = ShardStats()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        __SimpleShardStatsSerDer__().parseInternal(value, instance)
        from netbluemind.mailbox.api.ShardStatsMailboxStats import ShardStatsMailboxStats
        from netbluemind.mailbox.api.ShardStatsMailboxStats import __ShardStatsMailboxStatsSerDer__
        topMailboxValue = value['topMailbox']
        instance.topMailbox = serder.ListSerDer(
            __ShardStatsMailboxStatsSerDer__()).parse(topMailboxValue)
        from netbluemind.mailbox.api.ShardStatsState import ShardStatsState
        from netbluemind.mailbox.api.ShardStatsState import __ShardStatsStateSerDer__
        stateValue = value['state']
        instance.state = __ShardStatsStateSerDer__().parse(stateValue)
        return instance

    def encode(self, value):
        if (value == None):
            return None
        instance = dict()
        self.encodeInternal(value, instance)
        return instance

    def encodeInternal(self, value, instance):
        __SimpleShardStatsSerDer__().encodeInternal(value, instance)

        from netbluemind.mailbox.api.ShardStatsMailboxStats import ShardStatsMailboxStats
        from netbluemind.mailbox.api.ShardStatsMailboxStats import __ShardStatsMailboxStatsSerDer__
        topMailboxValue = value.topMailbox
        instance["topMailbox"] = serder.ListSerDer(
            __ShardStatsMailboxStatsSerDer__()).encode(topMailboxValue)
        from netbluemind.mailbox.api.ShardStatsState import ShardStatsState
        from netbluemind.mailbox.api.ShardStatsState import __ShardStatsStateSerDer__
        stateValue = value.state
        instance["state"] = __ShardStatsStateSerDer__().encode(stateValue)
        return instance
