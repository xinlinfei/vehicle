import test
import paddleocr
import cv2


def detect(pic_img):
    imgs, colors = test.GetCaridBySplit(pic_img)
    carid = []
    ocr = paddleocr.PaddleOCR(use_angle_cls=True, use_gpu=True, lang="ch")
    for img in imgs:
        result = ocr.ocr(img, cls=True, det=False)
        for line in result:
            carid.append(line[1][0])
    return imgs, colors, carid


if __name__ == "__main__":
    imgs, colors, carid = detect("dataset/2.jpg")
    for i in range(len(imgs)):
        cv2.imshow(colors[i], imgs[i])
        cv2.waitKey(0)
        print(carid)
