from adb.scrcpy_adb import ScrcpyADB
from game import GameControl
from game.attack.attack_master import AttackMaster
from game.game_action import GameAction


def run():
    ctrl = GameControl(ScrcpyADB(1384)) #1384
    action = GameAction(ctrl)
    attack_master = AttackMaster(ctrl)
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