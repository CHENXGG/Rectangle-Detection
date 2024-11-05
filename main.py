import cv2
import os
from utils.dect_line import dect_line, get_hough_res

def main_worker(orignal_img_path):
    img_name = orignal_img_path.split('\\')[-1]
    # 创建保存路径
    overview_root = os.path.join('output_dir', f'orig_imag_{img_name}')

    if not os.path.exists(overview_root):
        os.makedirs(overview_root, exist_ok=False)

    # 载入图片
    orignal_img = cv2.imread(orignal_img_path)
    cv2.imwrite(os.path.join(overview_root, 'Original image.jpg'), orignal_img)

    # 预处理
    imgGray = cv2.cvtColor(orignal_img, cv2.COLOR_RGB2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
    imgCanny = cv2.Canny(imgBlur, 60, 60)

    # 霍夫变换
    imgHough = get_hough_res(orignal_img, imgCanny)

    # 得到四边形检测的结果
    line_min_distance = 20
    img_lines, img_intersection, intersection = dect_line(orignal_img, imgCanny, threshold=line_min_distance, threshold_k=45)

    # 显示
    # cv2.imshow('Orignal Image.jpg', orignal_img)
    # cv2.imshow('Edge detection results.jpg', imgCanny)
    # cv2.imshow('Hough results.jpg', imgHough)
    # cv2.imshow('Line positioning results.jpg', img_lines)
    # cv2.imshow('Positioning point results.jpg', img_intersection)
    # cv2.waitKey(0)

    # 保存结果
    cv2.imwrite(os.path.join(overview_root, 'Original image.jpg'), orignal_img)
    cv2.imwrite(os.path.join(overview_root, 'Orignal Image.jpg'), orignal_img)
    cv2.imwrite(os.path.join(overview_root, 'Edge detection results.jpg'), imgCanny)
    cv2.imwrite(os.path.join(overview_root, 'Hough results.jpg'), imgHough)
    cv2.imwrite(os.path.join(overview_root, 'Line positioning results.jpg'), img_lines)
    cv2.imwrite(os.path.join(overview_root, 'Positioning point results.jpg'), img_intersection)


def main():
    root_source_img_dir = 'source_img'

    for root, dirs, files in os.walk(root_source_img_dir):
        img_num = len(files)
        for i, file in enumerate(files):
            print(f"{i+1}/{img_num}, processing: {file}")
            orignal_img_path = os.path.join(root_source_img_dir, file)
            main_worker(orignal_img_path)


if __name__ == "__main__":
    main()
