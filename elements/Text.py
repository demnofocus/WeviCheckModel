import cv2

from elements.Bbox import Bbox
import uuid


def set_uuid():
    return uuid.uuid1()


class Text:
    def __init__(self, content, boundary):
        self.id = str(set_uuid())
        self.content = content
        self.boundary = boundary
        self.width = self.boundary['right'] - self.boundary['left']
        self.height = self.boundary['top'] - self.boundary['bottom']
        self.area = self.width * self.height
        self.word_width = self.width / len(self.content)
        self.bbox = self.set_bbox()
        self.category = 'Text'

    def set_bbox(self):
        boundary_left, boundary_bottom = self.boundary['left'], self.boundary['bottom']
        boundary_right, boundary_top = self.boundary['right'], self.boundary['top']
        bbox = Bbox(boundary_left, boundary_bottom, boundary_right, boundary_top)
        return bbox
