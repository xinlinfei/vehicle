import os

import handle
import paddleocr
import cv2


def detect(pic_img):
    imgs, _ = handle.GetCaridBySplit(pic_img)
    carid = []
    ocr = paddleocr.PaddleOCR(use_angle_cls=True, use_gpu=True, lang="ch")
    for img in imgs:
        result = ocr.ocr(img, cls=True, det=False)
        for line in result:
            carid.append(line[0][0])
    if len(carid) == 0:
        return "未检测到车牌，请重新拍摄"
    return carid[0]