from adb.scrcpy_adb import ScrcpyADB
from game import GameControl
from game.attack.attack_master import AttackMaster
from game.game_action import GameAction


def run():
    ctrl = GameControl(ScrcpyADB(1384)) #1384
    action = GameAction(ctrl)
    attack_master = AttackMaster(ctrl)
    attack_master.room_skill((1,0))
    # attack_master.hurt_skill()
    # attack_master.state_skill()
    # attack_master.buff_skill()
    pass


if __name__ == '__main__':
    run()