import json
import os
import typing

import cv2
from logger import log
from ncnn.utils.objects import Rect
from torch import Size
from typing import Tuple

from utils.cvmatch import image_match_util
from utils.template_util import TemplateUtil

# 走的房间路线顺序路线图,第几行第几列
room_route = [
    (1, 0),
    (2, 0),
    (2, 1),
    (2, 2),
    (1, 2),
    (1, 1),
    (1, 2),
    (1, 3),
    (1, 4),
    (1, 5)
]
log.logger.info(f"布万加刷图的路线图:{room_route}")
all_room = [
    (1, 0),
    (2, 0),
    (2, 1),
    (2, 2),
    (1, 2),
    (1, 1),
    (1, 2),
    (1, 3),
    (1, 4),
    (1, 5)
]

# 获取屏幕每帧的缩放比例
zoom_ratio = 1


def rect_slice_index(rect: Rect, size: Size, point: tuple) -> Tuple[int, int]:
    """
    矩形（范围)，切片索引
    ：param rect：范围
    ：param size： 切片大小 x 方块数量 y 轴方块数量
    ：param point：要索引的坐标
    : return: 如 (4, 1) 则表示目标在切片索引的第 4 行，第 1 列
    """
    x1, y1, x2, y2 = rect.x, rect.y, rect.x + rect.w, rect.y + rect.h
    width = rect.w / size[0]
    height = rect.h / size[1]
    rects = [
        [(x1 + i * width, y1 + j * height, x1 + (i + 1) * width, y1 + (j + 1) * height) for i in range(size[0])] for
        j in range(size[1])]
    # log.logger.info(f"所有方块对应的坐标范围:{rects}")
    for i, row in enumerate(rects):
        for j, rect in enumerate(row):
            x1, y1, x2, y2 = rect
            if x1 <= point[0] < x2 and y1 <= point[1] < y2:
                return i, j


def get_cur_room_index(point):
    """
    获取房间索引
    ：param point：要索引的坐标
    : return: 如 (4, 1) 则表示目标在切片索引的第 4 行，第 1 列
    """
    # 锁定获取的范围和每个房间方块的大小
    # Rect从投屏画面中获取区域左上角x,y和w，h
    # xy = rect_slice_index(Rect(504, 225, 376, 187), Size((6, 3)), point)
    # xy = rect_slice_index(Rect(1000, 436, 715, 351), Size((6, 3)), point)
    xy = rect_slice_index(Rect(818, 404, 689, 308), Size((6, 3)), point)
    # 遍历room_route
    cur_ind = None

    for ind,room in enumerate(room_route):
        if xy == room_route[ind]:
            cur_ind = ind
            break
    log.logger.info(f"当前房间索引:{cur_ind},房间行列号：{xy}")
    return cur_ind,xy


def get_recent_room(cur_room):
    next_room_1 = (cur_room[0],cur_room[1] + 1)
    next_room_2 = (cur_room[0] + 1,cur_room[1])
    next_room_3 = (cur_room[0],cur_room[1] - 1)
    next_room_4 = (cur_room[0] - 1,cur_room[1])
    for ind,room in enumerate(room_route):
        if next_room_1 == room or next_room_2 == room or next_room_3 == room or next_room_4 == room:
            return room
    log.logger.info("从预设的路线中，没有找到下一个房间")
    for ind,room in enumerate(all_room):
        if next_room_1 == room or next_room_2 == room or next_room_3 == room or next_room_4 == room:
            return room


def get_next_room(cur_room, is_succ_sztroom: bool = False):
    # ind,cur_room = get_cur_room_index(point)
    if cur_room == (1, 2):
        log.logger.info('进入狮子头前一房间')
    ind = None
    for i, room in enumerate(room_route):
        if cur_room == room_route[i]:
            ind = i
            break
    if is_succ_sztroom and ind == 4:
        ind = 6

    if ind is None:
        log.logger.info("从预设的路线中，没有找到下一个房间")
        # 错误房间就三个，分别枚举算了
        if cur_room == (0, 0):
            return None, (1,0)
        if cur_room == (0, 1):
            return None, (0, 2)
        if cur_room == (0, 2):
            return None, (1, 2)
        return None, None
    # 狮子头房间刷过了，不用去了
    if is_succ_sztroom and cur_room == (1, 2):
        log.logger.info("狮子头刷过了，不用去了")
        return 7, (1, 3)
    # 狮子头房间=5,(1,1) 没有刷，但是不小心进去下一个了,往回走
    if not is_succ_sztroom and ind > 5:
        nex_room = room_route[ind-1]
        return ind-1, nex_room

    # vals转换成连表的形式，用于获取下一个
    if cur_room in room_route:
        try:
            index = room_route.index(cur_room,ind)
        except ValueError:
            index = all_room.index(cur_room,0)

        if index >= len(room_route) - 1:
            log.logger.warn(f'【警告】返回none')
            # return None,None
            #先返回第一个房间，测试
            return None,(0,1)
        next_room = room_route[index + 1]
        return index + 1, next_room

def get_next_room2(cur_room, is_succ_sztroom: bool = False):
    # ind,cur_room = get_cur_room_index(point)
    if cur_room == (1, 2):
        log.logger.info('进入狮子头前一房间')

    # 狮子头房间刷过了，不用去了
    if is_succ_sztroom and cur_room == (1, 2):
        log.logger.info("狮子头刷过了，不用去了")
        return 7, (1, 3)

    # vals转换成连表的形式，用于获取下一个
    if cur_room in room_route:
        try:
            index = room_route.index(cur_room)
        except ValueError:
            index = all_room.index(cur_room,0)
        if index >= len(room_route) - 1:
            log.logger.warn(f'【警告】返回none')
            # return None,None
            #先返回第一个房间，测试
            return None,(0,1)
        next_room = room_route[index + 1]
        return index + 1, next_room
    else:
        # 错误房间就三个，分别枚举算了
        if cur_room == (0, 0):
            return None, (1, 0)
        if cur_room == (0, 1):
            return None, (0, 2)
        if cur_room == (0, 2):
            return None, (1, 2)
        return None, (1,0)


def get_run_direction(cur_room,next_room):
    # (1,0)-(2,0) 走下
    # 计算行走的方向
    if cur_room[0] == next_room[0]:
        if cur_room[1] > next_room[1]:
            return 'left'
        else:
            return 'right'
    else:
        if cur_room[0] > next_room[0]:
            return 'up'
        else:
            return 'down'

def determine_direction(hx, hy, ax, ay):
    """
    计算目标对象 (ax, ay) 相对于 hero (hx, hy) 的方向。

    参数:
    - hx, hy: hero 对象的底部坐标。
    - ax, ay: 目标对象的底部坐标。

    返回:
    - 'left', 'right', 'up', 'down' 其中之一，表示目标相对于 hero 的方向。
    """
    if ax < hx:  # 目标在 hero 的左侧
        return 'left'
    elif ax > hx:  # 目标在 hero 的右侧
        return 'right'
    elif ay < hy:  # 目标在 hero 的上方
        return 'up'
    elif ay > hy:  # 目标在 hero 的下方
        return 'down'

def get_tag_by_direction(direction):
    # 计算行走的方向
    if direction == 'up':
        return 'opendoor_u'
    elif direction == 'down':
        return 'opendoor_d'
    elif direction == 'left':
        return 'opendoor_l'
    elif direction == 'right':
        return 'opendoor_r'

# 定义模块级别的变量
_img_map = None
_cfgs = None
def load_map_template(map_name='bwj_room'):
    """
    加载布万加的地图模板
    :return:
    """
    try:
        global _img_map, _cfgs  # 声明使用模块级别的变量
        # 加载布万加的地图模板
        map_template = TemplateUtil().load_template(map_name)
        _img_map = map_template.img_map
        _cfgs = map_template.cfgs
    except Exception as e:
        # 处理可能出现的异常
        log.logger.info(f"加载{map_name}地图模板时发生错误: {e}")


def find_cur_room(screen,cur_room, confi=0.7):
    """
    根据小地图特征找当前房间
    :param screen: 当前帧
    :param confi: 默认最小置信度
    :return: flag 是否匹配成功, room
    """
    #加入当前图的判断，已经过去的图，不再判断,index为当前地图的索引
    index  = 0
    if cur_room in room_route:
        index = room_route.index(cur_room)
        log.logger.info(f'当前房间索引号{cur_room}')

    flag = False
    most_similar_room = None
    if _img_map is None or _cfgs is None:
        load_map_template()
    if isinstance(_cfgs, list):
        confidence = confi
        for cfg in _cfgs:
            # 识别区域
            crop = cfg['rect']
            img_name = cfg['img_name']
            img = _img_map[img_name]
            #配置文件中的每一个地图
            current_room = tuple(cfg['name'])
            #加入当前图的判断，已经过去的图，不再判断
            if current_room in room_route:
                if room_route.index(current_room) < index:
                    log.logger.info(f'已经过图,不在判断{current_room}')
                    continue
            else:
                log.logger.info(f'找不到当前房间号:{current_room}')
            res = image_match_util.cvmatch_template_best(img, screen,current_room, crop,)
            if res is not None:
                # 取可信度最高的匹配结果
                if res['confidence'] > confidence:
                    confidence = res['confidence']
                    flag = True
                    most_similar_room = current_room

    if cur_room is None:
        cur_room = most_similar_room
        log.logger.warn(f'当前房间为空,直接使用匹配结果')
    if most_similar_room is not None:
        log.logger.info(f'匹配房间结果：{flag},房间行列号:{most_similar_room}')
        if cur_room[0] - most_similar_room[0] not in {0, 1,-1}:
            log.logger.info(f'1匹配房间误差太大，使用原有数据,当前房间号:{cur_room},匹配的房间号:{most_similar_room}')
            return flag, cur_room
        elif cur_room[1] - most_similar_room[1] not in {0, 1,-1}:
            log.logger.info(f'2匹配房间误差太大，使用原有数据,当前房间号:{cur_room},匹配的房间号:{most_similar_room}')
            return flag, cur_room
    else:
        #新增，匹配地图失败，直接返回预定路线中的地图
        return flag, cur_room

    return flag, most_similar_room


def find_cur_room2(screen,cur_room, confi=0.7):
    """
    直接返回当前房间，只匹配狮子头前的房间，和狮子头房间
    :param screen: 当前帧
    :param confi: 默认最小置信度
    :return: flag 是否匹配成功, room
    """
    room_ = cur_room[0] == 1 and cur_room[1] == 2
    room_2 = cur_room[0] == 1 and cur_room[1] == 1
    if room_ or room_2:
        flag = False
        most_similar_room = None
        if _img_map is None or _cfgs is None:
            load_map_template()
        if isinstance(_cfgs, list):
            confidence = confi
            for cfg in _cfgs:
                # 识别区域
                crop = cfg['rect']
                img_name = cfg['img_name']
                img = _img_map[img_name]
                # 配置文件中的每一个地图
                current_room = tuple(cfg['name'])
                res = image_match_util.cvmatch_template_best(img, screen, current_room, crop, )
                if res is not None:
                    # 取可信度最高的匹配结果
                    if res['confidence'] > confidence:
                        confidence = res['confidence']
                        flag = True
                        most_similar_room = current_room
        if flag is True:
            #新增，匹配地图失败，直接返回预定路线中的地图
            return flag, most_similar_room
    return True,cur_room

if __name__ == '__main__':
    t = rect_slice_index(Rect(100, 100, 100, 100), Size((10, 6)), (101.54, 145.864))
    log.logger.info(get_next_room((1, 1), False))
    log.logger.info(t)
    log.logger.info(t == (4, 0))
    log.logger.info(get_cur_room_index((101.54, 145.864)))
    log.logger.info(get_run_direction((0, 1), (0, 2)))
    log.logger.info(get_run_direction((0, 2), (1, 2)))