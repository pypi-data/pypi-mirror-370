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


class CertInfo:
    def __init__(self):
        self.usage = None
        self.x509Certificate = None
        pass


class __CertInfoSerDer__:
    def __init__(self):
        pass

    def parse(self, value):
        if (value == None):
            return None
        instance = CertInfo()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.addressbook.api.CertInfoCertUsage import CertInfoCertUsage
        from netbluemind.addressbook.api.CertInfoCertUsage import __CertInfoCertUsageSerDer__
        usageValue = value['usage']
        instance.usage = serder.SetSerDer(
            __CertInfoCertUsageSerDer__()).parse(usageValue)
        x509CertificateValue = value['x509Certificate']
        instance.x509Certificate = serder.ByteArraySerDer.parse(
            x509CertificateValue)
        return instance

    def encode(self, value):
        if (value == None):
            return None
        instance = dict()
        self.encodeInternal(value, instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.addressbook.api.CertInfoCertUsage import CertInfoCertUsage
        from netbluemind.addressbook.api.CertInfoCertUsage import __CertInfoCertUsageSerDer__
        usageValue = value.usage
        instance["usage"] = serder.SetSerDer(
            __CertInfoCertUsageSerDer__()).encode(usageValue)
        x509CertificateValue = value.x509Certificate
        instance["x509Certificate"] = serder.ByteArraySerDer.encode(
            x509CertificateValue)
        return instance
