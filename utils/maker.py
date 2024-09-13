import cv2
import json
import os
from adb.scrcpy_adb import ScrcpyADB
import time
"""
框选自动生成文件的工具,模板不需要去截图了
连上手机后直接运行，直接在画面中划定区域就可以

"""
root = r'./template/'
img_desc = '背包内分解-确认按钮'
template_name = 'zzz_test'

from_emulator = True

rect = (0, 0, 1, 1)
rectangle = False
rect_over = False
if from_emulator:
    adb = ScrcpyADB(1384)
    time.sleep(1)
    sceneImg = adb.last_screen
    # sceneImg = sceneImg.mat
else:
    sceneImg = cv2.imread('test.jpg')

# cv2.imwrite('out.jpg', sceneImg)
sceneImgShow = sceneImg
height, width, channels = sceneImg.shape


def onmouse(event, x, y, flags, params):
    global sceneImgShow, sceneImg, rectangle, rect, ix, iy, rect_over

    # Draw Rectangle
    if event == cv2.EVENT_LBUTTONDOWN:
        print('按下鼠标左键')
        rectangle = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if rectangle:
            print(f'指针移动到{x,y}')
            sceneImgShow = sceneImg.copy()
            cv2.rectangle(sceneImgShow, (ix, iy), (x, y), (255, 0, 0), 1)
            cv2.imshow('mouse input', sceneImgShow)
            rect = (min(ix, x), min(iy, y), abs(ix - x), abs(iy - y))

    elif event == cv2.EVENT_LBUTTONUP:
        print('松开了鼠标左键')
        rectangle = False
        rect_over = True
        rect = (min(ix, x), min(iy, y), abs(ix - x), abs(iy - y))
        x1, y1, w, h = rect
        roi = sceneImg[y1:y1 + h, x1:x1 + w]

        x1 = x1 - 5 if x1 > 5 else 0
        y1 = y1 - 5 if y1 > 5 else 0
        w = w + 10 if x1 + w + 10 < width else width - x1 - 1
        h = h + 10 if y1 + h + 10 < height else height - y1 - 1

        # {"rect": [91, 589, 114, 38], "img_name": "img.png", "desc": "打开世界地图，rect为x,y,w,h，可以通过截图工具得到，这个参数根据投屏的画面决定"}
        config = {
            'rect': [x1, y1, w, h],
            'img_name': 'img.png',
            'desc': f'{img_desc}，rect为x,y,w,h，可以通过截图工具得到，这个参数根据投屏的画面决定'
        }

        try:
            os.mkdir(root + template_name)
        except Exception as e:
            print(e)

        write_path = root + template_name + '/img' + '.png'
        cv2.imencode('.png', roi)[1].tofile(write_path)
        with open(root + template_name + '/cfg' + '.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False)


# Named window and mouse callback
cv2.namedWindow('mouse input')
cv2.setMouseCallback('mouse input', onmouse)
cv2.imshow('mouse input', sceneImg)

keyPressed = None
running = True
scene = False
while running:
    keyPressed = cv2.waitKey(1)
    if keyPressed == ord('s'):
        running = False

cv2.destroyAllWindows()
