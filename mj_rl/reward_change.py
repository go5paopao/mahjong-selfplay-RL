import os

class Reward():
    """
    報酬を状態に応じて決めるためのクラス
    段階的な報酬を定義し、条件を満たしたら次の状態に進む
    """
    def __init__(self):
        self.stage = 0
        self.max_stage = 6
        self.stage_clear_rate = {
            0:0.9,
            1:0.9,
            2:0.9,
            3:0.9,
            4:0.7,
            5:0.6,
            6:0.3
        }
    def get_result_and_reward(self,mj):
        """現在の報酬ステージと結果から報酬を決める"""
        result = None
        reward = 0
        stop_flg = False
        if self.stage == 0:
            if mj.missed:
                reward = -1
                result = -1
                stop_flg = True
            elif mj.turn_num > 3:
                reward = 1
                result = 1
                stop_flg = True
            else:
                reward = 0
        elif self.stage == 1:
            if mj.missed:
                reward = -1
                result = -1
                stop_flg = True
            elif mj.turn_num > 7:
                reward = 1
                result = 1
                stop_flg = True
            else:
                reward = 0
        elif self.stage == 2:
            if mj.missed:
                reward = -1
                result = -1
                stop_flg = True
            elif mj.turn_num > 15:
                reward = 1
                result = 1
                stop_flg = True
            else:
                reward = 0
        elif self.stage == 3:
            if mj.missed:
                reward = -1
                result = -1
                stop_flg = True
            elif mj.turn_num > RYUKYOKU_NUM:
                reward = 1
                result = 1
                stop_flg = True
            else:
                reward = 0
        elif self.stage == 4:
            if mj.missed:
                reward = -1
                result = -1
                stop_flg = True
            elif mj.syanten <= 1:
                reward = 1
                result = 1
                stop_flg = True
            elif mj.turn_num > RYUKYOKU_NUM:
                reward = 0
                result = 0
                stop_flg = True
            else:
                reward = 0
        elif self.stage == 5:
            if mj.missed:
                reward = -1
                result = -1
                stop_flg = True
            elif mj.syanten <= 0:
                reward = 1
                result = 1
                stop_flg = True
            elif mj.turn_num > RYUKYOKU_NUM:
                reward = 0
                result = 0
                stop_flg = True
            else:
                reward = 0
        elif self.stage == 6:
            if mj.missed:
                reward = -1
                result = -1
                stop_flg = True
            elif mj.syanten < 0:
                reward = 1
                result = 1
                stop_flg = True
            elif mj.turn_num > RYUKYOKU_NUM:
                reward = 0
                result = 0
                stop_flg = True
            else:
                reward = 0
        return reward,result,stop_flg

    def stage_check(self,win,miss,draw):
        """報酬ステージをクリアしたかをチェック"""
        win_rate = float(win) / (win+miss+draw)
        if win_rate > self.stage_clear_rate[self.stage] and self.stage < self.max_stage:
            print ("StageUp:{0}to{1}".format(self.stage,self.stage+1))
            self.stage += 1

