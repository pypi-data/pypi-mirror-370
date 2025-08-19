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
from enum import Enum


class MailFilterRuleActionName(Enum):
    ADD_HEADER = 'ADD_HEADER'
    CATEGORIZE = 'CATEGORIZE'
    COPY = 'COPY'
    CUSTOM = 'CUSTOM'
    DEFERRED_ACTION = 'DEFERRED_ACTION'
    DISCARD = 'DISCARD'
    MARK_AS_DELETED = 'MARK_AS_DELETED'
    MARK_AS_IMPORTANT = 'MARK_AS_IMPORTANT'
    MARK_AS_READ = 'MARK_AS_READ'
    MOVE = 'MOVE'
    PRIORITIZE = 'PRIORITIZE'
    REDIRECT = 'REDIRECT'
    REMOVE_HEADERS = 'REMOVE_HEADERS'
    REPLY = 'REPLY'
    SET_FLAGS = 'SET_FLAGS'
    TRANSFER = 'TRANSFER'
    UNCATEGORIZE = 'UNCATEGORIZE'
    UNFOLLOW = 'UNFOLLOW'


class __MailFilterRuleActionNameSerDer__:
    def __init__(self):
        pass

    def parse(self, value):
        if (value == None):
            return None
        instance = MailFilterRuleActionName[value]
        return instance

    def encode(self, value):
        if (value == None):
            return None
        instance = value.value
        return instance
