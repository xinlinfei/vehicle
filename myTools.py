import cv2
import numpy as np
from queue import Queue


# 做了正负90°的纠正
def GetCorrectNumpyArray(pointarr, center):
    # 如果没有旋转:
    if pointarr[0][1] == pointarr[1][1] or pointarr[0][0] == pointarr[2][0]:
        return pointarr
    # 发生了旋转
    index = [0, 1, 2, 3, 0, 1, 2]
    begin = 0
    result = []
    ymin = pointarr[0][1]
    for idx in range(len(pointarr)):
        if pointarr[idx][1] < ymin:
            ymin = pointarr[idx][1]
            begin = idx
    # 统计x比最高点小的点的个数
    count = 0
    for point in pointarr:
        if point[0] < pointarr[begin][0]:
            count += 1
    if count == 2:
        begin -= 1
        if begin == -1:
            begin = 3
    for idx in range(len(index)):
        if index[idx] == begin:
            for i in range(idx, idx + 4):
                result.append(pointarr[index[i]])
            break
    return result


def SplitImgForRecognize(img):
    # 1.先将图片分割为小块
    block_size = (10, 10)
    blocks = splitImg(img, block_size)
    row = blocks.shape[0]
    col = blocks.shape[1]
    blocks_count = row * col
    visted = np.zeros((row, col), dtype=bool)
    q = Queue()
    for i in range(row):
        for j in range(col):
            if visted[i, j] == False:
                h, s, v = getHSVAvg(blocks[i, j])
                if h > 11 and h <= 124:
                    visted[i, j] = True
                    q.put((i, j))
                    count = 1
                    while not q.empty():
                        sz = q.qsize()
                        while sz != 0:
                            sz -= 1
                            x, y = q.get()
                            if x - 1 >= 0 and visted[x - 1, y] == False:
                                h1, s1, v1 = getHSVAvg(blocks[x - 1, y])
                                if h1-h<6 and h1-h>-6:
                                    visted[x - 1, y] = True
                                    q.put((x - 1, y))
                                    count += 1
                            if x + 1 < row and visted[x + 1, y] == False:
                                h1, s1, v1 = getHSVAvg(blocks[x + 1, y])
                                if h1-h<6 and h1-h>-6:
                                    visted[x + 1, y] = True
                                    q.put((x + 1, y))
                                    count += 1
                            if y - 1 >= 0 and visted[x, y - 1] == False:
                                h1, s1, v1 = getHSVAvg(blocks[x, y - 1])
                                if h1-h<6 and h1-h>-6:
                                    visted[x, y - 1] = True
                                    q.put((x, y - 1))
                                    count += 1
                            if y + 1 < col and visted[x, y + 1] == False:
                                h1, s1, v1 = getHSVAvg(blocks[x, y + 1])
                                if h1-h<6 and h1-h>-6:
                                    visted[x, y + 1] = True
                                    q.put((x, y + 1))
                                    count += 1
                    if count >=blocks_count*0.5:
                        if 11<h<=34<s:
                            return True,"yellow"
                        elif 35<h<=99 and s>34:
                            return True,"green"
                        elif 99<h<=124 and s>34:
                            return True,"blue"
                else:
                    visted[i, j] = True
    return False,"none"


def splitImg(image, block_size):
    height, width = image.shape[:2]
    rows = height // block_size[0]
    cols = width // block_size[1]

    blocks = np.empty((rows, cols), dtype=object)
    for r in range(rows):
        for c in range(cols):
            block = image[r * block_size[0]:(r + 1) * block_size[0], c * block_size[1]:(c + 1) * block_size[1]]
            blocks[r, c] = block

    return blocks


def getHSVAvg(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    h_avg = np.average(h)
    s_avg = np.average(s)
    v_avg = np.average(v)
    return h_avg, s_avg, v_avg
