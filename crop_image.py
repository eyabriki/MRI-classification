import pandas as pd
import numpy as np
import cv2
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import tensorflow as tf
import imutils
import dataset

def crop_image(img):
    # Resize the image to 256x256 pixels
    resized_img = cv2.resize(
        img,
        dsize=(256, 256),
        interpolation=cv2.INTER_CUBIC
    )
    # Convert the image to grayscale
    gray = cv2.cvtColor(resized_img, cv2.COLOR_RGB2GRAY)

    # Apply a Gaussian blur to the image
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Threshold the image by Binary Thresholding
    thresh = cv2.threshold(gray, 45, 255, cv2.THRESH_BINARY)[1]
    
    # perform a series of erosions & dilations to remove any small regions of noise
    thresh = cv2.erode(thresh, None, iterations=2)
    thresh = cv2.dilate(thresh, None, iterations=2)
    # find contours in thresholded image, then grab the largest one
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    c = max(cnts, key=cv2.contourArea)

    # find the extreme points
    extLeft = tuple(c[c[:, :, 0].argmin()][0])
    extRight = tuple(c[c[:, :, 0].argmax()][0])
    extTop = tuple(c[c[:, :, 1].argmin()][0])
    extBot = tuple(c[c[:, :, 1].argmax()][0])

    # crop
    ADD_PIXELS = 0
    cropped_img = resized_img[extTop[1]-ADD_PIXELS:extBot[1]+ADD_PIXELS,
                              extLeft[0]-ADD_PIXELS:extRight[0]+ADD_PIXELS].copy()
    return cropped_img
