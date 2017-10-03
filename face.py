import numpy as np
from scipy.ndimage import imread
from scipy.misc import imsave
from skimage.draw import circle
from openface import AlignDlib
from subprocess import call
from os import remove
from os.path import isfile
from dlib import rectangle


landmark_model = AlignDlib("/root/openface/models/dlib/shape_predictor_68_face_landmarks.dat")


class ShepardsDistortion:

    def __init__(self, target_image, target_landmarks):
        imsave("target.png", target_image)
        self.target_landmarks = target_landmarks

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if isfile("target.png"):
            remove("target.png")
        if isfile("outcome.png"):
            remove("outcome.png")

    def transform(self, transform_landmarks):
        pts = ""
        for ((ly, lx), (ty, tx)) in zip(self.target_landmarks.points, transform_landmarks.points):
            pts += " %d,%d %d,%d" % (ly,lx,ty,tx)
        # for (ly, lx) in self.target_landmarks.points[:26]:
        #     pts += " %d,%d %d,%d" % (ly,lx,ly,lx)

        cmd = ["convert", "target.png", "-distort", "Shepards", pts, "outcome.png" ]
        call(cmd)
        return imread("outcome.png", mode="RGB")


class Landmarks:

    def __init__(self, bb, points):
        self.bb = bb
        self.points = points

    @classmethod
    def from_image(cls, image):
        bb = landmark_model.getLargestFaceBoundingBox(image)
        points = landmark_model.findLandmarks(image, bb)
        instance = cls(bb, points)
        instance.normalize()
        return instance

    def normalize(self):
        self.normalized = [(y - self.bb.top(), x - self.bb.left()) for (y, x) in self.points]
        self.normalized = [(y / float(self.bb.height()), x / float(self.bb.width())) for (y, x) in self.normalized]

    def get_transform(self, other):
        points = []
        for (t_y, t_x), (p_y, p_x) in zip(other.normalized, self.points):
            y = p_y + int(t_y * float(self.bb.height()))
            x = p_x + int(t_x * float(self.bb.width()))
            points.append((y, x))
        bb = rectangle(1, 2, 3, 4)
        instance = Landmarks(bb, points)
        instance.normalize()
        return instance

    def __sub__(self, other):
        points = [(y1-y2, x1-x2) for ((y1, x1), (y2, x2)) in zip(self.points, other.points)]
        normalized = [(y1-y2, x1-x2) for ((y1, x1), (y2, x2)) in zip(self.normalized, other.normalized)]
        bb = rectangle(self.bb.left()   - other.bb.left(),
                       self.bb.top()    - other.bb.top(),
                       self.bb.right()  - other.bb.right(),
                       self.bb.bottom() - other.bb.bottom())
        instance = Landmarks(bb, points)
        instance.normalized = normalized
        return instance

    def __mul__(self, val):
        points = [(y*val, x*val) for (y, x) in self.points]
        bb = rectangle(self.bb.left()* val, self.bb.top()* val, self.bb.right()* val, self.bb.bottom()* val)
        instance = Landmarks(bb, points)
        instance.normalize()
        return instance


class WarpImage:

    def __init__(self, image_data):
        self.image_data = image_data

    def save(self, path):
        imsave(path, self.image_data)

def draw_landmarks_on_image(image, lms):
    marked = np.copy(image)
    for (y, x) in lms.points:
        rr, cc = circle(x, y, 2.0, marked.shape)
        marked[rr, cc, :] = [255, 0, 0]
    return marked


class FaceWarp:

    def __init__(self, target_image, base_image, warp_images):
        if type(target_image) is str:
            self.target_image = imread(target_image, mode='RGB')
        else:
            self.target_image = target_image

        if type(base_image) is str:
            self.base_image = imread(base_image, mode='RGB')
        else:
            self.base_image = base_image

        self.warp_images = []
        for warp_image in warp_images:
            if type(warp_image) is str:
                self.warp_images.append(imread(warp_image, mode='RGB'))
            else:
                self.warp_images.append(warp_image)

    def get_warps(self):
        target_lms = Landmarks.from_image(self.target_image)
        imsave("outcomes/target_lms.png", draw_landmarks_on_image(self.target_image, target_lms))
        base_lms = Landmarks.from_image(self.base_image)
        imsave("outcomes/base_lms.png", draw_landmarks_on_image(self.base_image, base_lms))
        with ShepardsDistortion(self.target_image, target_lms) as distort:
            i = 1
            for warp_image in self.warp_images:
                warp_lms = Landmarks.from_image(warp_image)
                imsave("outcomes/input_lms_%d.png" % i, draw_landmarks_on_image(warp_image, warp_lms))
                print(((base_lms - warp_lms) * 100).points)
                transform_lms = target_lms.get_transform(warp_lms - base_lms)
                distorted = WarpImage(distort.transform(transform_lms))
                imsave("outcomes/warp_lms_%d.png" % i, draw_landmarks_on_image(distorted.image_data, transform_lms))
                i = i + 1
                yield distorted


if __name__ == "__main__":
    warper = FaceWarp("static/face1.jpg", "inputs/0.png", ["inputs/1.png", "inputs/2.png"])
    for i, warped in enumerate(warper.get_warps()):
        warped.save("outcomes/%d.png" % i)
