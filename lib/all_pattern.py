#!/usr/bin/env python3
import copy
import random
import json

# 各役職が占い師CO
VILLAGER_CO = 0.7
SEER_CO = 1.2
POSESSED_CO = 1.2
WEREWOLF_CO = 1.1

# 占い師が嘘の結果を言う
SEER_WRONG_RESULT = 0.8

# 村人2CO
TWO_VILLAGER_CO = 0.001

# 占い師が1日目の投票までにCOしない
SEER_NO_CO = 0.5

# 自分に白出しor他に黒出ししたプレイヤーに人狼が投票
WEREWOLF_VOTE_FAKE_SEER = 0.5

# 占い師が白出しをしたプレイヤーがCOしておらず，かつ狂人の場合
SEER_WHITE_NOCO_POSSESSED = 0.8


class RolePattern:
    def __init__(self, json_file):
        f = open(json_file, "r")
        self.pattern_score_map = {}
        self.role_pattern = []
        agent_id_list = [1,2,3,4,5]

        for l in json.load(f):
            tmp_map = {}
            for k, v in l.items():
                tmp_map[int(k)] = v
            self.role_pattern.append(tmp_map)
            self.pattern_score_map[str(tmp_map)] = 1.0
        f.close()

    def day_one_update(self, seer_co_id_list, divine_list, vote_phase=False, my_id=None, my_role=None):
        if my_id is not None and my_role is not None:
            new_pattern = []
            for p in self.role_pattern:
                if p[my_id] == my_role:
                    new_pattern.append(p)
                else:
                    self.pattern_score_map[str(p)] *= 0.0
            self.role_pattern = new_pattern

        self.update_by_seer_co(seer_co_id_list, after_day_one_vote=vote_phase)
        self.update_by_divine(seer_co_id_list, divine_list)

    def day_two_update(self, seer_co_id_list, divine_list, vote_list, dead_id_list, my_id=None, my_role=None):
        if my_id is not None and my_role is not None:
            new_pattern = []
            for p in self.role_pattern:
                if p[my_id] == my_role:
                    new_pattern.append(p)
                else:
                    self.pattern_score_map[str(p)] *= 0.0
            self.role_pattern = new_pattern

        self.update_by_seer_co(seer_co_id_list, after_day_one_vote=True)
        self.update_by_divine(seer_co_id_list, divine_list)
        self.update_by_divine_and_vote(divine_list, vote_list)
        self.update_by_death(dead_id_list)

    def update_by_divine(self, seer_co_id_list, divine_list):
        for p in self.role_pattern:
            for d in divine_list:
                divine_agent_id = d[0]
                divine_target_id = d[1]
                result = d[2]

                if p[divine_agent_id] == "占":
                    if p[divine_target_id] == "狼" and result == "HUMAN":
                        self.pattern_score_map[str(p)] *= SEER_WRONG_RESULT
                    elif p[divine_target_id] != "狼" and result == "WEREWOLF":
                        self.pattern_score_map[str(p)] *= SEER_WRONG_RESULT
                    # 白だししたプレイヤーが狂人でありかつCOしていない
                    if p[divine_target_id] == "狂" and result == "HUMAN" and divine_target_id not in seer_co_id_list:
                        self.pattern_score_map[str(p)] *= SEER_WHITE_NOCO_POSSESSED

    def update_by_divine_and_vote(self, divine_list, vote_list):
        for p in self.role_pattern:
            # divineとvoteの組合せ
            for v in vote_list:
                vote_agent_id = v[0]
                vote_target_id = v[1]

                if p[vote_agent_id] == "狼":
                    for d in divine_list:
                        divine_agent_id = d[0]
                        divine_target_id = d[1]
                        result = d[2]
                        # 人狼に白出しした(偽物とわかっている)占い師に人狼が投票した場合
                        if result == "白" and divine_target_id == vote_agent_id:

                            self.pattern_score_map[str(p)] *= WEREWOLF_VOTE_FAKE_SEER
                        # 他のプレイヤーに黒出しした(偽物とわかっている)占い師に人狼が投票した場合
                        elif (result == "黒" or result == "狼") and p[
                            divine_target_id] != "狼" and vote_target_id == divine_agent_id:

                            self.pattern_score_map[str(p)] *= WEREWOLF_VOTE_FAKE_SEER

    def update_by_death(self, dead_id_list):
        new_pattern = []

        for p in self.role_pattern:
            flag = False
            for id in dead_id_list:
                if p[id] == "狼":
                    flag = True
            if not flag:
                new_pattern.append(p)
            else:
                self.pattern_score_map[str(p)] *= 0.0

        self.role_pattern = new_pattern

    def update_by_seer_co(self, seer_co_id_list, after_day_one_vote=False):
        for p in self.role_pattern:
            v_co_count = 0
            for id in seer_co_id_list:
                if p[id] == "狼":
                    self.pattern_score_map[str(p)] *= WEREWOLF_CO
                elif p[id] == "狂":
                    self.pattern_score_map[str(p)] *= POSESSED_CO
                elif p[id] == "占":
                    self.pattern_score_map[str(p)] *= SEER_CO
                elif p[id] == "村":
                    self.pattern_score_map[str(p)] *= VILLAGER_CO
                    v_co_count += 1
            if v_co_count >= 2:
                self.pattern_score_map[str(p)] *= TWO_VILLAGER_CO

        # １日目の投票日までに占い師がCOしない場合を考慮
        if after_day_one_vote:
            no_co_id_list = [1,2,3,4,5]
            for id in seer_co_id_list:
                no_co_id_list.remove(id)
            for p in self.role_pattern:
                for id in no_co_id_list:

                    if p[id] == "占":
                        self.pattern_score_map[str(p)] *= SEER_NO_CO

    def get_max_pattern(self):
        max_s = -1
        for r in self.role_pattern:
            s = self.pattern_score_map[str(r)]
            if s > max_s:
                max_s = s
        max_pattern = []
        for r in self.role_pattern:
            if max_s == self.pattern_score_map[str(r)]:
                max_pattern.append(r)
        return max_pattern

    def get_estimated_role(self, exclude_id=None):
        if exclude_id is None:
            exclude_id = -100
        black_id_list = []
        werewolf_id_list = []
        possessed_id_list = []
        seer_id_list = []
        villager_id_list = []
        white_id_list = []
        max_pattern = self.get_max_pattern()
        for i in range(5):
            id = i + 1
            black_count = 0
            werewolf_count = 0
            possessed_count = 0
            seer_count = 0
            villager_count = 0
            white_count = 0
            for p in max_pattern:
                if p[id] == "狼" or p[id] == "狂":
                    black_count += 1
                    if p[id] == "狼":
                        werewolf_count += 1
                    else:
                        possessed_count += 1
                if p[id] == "村" or p[id] == "占":
                    white_count += 1
                    if p[id] == "村":
                        villager_count += 1
                    else:
                        seer_count += 1

            if id != exclude_id:
                if len(max_pattern) == black_count:
                    black_id_list.append(id)
                if len(max_pattern) == werewolf_count:
                    werewolf_id_list.append(id)
                if len(max_pattern) == possessed_count:
                    possessed_id_list.append(id)
                if len(max_pattern) == villager_count:
                    villager_id_list.append(id)
                if len(max_pattern) == seer_count:
                    seer_id_list.append(id)
                if len(max_pattern) == white_count:
                    white_id_list.append(id)

        ret_dic = {"黒": black_id_list, "狼": werewolf_id_list, "狂": possessed_id_list, "占": seer_id_list,
                   "村": villager_id_list, "白": white_id_list}
        return ret_dic
