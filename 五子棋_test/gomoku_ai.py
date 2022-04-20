import sys
import numpy as np

value_lf = 1000
value_lt = 100
key_white = 2
key_black = 1
key_block = 0
depth = 2


class AI:
    def __init__(self, state_board):
        self.state_board = state_board
        self.pos_white = []  # 记录白棋的位置
        self.pos_black = []  # 记录黑棋的位置
        self.size = len(state_board)
        for i in range(self.size):
            for j in range(self.size):
                if state_board[i][j].value == key_black:
                    self.pos_black.append((i, j))
                elif state_board[i][j].value == key_white:
                    self.pos_white.append((i, j))

    def ab_search(self):  # 返回下一步的坐标
        _, x, y = self.max_value(-sys.maxsize - 1, sys.maxsize, depth)
        return x, y

    def max_value(self, a, b, dep):
        if dep == 0:
            return self.eval(), 0, 0
        val = -sys.maxsize - 1
        best_act = ()
        acts = self.action()

        for act in acts:
            self.push(dep, act)
            val = max(val, self.min_value(a, b, dep - 1)[0])
            self.pop(dep, act)
            # 剪枝
            if val >= b:
                return val, act[0], act[1]
            if val >= a:
                a = val
                best_act = act
        return val, best_act[0], best_act[1]

    def min_value(self, a, b, dep):
        if dep == 0:
            return self.eval(), 0, 0
        val = sys.maxsize
        best_act = ()
        acts = self.action()

        for act in acts:
            self.push(dep, act)
            val = min(val, self.max_value(a, b, dep - 1)[0])
            self.pop(dep, act)
            if val <= a:
                return val, act[0], act[1]
            if val <= b:
                b = val
                best_act = act
        return val, best_act[0], best_act[1]

    # 由于根节点为下白棋，故可以根据dep来判断该步下黑棋还是白棋
    def push(self, flag, act):
        if flag & 1:
            self.pos_black.append(act)
            self.state_board[act[0]][act[1]].value = key_black
        else:
            self.pos_white.append(act)
            self.state_board[act[0]][act[1]].value = key_white

    def pop(self, flag, act):
        if flag & 1:
            self.pos_black.pop()
        else:
            self.pos_white.pop()
        self.state_board[act[0]][act[1]].value = key_block

    def action(self):
        mx_r_w, mx_c_w, mn_r_w, mn_c_w = 0, 0, 0, 0
        mx_r_b, mx_c_b, mn_r_b, mn_c_b = 0, 0, 0, 0
        #print(self.pos_white)


        if len(self.pos_white) != 0:
            mx_r_w, mx_c_w = np.max(self.pos_white, axis=0)
            mn_r_w, mn_c_w = np.min(self.pos_white, axis=0)

        if len(self.pos_black) != 0:
            mx_r_b, mx_c_b = np.max(self.pos_black, axis=0)
            mn_r_b, mn_c_b = np.min(self.pos_black, axis=0)
        else:
            mx_r_b, mx_c_b = mx_r_w, mx_c_w
            mn_r_b, mn_c_b = mn_r_w, mn_c_w

        # 构造可下子的方形区域
        r_begin = min(max(0, mn_r_w - 2), max(0, mn_r_b - 2))
        r_end = max(min(14, mx_r_w + 2), min(14, mx_r_b + 2))
        c_begin = min(max(0, mn_c_w - 2), max(0, mn_c_b - 2))
        c_end = max(min(14, mx_c_w + 2), min(14, mx_c_b + 2))

        act = []
        r = r_begin
        while r <= r_end:
            c = c_begin
            while c <= c_end:
                if self.state_board[r][c].value == 0:
                    act.append((r, c))
                c = c + 1
            r = r + 1
        return act

    def eval(self):
        num_lf = self.live_four()
        num_lt = self.live_three()
        return num_lf * value_lf + num_lt * value_lt

    def in_board(self, row, col):
        if row < 0 or row > self.size - 1 or col < 0 or col > self.size - 1:
            return False
        return True

    # 活四
    def live_four(self):
        # 计算白棋活四数量
        num_w = self.cal_live_four(self.pos_white, key_white)
        # 计算黑棋活四数量
        num_b = self.cal_live_four(self.pos_black, key_black)
        return num_w - num_b

    def cal_live_four(self, pos, key):
        num = 0
        for r, c in pos:
            if self.same(r + 1, c, 0) and self.same(r - 4, c, 0) \
                    and self.same(r - 1, c, key) and self.same(r - 2, c, key) and self.same(r - 3, c, key):
                num = num + 1

            if self.same(r + 1, c - 1, 0) and self.same(r - 4, c + 4, 0) \
                    and self.same(r - 1, c + 1, key) and self.same(r - 2, c + 2, key) and self.same(r - 3, c + 3, key):
                num = num + 1

            if self.same(r, c - 1, 0) and self.same(r, c + 4, 0) \
                    and self.same(r, c + 1, key) and self.same(r, c + 2, key) and self.same(r, c + 3, key):
                num = num + 1

            if self.same(r - 1, c - 1, 0) and self.same(r + 4, c + 4, 0) \
                    and self.same(r + 1, c + 1, key) and self.same(r + 2, c + 2, key) and self.same(r + 3, c + 3, key):
                num = num + 1
        return num

    def same(self, row, col, key):
        if not self.in_board(row, col):
            return False
        return self.state_board[row][col].value == key

    # 活三
    def live_three(self):
        num_w = self.cal_live_three(self.pos_white, key_white)
        num_b = self.cal_live_three(self.pos_black, key_black)
        return num_w - num_b

    def cal_live_three(self, pos, key):
        num = 0
        for r, c in pos:
            # 朝上两种
            if self.same(r + 1, c, 0) and self.same(r - 1, c, key) \
                    and ((self.same(r - 3, c, 0) and self.same(r - 2, c, key) and (
                    self.same(r + 2, c, 0) or self.same(r - 4, c, 0)))
                         or (self.same(r - 2, c, 0) and self.same(r - 3, c, key) and self.same(r - 4, c, 0))):
                num = num + 1
            # 斜上两种
            if self.same(r + 1, c - 1, 0) and self.same(r - 1, c + 1, key) \
                    and ((self.same(r - 3, c + 3, 0) and self.same(r - 2, c + 2, key) and
                          (self.same(r + 2, c - 2, 0) or self.same(r - 4, c + 4, 0)))
                         or (self.same(r - 2, c + 2, 0) and self.same(r - 3, c + 3, key) and self.same(r - 4, c + 4,
                                                                                                       0))):
                num = num + 1
            # 横向两种
            if self.same(r, c - 1, 0) and self.same(r, c + 1, key) \
                    and ((self.same(r, c + 3, 0) and self.same(r, c + 2, key)
                          and (self.same(r, c - 2, 0) or self.same(r, c + 4, 0)))
                         or (self.same(r, c + 2, 0) and self.same(r, c + 3, key) and self.same(r, c + 4, 0))):
                num = num + 1
            # 斜下两种
            if self.same(r - 1, c - 1, 0) and self.same(r + 1, c + 1, key) \
                    and ((self.same(r + 3, c + 3, 0) and self.same(r + 2, c + 2, key)
                          and (self.same(r - 2, c - 2, 0) or self.same(r + 4, c + 4, 0)))
                         or (self.same(r + 2, c + 2, 0) and self.same(r + 3, c + 3, key) and self.same(r + 4, c + 4,
                                                                                                       0))):
                num = num + 1
        return num

    def rush_four(self):
        pass

    def cal_rush_four(self, pos, key):
        pass
