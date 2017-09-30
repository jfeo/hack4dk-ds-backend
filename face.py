import numpy as np
from scipy.ndimage import imread
from scipy.misc import imsave
from openface import AlignDlib
from subprocess import call

def get_landmarks(rgbImg):
    align = AlignDlib("/root/openface/models/dlib/shape_predictor_68_face_landmarks.dat")
    bb = align.getLargestFaceBoundingBox(rgbImg)
    lms = align.findLandmarks(rgbImg, bb)
    norm_lms = [(y - bb.top(), x - bb.left() < bb.width()) for (y, x) in lms]
    norm_lms = [(y / float(bb.height()), x / float(bb.width())) for (y, x) in norm_lms]
    return (bb, lms, norm_lms)

def landmark_differences(lms1, lms2):
    return [(y2-y1, x2-x1) for ((y1, x1), (y2, x2)) in zip(lms1, lms2)]

def generate_warp(outcome_name, art_img_fname, lms, trans_lms):
    pts = ""
    for ((ly, lx), (ty, tx)) in zip(lms[26:], trans_lms[26:]):
        pts += " %d,%d %d,%d" % (ly,lx,ty,tx)
    for (ly, lx) in lms[:26]:
        pts += " %d,%d %d,%d" % (ly,lx,ly,lx)

    cmd = ["convert", art_img_fname, "-distort", "Shepards", pts, outcome_name ]
    call(cmd)

def warped_art(uuid, art_img_fname, transforms):
    art_img = imread(art_img_fname, mode="RGB")
    (art_bb, art_lms, norm_art_lms) = get_landmarks(art_img)
    for i, t in enumerate(transforms):
        transformed_art_lms = [(a_y + int(t_y * float(art_bb.height())), a_x + int(t_x * float(art_bb.width()))) for ((t_y, t_x), (a_y, a_x)) in zip(t, art_lms)]
        generate_warp("outcomes/%s_%d.png" % (uuid, i), art_img_fname, art_lms, transformed_art_lms)

def generate_transforms(fnames):
    orig = imread(fnames[0], mode="RGB")
    (orig_bb, orig_lms, orig_norm_lms) = get_landmarks(orig)
    transforms = []
    for fname in fnames[1:]:
        img = imread(fname, mode="RGB")
        (bb, lms, norm_lms) = get_landmarks(img)
        transforms.append(landmark_differences(orig_norm_lms, norm_lms))
    return transforms
