import numpy as np


class Bbox:
    def __init__(self, boundary_left, boundary_bottom, boundary_right, boundary_top):
        self.boundary_left = boundary_left
        self.boundary_bottom = boundary_bottom
        self.boundary_right = boundary_right
        self.boundary_top = boundary_top

        self.width = boundary_right - boundary_left
        self.height = boundary_top - boundary_bottom
        self.box_area = self.width * self.height

    def bbox_relation_nms(self, bbox_b, bias=(0, 0)):
        """
        Calculate the relation between two rectangles by nms
        :return:
            -1 : a in b
            0  : a, b are not intersected
            1  : b in a
            2  : a, b are intersected
        """
        bias_col, bias_row = bias
        # get the intersected area
        col_min_s = max(self.boundary_left - bias_col, bbox_b.boundary_left - bias_col)
        row_min_s = max(self.boundary_bottom - bias_row, bbox_b.boundary_bottom - bias_row)
        col_max_s = min(self.boundary_right + bias_col, bbox_b.boundary_right + bias_col)
        row_max_s = min(self.boundary_top + bias_row, bbox_b.boundary_top + bias_row)
        w = np.maximum(0, col_max_s - col_min_s)
        h = np.maximum(0, row_max_s - row_min_s)
        inter = w * h
        area_a = (self.boundary_right - self.boundary_left) * (self.boundary_top - self.boundary_bottom)
        area_b = (bbox_b.boundary_right - bbox_b.boundary_left) * (bbox_b.boundary_top - bbox_b.boundary_bottom)
        iou = inter / (area_a + area_b - inter)
        ioa = inter / self.box_area
        iob = inter / bbox_b.box_area

        # not intersected
        if iou == 0 and ioa == 0 and iob == 0:
            return 0
        # contained by b
        if ioa >= 1:
            return -1
        # contains b
        if iob >= 1:
            return 1
        # intersected
        if iou >= 0.02 or iob > 0.2 or ioa > 0.2:
            return 2
        return 0

    def bbox_cvt_relative_position(self, col_min_base, row_min_base):
        """
        Convert to relative position based on base coordinator
        """
        self.boundary_left += col_min_base
        self.boundary_right += col_min_base
        self.boundary_bottom += row_min_base
        self.boundary_top += row_min_base

    def get_merged(self, bbox_b):
        """
        Merge two intersected bboxes
        """
        return Bbox(boundary_left=min(self.boundary_left, bbox_b.boundary_left),
                    boundary_bottom=max(self.boundary_right, bbox_b.boundary_right),
                    boundary_right=min(self.boundary_bottom, bbox_b.boundary_bottom),
                    boundary_top=max(self.boundary_top, bbox_b.boundary_top))
