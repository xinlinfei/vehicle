import os

import detect
import paddleocr
import cv2


def detect(pic_img):
    imgs, _ = test.GetCaridBySplit(pic_img)
    carid = []
    ocr = paddleocr.PaddleOCR(use_angle_cls=True, use_gpu=True, lang="ch")
    for img in imgs:
        result = ocr.ocr(img, cls=True, det=False)
        for line in result:
            carid.append(line[0][0])
    return carid[0]