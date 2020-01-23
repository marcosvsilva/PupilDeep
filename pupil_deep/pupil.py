import numpy as np
import cv2
from pupil_deep import PupilDeep


class Pupil:
    def __init__(self):
        # Orientations
        # self.orientations = ['north', 'northeast', 'east', 'southeast', 'south', 'southwest', 'west', 'northwest']
        self._orientations = ['southeast']

        # Variables
        self._center = []
        self._default_color = 0

        # Dependences
        self._pupul_deep = PupilDeep()

        # Params
        self._thresh_binary = 25
        self._threshold_binary = 255
        self._radius_range = range(35, 100, 1)
        self._pupil_color_range = range(0, 170, 1)
        self._new_color_pupil = 10
        self._range_search_reflex = 40

    def _mask_reflex(self, image, binary):
        new_image = np.copy(image)

        i, j = self._center
        for x in range(i-self._range_search_reflex, i+self._range_search_reflex):
            for y in range(j-self._range_search_reflex, j+self._range_search_reflex):
                if binary[y, x] != 0:
                    new_image[y, x] = self._new_color_pupil

        return new_image

    def _binarize(self, image):
        return cv2.threshold(image, self._thresh_binary, self._threshold_binary, cv2.THRESH_BINARY)[1]

    def _calc_radius(self, image):
        radius, points = np.array([]), []
        for orientation in self._orientations:
            point = self._search_edge(image, orientation)
            points.append(point)
            radius = np.append(radius, self._calc_distance(point))

        return points, radius[0]

    def _calc_distance(self, points):
        return int((((self._center[0]-points[0]) ** 2) + ((self._center[1] - points[1]) ** 2)) ** (1/2))

    def _search_edge(self, image, orientation):
        i, j = self._center
        x, y = image.shape
        while 0 <= i < y and 0 <= j < x:
            if image[j, i] != self._default_color:
                break
            else:
                i, j = self._calc_coordinates(orientation, (i, j))
        return [i, j]

    def _calc_coordinates(self, orientation, position):
        if orientation == 'northwest':
            position = self._inc_coordinates('north', position)
            position = self._inc_coordinates('west', position)
        elif orientation == 'northeast':
            position = self._inc_coordinates('north', position)
            position = self._inc_coordinates('east', position)
        elif orientation == 'southwest':
            position = self._inc_coordinates('south', position)
            position = self._inc_coordinates('west', position)
        elif orientation == 'southeast':
            position = self._inc_coordinates('south', position)
            position = self._inc_coordinates('east', position)
        else:
            position = self._inc_coordinates(orientation, position)
        return position

    def _inc_coordinates(self, orientation, position):
        i, j = position[0], position[1]
        if orientation == 'south':
            j += 1
        elif orientation == 'north':
            j -= 1
        elif orientation == 'east':
            i += 1
        elif orientation == 'west':
            i -= 1
        return i, j

    def pupil_detect(self, image, number_cal=1):
        original = np.copy(image)

        self._center = self._pupul_deep.run(image)

        binary = self._binarize(image)

        self._default_color = binary[self._center[1], self._center[0]]

        points, radius = self._calc_radius(binary)

        if int(radius) not in self._radius_range:
            if number_cal <= 5:
                new_image = self._mask_reflex(original, binary)
                return self.pupil_detect(new_image, number_cal + 1)

        return self._center, int(radius), points, binary
