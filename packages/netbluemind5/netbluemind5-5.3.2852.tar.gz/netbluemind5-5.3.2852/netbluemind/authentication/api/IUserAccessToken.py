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

IUserAccessToken_VERSION = "5.3.2852"


class IUserAccessToken(BaseEndpoint):
    def __init__(self, apiKey, url):
        self.url = url
        self.apiKey = apiKey
        self.base = url + '/auth/access_token'

    def authCodeReceived(self, state, code):
        postUri = "/_auth"
        __data__ = None
        __encoded__ = None
        queryParams = {'state': state, 'code': code}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IUserAccessToken_VERSION}, data=__encoded__)
        from netbluemind.authentication.api.AccessTokenInfo import AccessTokenInfo
        from netbluemind.authentication.api.AccessTokenInfo import __AccessTokenInfoSerDer__
        return self.handleResult__(__AccessTokenInfoSerDer__(), response)

    def getTokenInfo(self, external_system, baseUrl):
        postUri = "/_info"
        __data__ = None
        __encoded__ = None
        queryParams = {'external_system': external_system, 'baseUrl': baseUrl}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IUserAccessToken_VERSION}, data=__encoded__)
        from netbluemind.authentication.api.AccessTokenInfo import AccessTokenInfo
        from netbluemind.authentication.api.AccessTokenInfo import __AccessTokenInfoSerDer__
        return self.handleResult__(__AccessTokenInfoSerDer__(), response)
