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
import json
from netbluemind.python import serder
from netbluemind.python.client import BaseEndpoint

IDirEntryMaintenance_VERSION = "5.3.2852"


class IDirEntryMaintenance(BaseEndpoint):
    def __init__(self, apiKey, url, domain, entryUid):
        self.url = url
        self.apiKey = apiKey
        self.base = url + '/directory/{domain}/{entryUid}/mgmt'
        self.domain_ = domain
        self.base = self.base.replace('{domain}', domain)
        self.entryUid_ = entryUid
        self.base = self.base.replace('{entryUid}', entryUid)

    def getAvailableOperations(self):
        postUri = "/_maintenance"
        __data__ = None
        __encoded__ = None
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IDirEntryMaintenance_VERSION}, data=__encoded__)
        from netbluemind.directory.api.MaintenanceOperation import MaintenanceOperation
        from netbluemind.directory.api.MaintenanceOperation import __MaintenanceOperationSerDer__
        return self.handleResult__(serder.ListSerDer(__MaintenanceOperationSerDer__()), response)

    def repair(self, config):
        postUri = "/_maintenance/repair"
        __data__ = None
        __encoded__ = None
        from netbluemind.directory.api.RepairConfig import RepairConfig
        from netbluemind.directory.api.RepairConfig import __RepairConfigSerDer__
        __data__ = __RepairConfigSerDer__().encode(config)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IDirEntryMaintenance_VERSION}, data=__encoded__)
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
