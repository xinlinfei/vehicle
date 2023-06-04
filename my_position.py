import cv2
import numpy as np
import json


SZ = 20          # 训练图片长宽
MAX_WIDTH = 1000 # 原始图片最大宽度
Min_Area = 2000  # 车牌区域允许最大面积
PROVINCE_START = 1000

def CaridDetect(car_pic):
	contours = CaridDetect_contours(car_pic)
	if contours:
		car_imgs_possible = CaridDetect_possible_img(contours, car_pic)
	else :
		return None
	if car_imgs_possible:
		return CaridDetect_color(car_imgs_possible)
	else :
		return None
	




# 找到符合车牌形状的矩形
def CaridDetect_contours(car_pic):
    # 加载图片
	img = cv2.imread(car_pic)
	pic_hight, pic_width = img.shape[:2]

	if pic_width > MAX_WIDTH:
		resize_rate = MAX_WIDTH / pic_width
		img = cv2.resize(img, (MAX_WIDTH, int(pic_hight*resize_rate)), interpolation=cv2.INTER_AREA)
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
		img = cv2.GaussianBlur(img, (blur, blur), 0) #图片分辨率调整
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
	return contours


# 从contours中找出符合车牌形状的矩形并矫正
def CaridDetect_possible_img(contours, car_pic):
	possible_img = []
	oldimg = cv2.imread(car_pic)	    
	return possible_img



#从可能的车牌中根据颜色进一步筛选，并得出最后的车牌图片并返回
def CaridDetect_color(car_imgs_possible):
    roi = []
    color = []
    return roi, color


if __name__ == "__main__" :
    roi, label, color = CaridDetect("2.jpg")
    if len(roi) > 0:
        for img in roi:
            cv2.imshow("roi", img)
            cv2.waitKey(0)