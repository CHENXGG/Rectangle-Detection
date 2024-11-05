import math
import warnings
import cv2
import numpy as np

# 转换为角度
def convert_slope_to_angle(x):
    y = math.degrees(math.atan(x))
    return y

# 计算霍夫变换的结果直线的两点坐标，以确定一条直线
def calculate_coordinate(rho, theta):
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a * rho
    y0 = b * rho
    x1 = int(x0 + 1000 * (-b))
    y1 = int(y0 + 1000 * (a))
    x2 = int(x0 - 1000 * (-b))
    y2 = int(y0 - 1000 * (a))
    return x1, y1, x2, y2


# 已知(x1, y1)和(x2, y2)，计算直线的斜率k和截距b
def calculate_slope_and_intercept(x1, y1, x2, y2):
    k = (y2 - y1) / (x2 - x1 + 1)
    if k < -200:
        k = -200
    b = y1 - k * x1
    return k, b


# 已知一点(x1, y1)和一条直线的斜率k和截距b，求该点到直线的距离
def calculate_distance_to_line(x1, y1, k, b):
    d = abs(-k * x1 + y1 - b) / math.sqrt(k ** 2 + 1)
    return d


# 已知两条直线的斜率k和截距b，求交点
def find_intersection(k1, b1, k2, b2):
    # 检查斜率是否相等，如果相等，直线可能平行或重合
    if k1 == k2:
        if b1 == b2:
            return -1, -1
        else:
            return -1, -1
    x = (b2 - b1) / (k1 - k2)
    y = int(k1 * x + b1)
    x = int(x)

    return x, y

# 直线两两求交点
def find_all_intersections(img, line_list):
    height, width = img.shape[:2]
    intersections = []
    num_lines = len(line_list)
    # 直线两两求交
    for i in range(num_lines):
        for j in range(i + 1, num_lines):
            k1, b1 = line_list[i]
            k2, b2 = line_list[j]
            # 只对斜率差别很大的直线进行求交点
            if abs(convert_slope_to_angle(k1) - convert_slope_to_angle(k2)) >= 45:
                # 已知两条直线的斜率k和截距b，求交点
                x, y = find_intersection(k1, b1, k2, b2)
                # 记录在图片坐标范围内的点
                if 0 <= x <= width-1 and 0<= y <= height -1:
                    intersections.append((x, y))
    return intersections


# 给定斜率k和截距b, 在图片中画直线
def drawline(image, k, b):
    # 获取图像的尺寸
    height, width = image.shape[:2]

    # 计算直线与图像边缘的交点
    # 直线方程：y = kx + b
    # 与顶部和底部边缘的交点（x = 0 和 x = width - 1）
    x1, x2 = 0, width-1
    y1 = int(k * x1 + b)
    y2 = int(k * x2 + b)

    if y1 >= height:
        y1 = height - 1
        x1 = int((y1 - b)/k)
    elif y1 < 0 :
        y1 = 0
        x1 = int((y1 - b)/k)

    if y2 >= height:
        y2 = height - 1
        x2 = int((y2 - b)/k)
    elif y2 < 0 :
        y2 = 1
        x2 = int((y2 - b)/k)

    cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2)


# 检测直线，并给出定位点
# 返回值：img_lines：画线后的图片
#       img_intersection：画定位点后的图片
#       intersections：定位点
def dect_line(img_org, img_edge, threshold=20, threshold_k=45):
    img_lines = img_org.copy()
    img_intersection = img_org.copy()
    intersections = []

    # 霍夫变化
    lines = cv2.HoughLines(img_edge, 1, np.pi / 180, 200, 200, 5)

    # 记录直线信息: (斜率，截距)
    line_list = []
    # 遍历霍夫变换得到的直线
    for line in lines:
        rho = line[0][0]
        theta = line[0][1]
        # 计算直线中两点的坐标
        x1, y1, x2, y2 = calculate_coordinate(rho, theta)
        # 计算这条直线的斜率
        k_now, b_now = calculate_slope_and_intercept(x1, y1, x2, y2)
        # 将斜率转化回角度
        angle_of_k_now = convert_slope_to_angle(k_now)

        if len(line_list) == 0:  # 第一条直线直接加入
            line_list.append((k_now, b_now))
        else:  # 后续直线进行判断
            add_flag = 1
            # 对已经选取的直线进行遍历
            for i, (k, b) in enumerate(line_list):
                # 将斜率转化回角度
                angle_of_k = convert_slope_to_angle(k)
                # 如果有角度相近的直线，就进行距离比较
                if abs(angle_of_k_now - angle_of_k) <= threshold_k:
                    # 寻找同方向的线中是否有相似位置的线
                    d1 = calculate_distance_to_line(x1, y1, k, b)
                    d2 = calculate_distance_to_line(x2, y2, k, b)
                    if d1 < threshold or d2 < threshold:
                        add_flag = 0
            # 如果现有信息中，不存在相似的直线
            if add_flag:
                line_list.append((k_now, b_now))

        # 在图片中标定直线
        for (k, b) in line_list:
            drawline(img_lines, k, b)

        # 寻找直线的交点
        intersections = find_all_intersections(img_org, line_list)

        # 在图片中标定交点
        for x, y in intersections:
            cv2.circle(img_intersection, (x, y), radius=5, color=(0, 0, 255), thickness=-1)

    return img_lines, img_intersection, intersections


def get_hough_res(img_org, img_edge):
    imgLines = img_org.copy()
    lines = cv2.HoughLines(img_edge, 1, np.pi / 180, 200, 300, 5)

    for line in lines:
        rho = line[0][0]
        theta = line[0][1]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))

        cv2.line(imgLines, (x1, y1), (x2, y2), (0, 0, 255), 2)

    return imgLines