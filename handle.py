import os

import cv2
import numpy as np
import json
import myTools

MAX_WIDTH = 1000  # 原始图片最大宽度
Min_Area = 2000  # 车牌区域允许最大面积

COLORMAP = {
    "blue": (255, 0, 0),
    "yellow": (0, 255, 255),
    "green": (0, 255, 0),
}


def GetCaridImg(car_pic):
    return GetCaridPossibleByColor(car_pic)


def GetCaridPossible(car_pic):  # 1.矩形区域，2.长宽比
    # 加载图片
    global cfg
    img = cv2.imread(car_pic)
    pic_hight, pic_width = img.shape[:2]

    if pic_width > MAX_WIDTH:
        resize_rate = MAX_WIDTH / pic_width
        img = cv2.resize(img, (MAX_WIDTH, int(pic_hight * resize_rate)), interpolation=cv2.INTER_AREA)
    # 车牌识别的部分参数保存在js中，便于根据图片分辨率做调整
    f = open('config.js')
    j = json.load(f)
    for c in j["config"]:
        if c["open"]:
            cfg = c.copy()
            break
        else:
            raise RuntimeError('[ ERROR ] 没有设置有效配置参数.')

    blur = cfg["blur"]
    # 高斯去噪
    if blur > 0:
        img = cv2.GaussianBlur(img, (blur, blur), 0)  # 图片分辨率调整
    oldimg = img
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 去掉图像中不会是车牌的区域
    kernel = np.ones((20, 20), np.uint8)
    # morphologyEx 形态学变化函数
    img_opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    img_opening = cv2.addWeighted(img, 1, img_opening, -1, 0);

    # 找到图像边缘 Canny边缘检测
    ret, img_thresh = cv2.threshold(img_opening, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    img_edge = cv2.Canny(img_thresh, 100, 200)

    # 使用开运算和闭运算让图像边缘成为一个整体
    kernel = np.ones((cfg["morphologyr"], cfg["morphologyc"]), np.uint8)
    img_edge1 = cv2.morphologyEx(img_edge, cv2.MORPH_CLOSE, kernel)
    img_edge2 = cv2.morphologyEx(img_edge1, cv2.MORPH_OPEN, kernel)
    # 查找图像边缘整体形成的矩形区域，可能有很多，车牌就在其中一个矩形区域中
    # cv2.findContours()函数来查找检测物体的轮廓
    try:
        contours, hierarchy = cv2.findContours(img_edge2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    except ValueError:
        image, contours, hierarchy = cv2.findContours(img_edge2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = [cnt for cnt in contours if cv2.contourArea(cnt) > Min_Area]

    # 一一排除不是车牌的矩形区域，找到最小外接矩形的长宽比复合车牌条件的边缘检测到的物体
    car_imgs_possibly = []
    for cnt in contours:
        rect = cv2.minAreaRect(cnt)
        area_width, area_height = rect[1]
        if area_width < area_height:
            area_width, area_height = area_height, area_width
        wh_ratio = area_width / area_height
        # 要求矩形区域长宽比在2到5.5之间，2到5.5是车牌的长宽比，其余的矩形排除 一般的比例是3.5
        # 后面发现，由于车牌上下边缘有横向的凹槽，因此车牌的长宽比会变大，所以这里的上限定为6
        if wh_ratio > 2 and wh_ratio < 6:
            rect_points = cv2.boxPoints(rect)
            # 做了正负90°的纠正
            rect_points = myTools.GetCorrectNumpyArray(rect_points)
            rect_points = np.float32(rect_points)
            target_points = np.float32([[0, 0], [area_width, 0], [area_width, area_height], [0, area_height]])
            M = cv2.getPerspectiveTransform(rect_points, target_points)
            car_img = cv2.warpPerspective(oldimg, M, (int(area_width), int(area_height)))
            car_imgs_possibly.append(car_img)
    return car_imgs_possibly


def GetCaridPossibleByColor(car_pic):
    car_imgs_possibly = GetCaridPossible(car_pic)
    card_imgs = []
    colors = []
    for card_index, card_img in enumerate(car_imgs_possibly):
        green = yello = blue = 0
        card_img_hsv = cv2.cvtColor(card_img, cv2.COLOR_BGR2HSV)
        # 有转换失败的可能，原因来自于上面矫正矩形出错
        if card_img_hsv is None:
            continue
        row_num, col_num = card_img_hsv.shape[:2]
        card_img_count = row_num * col_num
        for i in range(row_num):
            for j in range(col_num):
                H = card_img_hsv.item(i, j, 0)
                S = card_img_hsv.item(i, j, 1)
                V = card_img_hsv.item(i, j, 2)
                if 11 < H <= 34 < S:
                    yello += 1
                elif 35 < H <= 99 and S > 34:
                    green += 1
                elif 99 < H <= 124 and S > 34:
                    blue += 1
        color = "no"
        if yello * 2.5 >= card_img_count:
            color = "yellow"
        elif green * 2.5 >= card_img_count:
            color = "green"
        elif blue * 2.5 >= card_img_count:
            color = "blue"
        else:
            continue
        colors.append(color)
        card_imgs.append(card_img)
    return card_imgs, colors


def GetCaridBySplit(car_pic):
    card_imgs_possible = GetCaridPossible(car_pic)
    card_imgs = []
    colors = []
    for card_img in card_imgs_possible:
        iscardid, color = myTools.SplitImgForRecognize(card_img)
        if iscardid:
            card_imgs.append(card_img)
            colors.append(color)
    return card_imgs, colors


if __name__ == "__main__":
    count=1
    for path in os.listdir("dataset"):
        path = os.path.join("dataset", path)
        # imgs, colors = GetCarid_possible_by_color(path)
        imgs, colors = GetCaridBySplit(path)
        if imgs:
            for index in range(len(imgs)):
                print("color:", colors[index], path, count)
                cv2.imshow("img", imgs[index])
                cv2.waitKey(0)
        else:
            print("no car id in this pic", path,count)
        count+=1
