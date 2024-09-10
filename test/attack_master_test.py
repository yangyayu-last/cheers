from adb.scrcpy_adb import ScrcpyADB
from game import GameControl
from game.Gameloop import GameLoop
from game.attack.attack_master import AttackMaster
from game.game_action import GameAction, AutoCleaningQueue


def run():
    image_queue = AutoCleaningQueue(maxsize=3)
    infer_queue = AutoCleaningQueue(maxsize=3)
    show_queue = AutoCleaningQueue(maxsize=3)
    frame_counter = 0
    ctrl = GameControl(ScrcpyADB(image_queue, infer_queue, show_queue, max_width=1384))  # 1384
    action = GameAction(ctrl, infer_queue)
    loop = GameLoop(action, infer_queue)
    action.ctrl.attack2(5)
    # attack_master.room_skill((1,0))
    # attack_master.hurt_skill()
    # attack_master.state_skill()
    # attack_master.buff_skill()
    #向右移动
    # ctrl.move(0,3)
    #向上移动
    ctrl.move(90,3)
    #向左移动
    # ctrl.move(180,3)
    #向下移动
    # ctrl.move(270,3)
    # skill_method = getattr(ctrl, 'move')
    #
    # skill_method([0,2])
    pass


if __name__ == '__main__':
    run()