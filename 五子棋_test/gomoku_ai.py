import sys
import numpy as np

value_sf = 1000
value_lf = 400
value_lt = 100
value_rf = 150
value_st = 50
value_ltw = 30
key_white = 2
key_black = 1
key_block = 0
depth = 2
dx = [-1, -1, 0, 1]
dy = [0, 1, 1, 1]


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

    def clear(self):
        self.pos_black.clear()
        self.pos_white.clear()

    def ab_search(self):  # 返回下一步的坐标
        _, x, y = self.max_value(-sys.maxsize - 1, sys.maxsize, depth)
        return x, y

    def max_value(self, a, b, dep):
        if dep == 0:
            return self.eval(), 0, 0
        val = -sys.maxsize - 1
        best_act = ()
        acts = self.action('near')

        for act in acts:
            self.push(dep, act)  # debug 原为self.push(dep, act)
            val = max(val, self.min_value(a, b, dep - 1)[0])
            self.pop(dep, act)
            # 剪枝
            if val >= b:
                return val, act[0], act[1]
            if val > a:
                a = val
                best_act = act
        return val, best_act[0], best_act[1]

    def min_value(self, a, b, dep):
        if dep == 0:
            return self.eval(), 0, 0
        val = sys.maxsize
        best_act = ()
        acts = self.action('near')

        for act in acts:
            self.push(dep, act)
            val = min(val, self.max_value(a, b, dep - 1)[0])
            self.pop(dep, act)
            if val <= a:
                return val, act[0], act[1]
            if val < b:
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

    def action(self, method):
        if method == 'matrix':
            return self.action_matrix()
        if method == 'near':
            return self.action_near()

    def action_matrix(self):
        mx_r, mx_c, mn_r, mn_c = 0, 0, 0, 0
        pos = self.pos_white + self.pos_black
        if len(pos) != 0:
            mx_r, mx_c = np.max(pos, axis=0)
            mn_r, mn_c = np.min(pos, axis=0)

        # 构造可下子的方形区域
        r_begin = max(0, mn_r - 2)
        r_end = min(self.size - 1, mx_r + 2)
        c_begin = max(0, mn_c - 2)
        c_end = min(self.size - 1, mx_c + 2)

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

    def action_near(self):
        board = np.zeros((self.size, self.size))
        pos = np.array(self.pos_white + self.pos_black)
        for r, c in pos:
            r_begin = max(0, r - 1)
            r_end = min(self.size - 1, r + 1)
            c_begin = max(0, c - 1)
            c_end = min(self.size - 1, c + 1)
            board[r_begin:r_end + 1, c_begin:c_end + 1] = 1
        board[pos[:, 0], pos[:, 1]] = 0
        return np.argwhere(board == 1)

    def eval(self):
        num_lf = self.live_four()
        num_lt = self.live_three()
        num_rf = self.rush_four()
        num_st = self.sleep_three()
        num_ltw = self.live_two()
        num_sf = self.succ_five()

        return num_sf * value_sf + num_lf * value_lf + num_lt * value_lt + num_rf * value_rf + num_st * value_st + \
               num_ltw * value_ltw

    def in_board(self, row, col):
        if row < 0 or row > self.size - 1 or col < 0 or col > self.size - 1:
            return False
        return True

    def succ_five(self):
        num_w = self.cal_succ_five(self.pos_white, key_white)
        num_b = self.cal_succ_five(self.pos_black, key_black)
        return num_w - num_b

    def cal_succ_five(self, pos, key):
        num = 0
        l = len(dx)
        for r, c in pos:
            for i in range(l):
                if self.same(r + dx[i], c + dy[i], key) and self.same(r + 2 * dx[i], c + 2 * dy[i], key) and \
                        self.same(r + 3 * dx[i], c + 3 * dy[i], key) and self.same(r + 4 * dx[i], c + 4 * dy[i], key):
                    num = num + 1
        return num

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
            if self.same(r + 1, c, key_block) and self.same(r - 4, c, key_block) \
                    and self.same(r - 1, c, key) and self.same(r - 2, c, key) and self.same(r - 3, c, key):
                num = num + 1

            if self.same(r + 1, c - 1, key_block) and self.same(r - 4, c + 4, key_block) \
                    and self.same(r - 1, c + 1, key) and self.same(r - 2, c + 2, key) and self.same(r - 3, c + 3, key):
                num = num + 1

            if self.same(r, c - 1, key_block) and self.same(r, c + 4, key_block) \
                    and self.same(r, c + 1, key) and self.same(r, c + 2, key) and self.same(r, c + 3, key):
                num = num + 1

            if self.same(r - 1, c - 1, key_block) and self.same(r + 4, c + 4, key_block) \
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
            if self.same(r + 1, c, key_block) and self.same(r - 1, c, key) \
                    and ((self.same(r - 3, c, key_block) and self.same(r - 2, c, key) and (
                    self.same(r + 2, c, key_block) or self.same(r - 4, c, key_block)))
                         or (self.same(r - 2, c, key_block) and self.same(r - 3, c, key) and self.same(r - 4, c,
                                                                                                       key_block))):
                num = num + 1
            # 斜上两种
            if self.same(r + 1, c - 1, key_block) and self.same(r - 1, c + 1, key) \
                    and ((self.same(r - 3, c + 3, key_block) and self.same(r - 2, c + 2, key) and
                          (self.same(r + 2, c - 2, key_block) or self.same(r - 4, c + 4, key_block)))
                         or (self.same(r - 2, c + 2, key_block) and self.same(r - 3, c + 3, key) and self.same(r - 4,
                                                                                                               c + 4,
                                                                                                               key_block))):
                num = num + 1
            # 横向两种
            if self.same(r, c - 1, key_block) and self.same(r, c + 1, key) \
                    and ((self.same(r, c + 3, key_block) and self.same(r, c + 2, key)
                          and (self.same(r, c - 2, key_block) or self.same(r, c + 4, key_block)))
                         or (self.same(r, c + 2, key_block) and self.same(r, c + 3, key) and self.same(r, c + 4,
                                                                                                       key_block))):
                num = num + 1
            # 斜下两种
            if self.same(r - 1, c - 1, key_block) and self.same(r + 1, c + 1, key) \
                    and ((self.same(r + 3, c + 3, key_block) and self.same(r + 2, c + 2, key)
                          and (self.same(r - 2, c - 2, key_block) or self.same(r + 4, c + 4, key_block)))
                         or (self.same(r + 2, c + 2, key_block) and self.same(r + 3, c + 3, key) and self.same(r + 4,
                                                                                                               c + 4,
                                                                                                               key_block))):
                num = num + 1
        return num

    def rush_four(self):
        num_w = self.cal_rush_four(self.pos_white, key_white)
        num_b = self.cal_rush_four(self.pos_black, key_black)
        return num_w - num_b

    def cal_rush_four(self, pos, key):
        num = 0
        for r, c in pos:
            for i in range(len(dx)):
                if (self.same(r - dx[i], c - dy[i], key_block) ^ self.same(r + dx[i] * 4, c + 4 * dy[i], key_block)) \
                        and self.same(r + dx[i], c + dy[i], key) and self.same(r + 2 * dx[i], c + 2 * dy[i], key) and \
                        self.same(r + 3 * dx[i], c + 3 * dy[i], key):
                    num = num + 1
                elif self.same(r + dx[i], c + dy[i], key) and self.same(r + 2 * dx[i], c + 2 * dy[i], key_block) and \
                        self.same(r + 3 * dx[i], c + 3 * dy[i], key) and self.same(r + 4 * dx[i], c + 4 * dy[i], key):
                    num = num + 1
                elif self.same(r + dx[i], c + dy[i], key_block) and self.same(r + 2 * dx[i], c + 2 * dy[i], key) and \
                        self.same(r + 3 * dx[i], c + 3 * dy[i], key) and self.same(r + 4 * dx[i], c + 4 * dy[i], key):
                    num = num + 1
                elif self.same(r + dx[i], c + dy[i], key) and self.same(r + 2 * dx[i], c + 2 * dy[i], key) and \
                        self.same(r + 3 * dx[i], c + 3 * dy[i], key_block) and self.same(r + 4 * dx[i], c + 4 * dy[i],
                                                                                         key):
                    num = num + 1
        return num

    def sleep_three(self):
        num_w = self.cal_sleep_three(self.pos_white, key_white)
        num_b = self.cal_sleep_three(self.pos_black, key_black)
        return num_w - num_b

    def cal_sleep_three(self, pos, key):
        num = 0
        l = len(dx)
        for r, c in pos:
            for i in range(l):
                if self.same(r + dx[i], c + dy[i], key) and self.same(r + 2 * dx[i], c + 2 * dy[i], key) and \
                        ((not self.same(r - 2 * dx[i], c - 2 * dy[i], key_block)
                          and self.same(r - dx[i], c - dy[i], key_block)
                          and self.same(r + 3 * dx[i], c + 3 * dy[i], key_block)
                          and not self.same(r + 4 * dx[i], c + 4 * dy[i], key_block))
                         or
                         (self.same(r - 2 * dx[i], c - 2 * dy[i], key_block)
                          and self.same(r - dx[i], c - dy[i], key_block)
                          and not self.same(r + 3 * dx[i], c + 3 * dy[i], key_block))
                         or
                         (not self.same(r - dx[i], c - dy[i], key_block)
                          and self.same(r + 3 * dx[i], c + 3 * dy[i], key_block)
                          and self.same(r + 4 * dx[i], c + 4 * dy[i], key_block))):
                    num = num + 1
                elif self.same(r + dx[i], c + dy[i], key_block) and self.same(r + 2 * dx[i], c + 2 * dy[i], key) \
                        and self.same(r + 3 * dx[i], c + 3 * dy[i], key) \
                        and (self.same(r - dx[i], c - dy[i], key_block) ^ self.same(r + 4 * dx[i], c + 4 * dy[i],
                                                                                    key_block)):
                    num = num + 1
                elif self.same(r + dx[i], c + dy[i], key) and self.same(r + 2 * dx[i], c + 2 * dy[i], key_block) \
                        and self.same(r + 3 * dx[i], c + 3 * dy[i], key) \
                        and (self.same(r - dx[i], c - dy[i], key_block) ^ self.same(r + 4 * dx[i], c + 4 * dy[i],
                                                                                    key_block)):
                    num = num + 1
                elif self.same(r + dx[i], c + dy[i], key) and self.same(r + 2 * dx[i], c + 2 * dy[i], key_block) \
                        and self.same(r + 3 * dx[i], c + 3 * dy[i], key_block) and self.same(r + 4 * dx[i],
                                                                                             c + 4 * dy[i], key):
                    num = num + 1
                elif self.same(r + dx[i], c + dy[i], key_block) and self.same(r + 2 * dx[i], c + 2 * dy[i], key) \
                        and self.same(r + 3 * dx[i], c + 3 * dy[i], key_block) and self.same(r + 4 * dx[i],
                                                                                             c + 4 * dy[i], key):
                    num = num + 1
                elif self.same(r + dx[i], c + dy[i], key_block) and self.same(r + 2 * dx[i], c + 2 * dy[i], key_block) \
                        and self.same(r + 3 * dx[i], c + 3 * dy[i], key) and self.same(r + 4 * dx[i],
                                                                                       c + 4 * dy[i], key):
                    num = num + 1
        return num

    def live_two(self):
        num_w = self.cal_live_two(self.pos_white, key_white)
        num_b = self.cal_live_two(self.pos_black, key_black)
        return num_w - num_b

    def cal_live_two(self, pos, key):
        num = 0
        l = len(dx)
        for r, c in pos:
            for i in range(l):
                if self.same(r - dx[i], c - dy[i], key_block) and self.same(r + dx[i], c + dy[i], key) \
                        and self.same(r + 2 * dx[i], c + 2 * dy[i], key_block) and \
                        ((self.same(r - 3 * dx[i], c - 3 * dy[i], key_block) and self.same(r - 2 * dx[i], c - 2 * dy[i],
                                                                                           key_block))
                         or
                         (self.same(r - 2 * dx[i], c - 2 * dy[i], key_block) and self.same(r + 3 * dx[i], c + 3 * dy[i],
                                                                                           key_block))
                         or
                         (self.same(r + 3 * dx[i], c + 3 * dy[i], key_block) and self.same(r + 4 * dx[i], c + 4 * dy[i],
                                                                                           key_block))):
                    num = num + 1
                elif self.same(r - dx[i], c - dy[i], key_block) and self.same(r + dx[i], c + dy[i], key_block) \
                        and self.same(r + 2 * dx[i], c + 2 * dy[i], key) and self.same(r + 3 * dx[i], c + 3 * dy[i],
                                                                                       key_block) and \
                        (self.same(r - 2 * dx[i], c - 2 * dy[i], key_block) or (
                                self.same(r + 4 * dx[i], c + 4 * dy[i], key_block))):
                    num = num + 1
                elif self.same(r + dx[i], c + dy[i], key_block) and self.same(r + 2 * dx[i], c + 2 * dy[i], key_block) \
                        and self.same(r + 3 * dx[i], c + 3 * dy[i], key) and self.same(r - dx[i], c - dy[i], key_block) \
                        and self.same(r + 4 * dx[i], c + 4 * dy[i], key_block):
                    num = num + 1
        return num

    def sleep_two(self):
        pass

    def cal_sleep_two(self, pos, key):
        pass
