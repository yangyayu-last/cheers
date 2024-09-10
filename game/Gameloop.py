import time

from logger import log


class GameState:
    PICKING_UP_EQUIPMENT = 'picking_up_equipment'
    ATTACKING_MONSTER = 'attacking_monster'
    MOVING_TO_NEXT_ROOM = 'moving_to_next_room'
    SELECTING_CARD = 'selecting_card'
    IDLE = 'idle'

class GameLoop:

    def __init__(self, action,infer_queue):
        self.action = action
        self.state = GameState.IDLE  # 初始状态为 idle
        self.last_action_time = time.time()  # 记录上一次动作时间，用于防止动作停滞
        self.infer_queue = infer_queue
        #没有发现任何目标的次数，有可能卡在哪个缝隙了
        self.no_task_no = 0

    def update(self,screen, result):
        # 获取当前屏幕和分析结果
        # screen, result = self.action.find_result()

        # 优先级 1：敌人
        if len(self.action.find_tag(result, ['Monster', 'Monster_ds', 'Monster_szt'])) > 0:
            if self.state != GameState.ATTACKING_MONSTER:
                log.logger.info('发现怪物，停止其他动作，优先攻击怪物...')
                self.state = GameState.ATTACKING_MONSTER
            # 持续攻击怪物，直到没有怪物为止
            self.action.attack_master()
            self.no_task_no = 0
            return

        # 优先级 2：装备
        if len(self.action.find_tag(result, 'equipment')) > 0:
            if self.state != GameState.PICKING_UP_EQUIPMENT:
                log.logger.info('发现装备，停止其他动作，优先捡装备...')
                self.state = GameState.PICKING_UP_EQUIPMENT
            # 持续捡装备，直到没有装备为止
            self.action.pick_up_equipment()
            self.no_task_no = 0
            return

        # 优先级 3：门（移动到下一个房间）
        if len(self.action.find_tag(result, ['go', 'go_d', 'go_r', 'go_u', 'opendoor_d', 'opendoor_r', 'opendoor_u', 'opendoor_l'])) > 0:
            if self.state != GameState.MOVING_TO_NEXT_ROOM:
                log.logger.info('发现门，停止其他动作，移动到下一个房间...')
                self.state = GameState.MOVING_TO_NEXT_ROOM
            # 持续移动到下一个房间，直到进入房间为止
            self.action.move_to_next_room()
            self.no_task_no = 0
            return

        # 优先级 4：选择卡片（如果没有其他更高优先级的任务）
        if len(self.action.find_tag(result, ['select', 'start', 'card'])) > 0:
            if self.state != GameState.SELECTING_CARD:
                log.logger.info('发现选择框或牌子卡片，开始选择...')
                self.state = GameState.SELECTING_CARD
            # 持续选择卡片，直到完成
            self.action.reset_start_game()
            self.no_task_no = 0
            return

        # 如果没有任何需要执行的动作，进入空闲状态
        log.logger.info('没有发现任何目标，进入空闲状态...')
        self.no_task_no += 1
        self.state = GameState.IDLE

        # 记录当前的时间，并计算每次动作的间隔
        elapsed_time = time.time() - self.last_action_time
        self.last_action_time = time.time()
        log.logger.info(f"一次循环花费时间: {elapsed_time:.4f} 秒")
