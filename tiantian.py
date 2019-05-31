# -*- coding: utf-8 -*-
from selenium import webdriver
import requests
import time
from selenium.webdriver.common.action_chains import ActionChains
import re
from PIL import Image
import io
# import cv2
# import numpy as np

# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')


def get_img(div_list):
    position_list = []
    for div in div_list:
        style = div.get_attribute('style')
        position_tuple = re.search(r'background-position:\s+-?(\d+)px\s-?(\d+)px', style).groups(1)
        position_list.append((int(position_tuple[0]), int(position_tuple[1])))
    style = div_list[0].get_attribute('style')
    img_url = re.search(r'url\(\"(.*?)\"\);', style).group(1)
    return position_list, img_url


def restore_img(img_data, position_list):
    img = Image.open(io.BytesIO(img_data))
    new_img = Image.new('RGB', (260, 116))
    i = 0
    j = 0
    for position in position_list:
        if position[1] == 58:
            region = img.crop((position[0], 58, position[0] + 10, 58 + 58))
            new_img.paste(region, (i, 0, i + 10, 58))
            i += 10
        else:
            region = img.crop((position[0], 0, position[0] + 10, 58))
            new_img.paste(region, (j, 58, j + 10, 58 + 58))
            j += 10
    return new_img


# 第一种方法是遍历带缺口的和不带缺口的两张图片的所有像素点寻找不同之处
def get_move_location(full_img, cut_img):
    for i in range(260):
        for j in range(116):
            full_pixel = full_img.getpixel((i, j))
            cut_pixel = cut_img.getpixel((i, j))
            for index in range(3):
                if abs(full_pixel[index] - cut_pixel[index]) >= 50:
                    return i - 5


# 第二种方法是使用OpenCV寻找滑块图片在带缺口的图片中的位置
# def get_move_location2(filename1, filename2):
#     target = cv2.imread(filename1)
#     template = cv2.imread(filename2)
#     temp = 'temp.jpg'
#     targ = 'targ.jpg'
#     cv2.imwrite(temp, template)
#     cv2.imwrite(targ, target)
#     target = cv2.imread(targ)
#     target = abs(255 - target)
#     cv2.imwrite(targ, target)
#     target = cv2.imread(targ)
#     template = cv2.imread(temp)
#     result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
#     x, y = np.unravel_index(result.argmax(), result.shape)
#     return y

# 模拟人手的滑动轨迹
def get_tracks(distance):
    v = 0
    t = 0.3
    tracks = []
    current = 0
    mid = distance * 5 / 6

    while current < distance:
        if current < mid:
            a = 2
        else:
            a = -3
        v0 = v
        s = v0 * t + 0.5 * a * (t ** 2)
        current += s
        tracks.append(round(s))
        v = v0 + a * t
    if current > distance:
        tracks.append(distance - current)
    return tracks


def move(location):
    element = driver.find_element_by_xpath('//div[@class="gt_slider_knob gt_show"]')
    ActionChains(driver).click_and_hold(element).perform()
    tracks = get_tracks(location)
    for track in tracks:
        ActionChains(driver).move_by_offset(track, 0).perform()
    time.sleep(0.8)
    ActionChains(driver).release(element).perform()

if __name__ == "__main__":
    # driver = webdriver.Chrome(r"C:\Users\97193\AppData\Local\Google\Chrome\Application\chromedriver.exe")
    # driver = webdriver.Chrome(r"F:\python_program\pachong_slide_verification\chromedriver.exe")

    options = webdriver.ChromeOptions()
    options.add_argument('lang=zh_CN.UTF-8')
    options.add_argument('user-agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"')

    driver = webdriver.Chrome(chrome_options=options, executable_path=r"F:\python_program\pachong_slide_verification\chromedriver.exe")

    time.sleep(1)
    driver.get('http://tiantian08.com/member.php?mod=register')

    time.sleep(1)
    distance = driver.find_element_by_xpath('.//div[@id="conqu3r_oc_page_register_input"]').location['x'] + 10
    print("滑块偏移量:{}px".format(distance))

    time.sleep(100)
    element = driver.find_element_by_xpath('.//span[@class="nc_iconfont btn_slide"]')
    ActionChains(driver).click_and_hold(element).perform()
    tracks = get_tracks(distance)
    for track in tracks:
        ActionChains(driver).move_by_offset(track, 0).perform()
    time.sleep(0.8)
    ActionChains(driver).release(element).perform()

    # time.sleep(1)
    # full_img_div_list = driver.find_elements_by_class_name('gt_cut_fullbg_slice')
    # cut_img_div_list = driver.find_elements_by_class_name('gt_cut_bg_slice')
    # full_img_position_list, full_img_url = get_img(full_img_div_list)
    # print(full_img_url)
    # cut_bg_img_position_list, cut_bg_img_url = get_img(cut_img_div_list)
    # print(cut_bg_img_url)
    # full_img = restore_img(requests.get(full_img_url).content, full_img_position_list)
    # cut_bg_img = restore_img(requests.get(cut_bg_img_url).content, cut_bg_img_position_list)
    # x = get_move_location(full_img, cut_bg_img)

    # cut_style = driver.find_element_by_xpath('//div[@class="gt_slice gt_show"]').get_attribute('style')
    # cut_url = re.search(r'url\(\"(.*?)\"\);', cut_style).group(1)
    # cut = Image.open(io.BytesIO(requests.get(cut_url).content))
    # cut = cut.convert('L')
    # cut_bg = cut_bg_img.convert('L')
    # cut.save("cut.png")
    # cut_bg.save("cut_bg.png")
    # x = get_move_location2("cut.png", "cut_bg.png")
    # print("滑块偏移量:{}px".format(x))
    # # print(location)
    # move(x)
    # time.sleep(5)
    driver.quit()
