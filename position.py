import cv2
import numpy as np
from numpy.linalg import norm
import sys
import os
import json

SZ = 20          # 训练图片长宽
MAX_WIDTH = 1000 # 原始图片最大宽度
Min_Area = 2000  # 车牌区域允许最大面积
PROVINCE_START = 1000


def point_limit(point):
	if point[0] < 0:
		point[0] = 0
	if point[1] < 0:
		point[1] = 0

#找到符合指定颜色范围和亮度条件的有效区域的边界位置
def accurate_place(card_img_hsv, limit1, limit2, color,cfg):
	row_num, col_num = card_img_hsv.shape[:2]
	xl = col_num
	xr = 0
	yh = 0
	yl = row_num
	#col_num_limit = cfg["col_num_limit"]
	row_num_limit = cfg["row_num_limit"]
	col_num_limit = col_num * 0.8 if color != "green" else col_num * 0.5 # 绿色有渐变
	for i in range(row_num):
		count = 0
		for j in range(col_num):
			H = card_img_hsv.item(i, j, 0)
			S = card_img_hsv.item(i, j, 1)
			V = card_img_hsv.item(i, j, 2)
			if limit1 < H <= limit2 and 34 < S and 46 < V:
				count += 1
		if count > col_num_limit:
			if yl > i:
				yl = i
			if yh < i:
				yh = i
	for j in range(col_num):
		count = 0
		for i in range(row_num):
			H = card_img_hsv.item(i, j, 0)
			S = card_img_hsv.item(i, j, 1)
			V = card_img_hsv.item(i, j, 2)
			if limit1 < H <= limit2 and 34 < S and 46 < V:
				count += 1
		if count > row_num - row_num_limit:
			if xl > j:
				xl = j
			if xr < j:
				xr = j
	return xl, xr, yh, yl

def CaridDetect(car_pic):

	# 加载图片
	global cfg
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
	# 一一排除不是车牌的矩形区域，找到最小外接矩形的长宽比复合车牌条件的边缘检测到的物体
	car_contours = []
	for cnt in contours:
		rect = cv2.minAreaRect(cnt) 
		area_width, area_height = rect[1]
		if area_width < area_height:
			area_width, area_height = area_height, area_width
		wh_ratio = area_width / area_height
		#print(wh_ratio)
		# 要求矩形区域长宽比在2到5.5之间，2到5.5是车牌的长宽比，其余的矩形排除 一般的比例是3.5
		if wh_ratio > 2 and wh_ratio < 5.5:
			car_contours.append(rect)
			box = cv2.boxPoints(rect)
			box = np.intp(box)
			oldimg = cv2.drawContours(oldimg, [box], 0, (0, 0, 255), 2)
			cv2.imshow("edge4", oldimg)
			print(rect)
			cv2.waitKey(0)
	card_imgs = []

	# 矩形区域可能是倾斜的矩形，需要矫正，以便使用颜色定位更加精确
	for rect in car_contours:
		#rect：（最小外接矩形的中心（x，y），（宽度，高度），旋转角度）
		if rect[2] > -1 and rect[2] < 1:#创造角度，使得左高右低拿到正确的值
			angle = 1
		else:
			angle = rect[2]
		rect = (rect[0], (rect[1][0]+5, rect[1][1]+5), angle)#扩大rect范围，避免车牌边缘被排除 

		box = cv2.boxPoints(rect)
		# 避免边界超出图像边界
		heigth_point = right_point = [0, 0]
		left_point = low_point = [pic_width, pic_hight]
		for point in box:
			if left_point[0] > point[0]:
				left_point = point
			if low_point[1] > point[1]:
				low_point = point
			if heigth_point[1] < point[1]:
				heigth_point = point
			if right_point[0] < point[0]:
				right_point = point

		if left_point[1] <= right_point[1]: # 正角度
			new_right_point = [right_point[0], heigth_point[1]]
			pts2 = np.float32([left_point, heigth_point, new_right_point])#字符只是高度需要改变
			pts1 = np.float32([left_point, heigth_point, right_point])
			M = cv2.getAffineTransform(pts1, pts2) # 仿射变换
			dst = cv2.warpAffine(oldimg, M, (pic_width, pic_hight))
			point_limit(new_right_point)
			point_limit(heigth_point)
			point_limit(left_point)
			card_img = dst[int(left_point[1]):int(heigth_point[1]), int(left_point[0]):int(new_right_point[0])]
			card_imgs.append(card_img)
		elif left_point[1] > right_point[1]: # 负角度
			
			new_left_point = [left_point[0], heigth_point[1]]
			pts2 = np.float32([new_left_point, heigth_point, right_point])#字符只是高度需要改变
			pts1 = np.float32([left_point, heigth_point, right_point])
			M = cv2.getAffineTransform(pts1, pts2)
			dst = cv2.warpAffine(oldimg, M, (pic_width, pic_hight))
			point_limit(right_point)
			point_limit(heigth_point)
			point_limit(new_left_point)
			card_img = dst[int(right_point[1]):int(heigth_point[1]), int(new_left_point[0]):int(right_point[0])]
			card_imgs.append(card_img)
	# for carimg in card_imgs:
	# 	cv2.imshow("card", carimg)
	# 	cv2.waitKey(0)

	# 开始使用颜色定位，排除不是车牌的矩形，目前只识别蓝、绿、黄车牌
	colors = []
	roi = []
	card_color = []
	labels = []
	for card_index,card_img in enumerate(card_imgs):
		green = yello = blue = black = white = 0
		card_img_hsv = cv2.cvtColor(card_img, cv2.COLOR_BGR2HSV)
		#有转换失败的可能，原因来自于上面矫正矩形出错
		if card_img_hsv is None:
			continue
		row_num, col_num= card_img_hsv.shape[:2]
		card_img_count = row_num * col_num

		for i in range(row_num):
			for j in range(col_num):
				H = card_img_hsv.item(i, j, 0)
				S = card_img_hsv.item(i, j, 1)
				V = card_img_hsv.item(i, j, 2)
				if 11 < H <= 34 and S > 34:#图片分辨率调整
					yello += 1
				elif 35 < H <= 99 and S > 34:#图片分辨率调整
					green += 1
				elif 99 < H <= 124 and S > 34:#图片分辨率调整
					blue += 1
				
				if 0 < H <180 and 0 < S < 255 and 0 < V < 46:
					black += 1
				elif 0 < H <180 and 0 < S < 43 and 221 < V < 225:
					white += 1
		color = "no"

		limit1 = limit2 = 0
		if yello*2 >= card_img_count:
			color = "yello"
			limit1 = 11
			limit2 = 34#有的图片有色偏偏绿
		elif green*2 >= card_img_count:
			color = "green"
			limit1 = 35
			limit2 = 99
		elif blue*2 >= card_img_count:
			color = "blue"
			limit1 = 100
			limit2 = 124#有的图片有色偏偏紫
		elif black + white >= card_img_count*0.7: #TODO
			color = "bw"
		# print("[ INFO ] color: {}".format(color))
		colors.append(color)
		# print(blue, green, yello, black, white, card_img_count)
		#cv2.imshow("color", card_img)
		#cv2.waitKey(0)
		if limit1 == 0:
			continue
		#以上为确定车牌颜色

		#以下为根据车牌颜色再定位，缩小边缘非车牌边界
		xl, xr, yh, yl = accurate_place(card_img_hsv, limit1, limit2, color,cfg)
		if yl == yh and xl == xr:
			continue
		need_accurate = False
		if yl >= yh:
			yl = 0
			yh = row_num
			need_accurate = True
		if xl >= xr:
			xl = 0
			xr = col_num
			need_accurate = True
		card_imgs[card_index] = card_img[yl:yh, xl:xr] if color != "green" or yl < (yh-yl)//4 else card_img[yl-(yh-yl)//4:yh, xl:xr]
		if need_accurate:#可能x或y方向未缩小，需要再试一次
			card_img = card_imgs[card_index]
			card_img_hsv = cv2.cvtColor(card_img, cv2.COLOR_BGR2HSV)
			xl, xr, yh, yl = accurate_place(card_img_hsv, limit1, limit2, color,cfg)
			if yl == yh and xl == xr:
				continue
			if yl >= yh:
				yl = 0
				yh = row_num
			if xl >= xr:
				xl = 0
				xr = col_num
		card_imgs[card_index] = card_img[yl:yh, xl:xr] if color != "green" or yl < (yh-yl)//4 else card_img[yl-(yh-yl)//4:yh, xl:xr]


		roi.append(card_img)
		card_color.append(color)
		labels.append((int(right_point[1]), int(heigth_point[1]), int(left_point[0]), int(right_point[0])))

			
	return roi,labels, card_color#定位的车牌图像、车牌颜色

if __name__ == '__main__':
	roi, label, color = CaridDetect("2.jpg")
	# roi, label, color = CaridDetect("2.jpg")
	# roi, label,color = CaridDetect("green.jpg")
	# print(len(roi), len(label), len(color))
	# print(label[0])
	# cv2.imshow("roi", roi[0])
	# cv2.waitKey(0)