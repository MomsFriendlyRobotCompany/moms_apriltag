##############################################
# The MIT License (MIT)
# Copyright (c) 2014 Kevin Walchko
# see LICENSE for full details
##############################################
# -*- coding: utf-8 -*
import numpy as np
import matplotlib.pyplot as plt


def visualizeTargetDetections(objpts, imgpts, img):
    """
    Plots the detected target tags and the image with the
    detected tags overlaid.

    objpts: Object corner points in world space
    imgpts: Detected tag corner points in the image
    img: The source image

    return: None
    """
    h,w = img.shape[:2]

    plt.subplot(121)
    markers = objpts.shape[0]//4
    pts = objpts
    for i in range(markers):
        x = np.hstack((pts[4*i:4*i+4,0], pts[4*i,0]))
        y = np.hstack((pts[4*i:4*i+4,1], pts[4*i,1]))
        plt.plot(x,y)
    plt.grid(True)
    plt.title("Object Points in World Space [meters]")
    # plt.axis("equal");
    plt.axis("square")

    plt.subplot(122)
    plt.scatter(imgpts[:,0],imgpts[:,1])
    markers = imgpts.shape[0]//4 # 4 corners
    pts = imgpts
    for i in range(markers):
        x = np.hstack((pts[4*i:4*i+4,0], pts[4*i,0]))
        y = np.hstack((pts[4*i:4*i+4,1], pts[4*i,1]))
        plt.plot(x,y)
    plt.grid(True)
    plt.title("Image Points in Image Space [pixels]")
    plt.imshow(img, cmap="gray");
