import paddleocr
import cv2
import test

imgs,_ = test.GetCarid_possible_by_color("dataset/2.jpg")
ocr = paddleocr.PaddleOCR(use_angle_cls=True, use_gpu=True, lang="ch")
for img in imgs:
    result = ocr.ocr(img, cls=True, det=False)
    for line in result:
        print(line)
    cv2.imshow("img", img)
    cv2.waitKey(0)