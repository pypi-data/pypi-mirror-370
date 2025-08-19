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


class ConversationFlagUpdate:
    def __init__(self):
        self.conversationUids = None
        self.mailboxItemFlag = None
        pass


class __ConversationFlagUpdateSerDer__:
    def __init__(self):
        pass

    def parse(self, value):
        if (value == None):
            return None
        instance = ConversationFlagUpdate()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        conversationUidsValue = value['conversationUids']
        instance.conversationUids = serder.ListSerDer(
            serder.STRING).parse(conversationUidsValue)
        from netbluemind.backend.mail.api.flags.MailboxItemFlag import MailboxItemFlag
        from netbluemind.backend.mail.api.flags.MailboxItemFlag import __MailboxItemFlagSerDer__
        mailboxItemFlagValue = value['mailboxItemFlag']
        instance.mailboxItemFlag = __MailboxItemFlagSerDer__().parse(mailboxItemFlagValue)
        return instance

    def encode(self, value):
        if (value == None):
            return None
        instance = dict()
        self.encodeInternal(value, instance)
        return instance

    def encodeInternal(self, value, instance):

        conversationUidsValue = value.conversationUids
        instance["conversationUids"] = serder.ListSerDer(
            serder.STRING).encode(conversationUidsValue)
        from netbluemind.backend.mail.api.flags.MailboxItemFlag import MailboxItemFlag
        from netbluemind.backend.mail.api.flags.MailboxItemFlag import __MailboxItemFlagSerDer__
        mailboxItemFlagValue = value.mailboxItemFlag
        instance["mailboxItemFlag"] = __MailboxItemFlagSerDer__().encode(
            mailboxItemFlagValue)
        return instance
