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


class AccessTokenInfo:
    def __init__(self):
        self.status = None
        self.externalAuthEndPointUrl = None
        self.internalRedirectUrl = None
        self.applicationId = None
        self.state = None
        self.codeChallenge = None
        self.codeChallengeMethod = None
        self.responseType = None
        self.scope = None
        self.url = None
        pass


class __AccessTokenInfoSerDer__:
    def __init__(self):
        pass

    def parse(self, value):
        if (value == None):
            return None
        instance = AccessTokenInfo()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.authentication.api.AccessTokenInfoTokenStatus import AccessTokenInfoTokenStatus
        from netbluemind.authentication.api.AccessTokenInfoTokenStatus import __AccessTokenInfoTokenStatusSerDer__
        statusValue = value['status']
        instance.status = __AccessTokenInfoTokenStatusSerDer__().parse(statusValue)
        externalAuthEndPointUrlValue = value['externalAuthEndPointUrl']
        instance.externalAuthEndPointUrl = serder.STRING.parse(
            externalAuthEndPointUrlValue)
        internalRedirectUrlValue = value['internalRedirectUrl']
        instance.internalRedirectUrl = serder.STRING.parse(
            internalRedirectUrlValue)
        applicationIdValue = value['applicationId']
        instance.applicationId = serder.STRING.parse(applicationIdValue)
        stateValue = value['state']
        instance.state = serder.STRING.parse(stateValue)
        codeChallengeValue = value['codeChallenge']
        instance.codeChallenge = serder.STRING.parse(codeChallengeValue)
        codeChallengeMethodValue = value['codeChallengeMethod']
        instance.codeChallengeMethod = serder.STRING.parse(
            codeChallengeMethodValue)
        responseTypeValue = value['responseType']
        instance.responseType = serder.STRING.parse(responseTypeValue)
        scopeValue = value['scope']
        instance.scope = serder.STRING.parse(scopeValue)
        urlValue = value['url']
        instance.url = serder.STRING.parse(urlValue)
        return instance

    def encode(self, value):
        if (value == None):
            return None
        instance = dict()
        self.encodeInternal(value, instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.authentication.api.AccessTokenInfoTokenStatus import AccessTokenInfoTokenStatus
        from netbluemind.authentication.api.AccessTokenInfoTokenStatus import __AccessTokenInfoTokenStatusSerDer__
        statusValue = value.status
        instance["status"] = __AccessTokenInfoTokenStatusSerDer__().encode(
            statusValue)
        externalAuthEndPointUrlValue = value.externalAuthEndPointUrl
        instance["externalAuthEndPointUrl"] = serder.STRING.encode(
            externalAuthEndPointUrlValue)
        internalRedirectUrlValue = value.internalRedirectUrl
        instance["internalRedirectUrl"] = serder.STRING.encode(
            internalRedirectUrlValue)
        applicationIdValue = value.applicationId
        instance["applicationId"] = serder.STRING.encode(applicationIdValue)
        stateValue = value.state
        instance["state"] = serder.STRING.encode(stateValue)
        codeChallengeValue = value.codeChallenge
        instance["codeChallenge"] = serder.STRING.encode(codeChallengeValue)
        codeChallengeMethodValue = value.codeChallengeMethod
        instance["codeChallengeMethod"] = serder.STRING.encode(
            codeChallengeMethodValue)
        responseTypeValue = value.responseType
        instance["responseType"] = serder.STRING.encode(responseTypeValue)
        scopeValue = value.scope
        instance["scope"] = serder.STRING.encode(scopeValue)
        urlValue = value.url
        instance["url"] = serder.STRING.encode(urlValue)
        return instance
