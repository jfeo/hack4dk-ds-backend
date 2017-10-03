import unittest as ut
from dlib import rectangle
from face import *


class LandmarksTestCase(ut.TestCase):

    def assertSubtractionPoints(self, pts1, pts2, expected):
        bottom_1, right_1 = reduce(lambda (y1, x1), (y2, x2): (max(y1, y2), max(x1, x2)), pts1)
        top_1, left_1 = reduce(lambda (y1, x1), (y2, x2): (min(y1, y2), min(x1, x2)), pts1)
        l1 = Landmarks(rectangle(left_1, top_1, right_1, bottom_1), pts1)
        l1.normalize()
        bottom_2, right_2 = reduce(lambda (y1, x1), (y2, x2): (max(y1, y2), max(x1, x2)), pts2)
        top_2, left_2 = reduce(lambda (y1, x1), (y2, x2): (min(y1, y2), min(x1, x2)), pts2)
        l2 = Landmarks(rectangle(left_2, top_2, right_2, bottom_2), pts2)
        l2.normalize()
        self.assertEquals((l1 - l2).points, expected)

    def test_sub(self):
        self.assertSubtractionPoints(
                [(10, 10), (10, 10), (10, 10)],
                [(5, 5), (5, 5), (5, 5)],
                [(5, 5), (5, 5), (5, 5)]
            )
        self.assertSubtractionPoints(
                [(0, 0), (0, 0), (0, 0)],
                [(5, 5), (5, 5), (5, 5)],
                [(-5, -5), (-5, -5), (-5, -5)]
            )
        self.assertSubtractionPoints(
                [(12345, 12345), (12345, 12345), (10, 10)],
                [(12345, 0), (-12345, 12345), (0, 20)],
                [(0, 12345), (12345*2, 0), (10, -10)]
            )

    def test_mul(self):
        pass

class FaceWarpTestCase(ut.TestCase):

    def test_get_warps(self):
        pass

alltests = ut.TestSuite(map(ut.TestLoader().loadTestsFromTestCase, [FaceWarpTestCase, LandmarksTestCase]))

if __name__ == "__name__":
    ut.main(defaultTest=alltests)
