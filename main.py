import handle
import paddleocr
import window

def detect(pic_img):
    imgs, colors = handle.GetCaridBySplit(pic_img)
    carid = []
    ocr = paddleocr.PaddleOCR(use_angle_cls=True, use_gpu=True, lang="ch")
    for img in imgs:
        result = ocr.ocr(img, cls=True, det=False)
        for line in result:
            carid.append(line[0][0])
    if len(carid) == 0:
        return "未检测到车牌，请重新拍摄","none"
    return carid[0],colors[0]

if __name__ =="__main__":
        window.create_picturegui()