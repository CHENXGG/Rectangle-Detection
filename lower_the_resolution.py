import cv2
import os

def main_worker(img_name, root_source_img, root_source_img_low_resoluation, scale_percent = 70):
    root_source_img_path = os.path.join(root_source_img, img_name)
    root_source_img_low_resoluation_path = os.path.join(root_source_img_low_resoluation, img_name)
    image = cv2.imread(root_source_img_path)

    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)

    # 调整分辨率
    resized_image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

    # 保存图片
    cv2.imwrite(root_source_img_low_resoluation_path, resized_image)


def main():
    scale_percent = 40
    root_source_img = 'source_img'
    root_source_img_low_resoluation = 'source_img_low_resolution'
    if not os.path.exists(root_source_img_low_resoluation):
        os.makedirs(root_source_img_low_resoluation, exist_ok=False)
    for root, dirs, files in os.walk(root_source_img):
        img_num = len(files)
        for i, file in enumerate(files):
            print(f"{i + 1}/{img_num}, processing: {file}")
            main_worker(file, root_source_img, root_source_img_low_resoluation, scale_percent=scale_percent)

if __name__ == '__main__':
    main()