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