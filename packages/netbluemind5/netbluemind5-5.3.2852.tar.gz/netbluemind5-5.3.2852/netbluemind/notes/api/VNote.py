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


class VNote:
    def __init__(self):
        self.height = None
        self.width = None
        self.posX = None
        self.posY = None
        self.color = None
        self.body = None
        self.subject = None
        self.categories = None
        pass


class __VNoteSerDer__:
    def __init__(self):
        pass

    def parse(self, value):
        if (value == None):
            return None
        instance = VNote()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        heightValue = value['height']
        instance.height = serder.INT.parse(heightValue)
        widthValue = value['width']
        instance.width = serder.INT.parse(widthValue)
        posXValue = value['posX']
        instance.posX = serder.INT.parse(posXValue)
        posYValue = value['posY']
        instance.posY = serder.INT.parse(posYValue)
        from netbluemind.notes.api.VNoteColor import VNoteColor
        from netbluemind.notes.api.VNoteColor import __VNoteColorSerDer__
        colorValue = value['color']
        instance.color = __VNoteColorSerDer__().parse(colorValue)
        bodyValue = value['body']
        instance.body = serder.STRING.parse(bodyValue)
        subjectValue = value['subject']
        instance.subject = serder.STRING.parse(subjectValue)
        from netbluemind.tag.api.TagRef import TagRef
        from netbluemind.tag.api.TagRef import __TagRefSerDer__
        categoriesValue = value['categories']
        instance.categories = serder.ListSerDer(
            __TagRefSerDer__()).parse(categoriesValue)
        return instance

    def encode(self, value):
        if (value == None):
            return None
        instance = dict()
        self.encodeInternal(value, instance)
        return instance

    def encodeInternal(self, value, instance):

        heightValue = value.height
        instance["height"] = serder.INT.encode(heightValue)
        widthValue = value.width
        instance["width"] = serder.INT.encode(widthValue)
        posXValue = value.posX
        instance["posX"] = serder.INT.encode(posXValue)
        posYValue = value.posY
        instance["posY"] = serder.INT.encode(posYValue)
        from netbluemind.notes.api.VNoteColor import VNoteColor
        from netbluemind.notes.api.VNoteColor import __VNoteColorSerDer__
        colorValue = value.color
        instance["color"] = __VNoteColorSerDer__().encode(colorValue)
        bodyValue = value.body
        instance["body"] = serder.STRING.encode(bodyValue)
        subjectValue = value.subject
        instance["subject"] = serder.STRING.encode(subjectValue)
        from netbluemind.tag.api.TagRef import TagRef
        from netbluemind.tag.api.TagRef import __TagRefSerDer__
        categoriesValue = value.categories
        instance["categories"] = serder.ListSerDer(
            __TagRefSerDer__()).encode(categoriesValue)
        return instance
