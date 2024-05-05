# -*- coding:utf-8 -*-
# author:jackwu
# time:2022/6/1
# description: 背景图还原 & 获取滑动距离 & 轨迹数组 & 滑动时间
import os
import sys
import requests
import time
import random
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_PATH)
from urllib.request import urlretrieve
from PIL import Image


class GetTrackInfo(object):
    def __init__(self):
        self.challenge = ""
        self.gt = ""

    def get_gt_challenge(self):
        """获取gt,challenge"""
        url = f"https://www.geetest.com/demo/gt/register-slide?t{self.get_timestamp()}"
        resp = requests.get(url).json()
        self.challenge = resp["challenge"]
        self.gt = resp["gt"]

    def get_image_data(self):
        """获取完整背景图&缺口图片,测试直接写死"""
        img_list = [
            "https://static.geetest.com/pictures/gt/09b7341fb/bg/82baf5d7d.jpg",   # 含缺口图 bg
            "https://static.geetest.com/pictures/gt/09b7341fb/09b7341fb.jpg"       # 完整背景图 fullbg
        ]
        for index, url in enumerate(img_list):
            img_name = "bg" if index == 0 else "fullbg"
            urlretrieve(url, f'{img_name}.png')

    def image_reduction(self):
        """
        ****** 乱序图片还原 ******
        Image.new(mode, size, color=0)
        mode:模式，通常用"RGB"这种模式，如果需要采用其他格式，可以参考博文：PIL的mode参数
        size：生成的图像大小
        color：生成图像的颜色，默认为0，即黑色。
        """
        img_path_list = ["bg.png", "fullbg.png"]
        for index, img in enumerate(img_path_list):
            image = Image.open(img)
            standard_img = Image.new("RGBA", (260, 160))  # 创建一个空画布
            position = [39, 38, 48, 49, 41, 40, 46, 47, 35, 34, 50, 51, 33, 32, 28, 29, 27, 26, 36, 37, 31, 30, 44, 45, 43, 42, 12, 13, 23, 22, 14, 15, 21, 20, 8, 9, 25, 24, 6, 7, 3, 2, 0, 1, 11, 10, 4, 5, 19, 18, 16, 17]
            s = 80
            for c in range(52):
                a = position[c] % 26 * 12 + 1
                b = s if position[c] > 25 else 0
                im = image.crop(box=(a, b, a + 10, b + 80))  # box参数分别代表：左上角x,y 坐标；右下角x,y坐标
                standard_img.paste(im, box=(c % 26 * 10, 80 if c > 25 else 0))  # 将im 贴到standard_img 指定坐标位置
                """
                standard_img.paste(im, box=None, mask=None)  // 图像粘贴在原图像上，box参数：左上角 x y
                """
            standard_img.save(f"img{index}.png")

    def get_track_info(self, threshold=60):
        """
        1. 获取滑动距离，返回滑动时间 & 轨迹大数组;
        2. 比较两张图片的像素点RGB的绝对值是否小于阈值60,如果在阈值内则相同,反之不同
        """
        pic_path = "img0.png"
        cut_pic_path = "img1.png"
        pic_img = Image.open(pic_path)
        cut_img = Image.open(cut_pic_path)
        width, height = pic_img.size
        for x in range(40, width - 40):  # 从左往右
            for y in range(5, height - 10):  # 从上往下
                pixel1 = pic_img.load()[x, y]
                pixel2 = cut_img.load()[x, y]
                if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(pixel1[2] - pixel2[2]) < threshold:
                    continue
                else:
                    return x

    def get_slide_track(self, distance):
        """
        根据滑动距离生成滑动轨迹
        :param distance: 需要滑动的距离
        :return: 滑动轨迹<type 'list'>: [[x,y,t], ...]
            x: 已滑动的横向距离
            y: 已滑动的纵向距离, 除起点外, 均为0
            t: 滑动过程消耗的时间, 单位: 毫秒
        """

        if not isinstance(distance, int) or distance < 0:
            raise ValueError(f"distance类型必须是大于等于0的整数: distance: {distance}, type: {type(distance)}")
        # 初始化轨迹列表
        slide_track = [
            [random.randint(-50, -10), random.randint(-50, -10), 0],
            [0, 0, 0],
        ]
        # 共记录count次滑块位置信息
        count = 30 + int(distance / 2)
        # 初始化滑动时间
        t = random.randint(50, 100)
        # 记录上一次滑动的距离
        _x = 0
        _y = 0
        for i in range(count):
            # 已滑动的横向距离
            x = round(self.__ease_out_expo(i / count) * distance)
            # 滑动过程消耗的时间
            t += random.randint(10, 20)
            if x == _x:
                continue
            slide_track.append([x, _y, t])
            _x = x
        slide_track.append(slide_track[-1])
        return slide_track, slide_track[-1][2]   # 大数组，滑动时间

    def __ease_out_expo(self, sep):
        if sep == 1:
            return 1
        else:
            return 1 - pow(2, -10 * sep)

    @staticmethod
    def get_timestamp():
        """获取毫秒级的时间戳"""
        t = time.time()
        return str(round(t * 1000))

    def main(self):
        self.get_gt_challenge()
        self.get_image_data()
        self.image_reduction()
        distance = self.get_track_info()
        track_array, passtime = self.get_slide_track(distance)
        print(distance,)
        print(track_array)
        print(passtime)


if __name__ == '__main__':
    s = GetTrackInfo()
    s.main()

