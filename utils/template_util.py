import json
import os
import time
from logger import log
import cv2

from utils.cvmatch import image_match_util


class TemplateUtil:

    def __init__(self):
        self.cfgs = None
        self.img_map = None
        pass

    def load_template(self, name):
        parent_directory = os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir, os.pardir))
        with open(f'{parent_directory}/template/{name}/cfg.json', 'r', encoding='utf-8') as file:
            self.cfgs = json.load(file)
        img_names = list(
            filter(lambda x: x.endswith('.png') or x.endswith('.jpg'), os.listdir(f'{parent_directory}/template/{name}')))
        self.img_map = {item: cv2.imread(f'{parent_directory}/template/{name}/{item}') for item in img_names}
        return self

    def find_template(self, name, screen, confi=0.7):
        """
        获取模板的中心坐标
        :param name:
        :param screen:
        :param confi:
        :return: 坐标点
        """
        try:
            if screen is None:
                log.logger.info('未获取到屏幕')
                return None
            self.load_template(name)
            if isinstance(self.cfgs, list):
                log.logger.info('模板配置不支持次方法')
                return None
            # 识别区域
            crop = self.cfgs['rect']
            img_name = self.cfgs['img_name']
            img = self.img_map[img_name]
            room = tuple(self.cfgs['name'])
            res = image_match_util.cvmatch_template_best(img, screen,room, crop)
            if res is not None:
                # 取可信度最高的匹配结果
                if res['confidence'] > confi:
                    x, y, w, h = res['rect']
                    return x + w / 2, y + h / 2
            return None
        except Exception as e:
            log.logger.info(f'查找模版{name}出现异常。{e}')
            return None
