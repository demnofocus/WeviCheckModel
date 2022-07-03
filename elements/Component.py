from elements.Bbox import Bbox
import uuid


def set_uuid():
    return uuid.uuid1()


def cvt_compos_relative_pos(compos, col_min_base, row_min_base):
    for compo in compos:
        compo.to_relative_position(col_min_base, row_min_base)


def compos_containment(compos):
    for i in range(len(compos) - 1):
        for j in range(i + 1, len(compos)):
            relation = compos[i].get_relationship(compos[j])
            if relation == -1:
                compos[j].contain.append(i)
            if relation == 1:
                compos[i].contain.append(j)


def compos_update(compos, org_shape):
    for i, compo in enumerate(compos):
        # start from 1, id 0 is background
        compo.update(compo.id, org_shape)

        
class Component:
    def __init__(self, region, image_shape):
        self.id = str(set_uuid())
        self.region = region
        self.boundary = self.get_boundary()
        self.bbox = self.get_bbox()
        self.bbox_area = self.bbox.box_area

        self.region_area = len(region)
        self.width = len(self.boundary[0])
        self.height = len(self.boundary[2])
        self.image_shape = image_shape
        self.area = self.width * self.height

        self.category = 'Compo'
        self.contain = []
        self.rect_ = None
        self.line_ = None
        self.redundant = False

    def update(self, id, org_shape):
        self.id = id
        self.image_shape = org_shape
        self.width = self.bbox.width
        self.height = self.bbox.height
        self.bbox_area = self.bbox.box_area
        self.area = self.width * self.height

    def get_boundaries(self):
        return self.bbox.boundary_left, self.bbox.boundary_bottom, self.bbox.boundary_right, self.bbox.boundary_top

    # def compo_update_bbox_area(self):
    #     self.bbox_area = self.bbox.box_cal_area()

    def get_boundary(self):
        border_up, border_bottom, border_left, border_right = {}, {}, {}, {}
        for point in self.region:

            if point[1] not in border_up or border_up[point[1]] > point[0]:
                border_up[point[1]] = point[0]
            if point[1] not in border_bottom or border_bottom[point[1]] < point[0]:
                border_bottom[point[1]] = point[0]
            if point[0] not in border_left or border_left[point[0]] > point[1]:
                border_left[point[0]] = point[1]
            if point[0] not in border_right or border_right[point[0]] < point[1]:
                border_right[point[0]] = point[1]

        boundary = [border_up, border_bottom, border_left, border_right]
        # descending sort
        for i in range(len(boundary)):
            boundary[i] = [[k, boundary[i][k]] for k in boundary[i].keys()]
            boundary[i] = sorted(boundary[i], key=lambda x: x[0])
        return boundary

    def get_bbox(self):
        boundary_left, boundary_bottom = (int(min(self.boundary[0][0][0], self.boundary[1][-1][0])),
                                          int(min(self.boundary[2][0][0], self.boundary[3][-1][0])))
        boundary_right, boundary_top = (int(max(self.boundary[0][0][0], self.boundary[1][-1][0])),
                                        int(max(self.boundary[2][0][0], self.boundary[3][-1][0])))
        bbox = Bbox(boundary_left, boundary_bottom, boundary_right, boundary_top)
        return bbox

    def is_rectangle(self, min_rec_evenness, max_dent_ratio, test=False):
        """
        detect if an object is rectangle by evenness and dent of each border
        """
        dent_direction = [1, -1, 1, -1]  # direction for convex

        flat = 0
        parameter = 0
        for n, border in enumerate(self.boundary):
            parameter += len(border)
            # dent detection
            pit = 0  # length of pit
            depth = 0  # the degree of surface changing
            if n <= 1:
                adj_side = max(len(self.boundary[2]), len(self.boundary[3]))  # get maximum length of adjacent side
            else:
                adj_side = max(len(self.boundary[0]), len(self.boundary[1]))

            abnormal = 0
            for i in range(int(3 + len(border) * 0.02), len(border) - 1):
                # calculate gradient
                difference = border[i][1] - border[i + 1][1]
                # the degree of surface changing
                depth += difference
                # ignore noise at the start of each direction
                if i / len(border) < 0.08 and (dent_direction[n] * difference) / adj_side > 0.5:
                    depth = 0  # reset

                # if the change of the surface is too large, count it as part of abnormal change
                if abs(depth) / adj_side > 0.3:
                    abnormal += 1  # count the size of the abnormal change
                    # if the abnormal change is too big, the shape should not be a rectangle
                    if abnormal / len(border) > 0.1:
                        self.rect_ = False
                        return False
                    continue
                else:
                    # reset the abnormal change if the depth back to normal
                    abnormal = 0

                # if sunken and the surface changing is large, then counted as pit
                if dent_direction[n] * depth < 0 and abs(depth) / adj_side > 0.15:
                    pit += 1
                    continue

                # if the surface is not changing to a pit and the gradient is zero, then count it as flat
                if abs(depth) < 1 + adj_side * 0.015:
                    flat += 1
                # if test:
                # # print(depth, adj_side, flat)
            # if the pit is too big, the shape should not be a rectangle
            if pit / len(border) > max_dent_ratio:
                self.rect_ = False
                return False

        # ignore text and irregular shape
        if self.height / self.image_shape[0] > 0.3:
            min_rec_evenness = 0.85
        if (flat / parameter) < min_rec_evenness:
            self.rect_ = False
            return False
        self.rect_ = True
        return True

    def is_line(self, min_line_thickness):
        """
        Check this object is line by checking its boundary
        :param min_line_thickness:
        :return: Boolean
        """
        # horizontally
        slim = 0
        for i in range(self.width):
            if abs(self.boundary[1][i][1] - self.boundary[0][i][1]) <= min_line_thickness:
                slim += 1

        if slim / len(self.boundary[0]) > 0.93:
            self.line_ = True
            return True

        # vertically
        slim = 0
        for i in range(self.height):
            if abs(self.boundary[2][i][1] - self.boundary[3][i][1]) <= min_line_thickness:
                slim += 1

        if slim / len(self.boundary[2]) > 0.93:
            self.line_ = True
            return True

        self.line_ = False
        return False

    def get_relationship(self, compo_b, bias=(0, 0)):
        """
        :return: -1 : a in b
                 0  : a, b are not intersected
                 1  : b in a
                 2  : a, b are identical or intersected
        """
        return self.bbox.bbox_relation_nms(compo_b.bbox, bias)

    def to_relative_position(self, col_min_base, row_min_base):
        """
        Convert to relative position based on base coordinator
        """
        self.bbox.bbox_cvt_relative_position(col_min_base, row_min_base)

    def merge(self, compo_b):
        self.bbox = self.bbox.get_merged(compo_b.bbox)
        self.update(self.id, self.image_shape)

    def get_clipped(self, img, pad=0, show=False):
        (column_min, boundary_bottom, column_max, boundary_top) = self.get_boundaries()

        column_min = max(column_min - pad, 0)
        column_max = min(column_max + pad, img.shape[1])
        boundary_bottom = max(boundary_bottom - pad, 0)
        boundary_top = min(boundary_top + pad, img.shape[0])
        clip = img[boundary_bottom:boundary_top, column_min:column_max]

        return clip
