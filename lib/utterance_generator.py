#!/usr/bin/env python3
import random
import lib.all_pattern
import lib.util


class UtteranceGenerator:
    def __init__(self, role_patteern_file, template_file):
        self.role_pattern_file = role_patteern_file
        self.template_file = template_file
        self.template = lib.util.read_template(template_file)
        self.dead_id_list = None

        self.rp = None
        self.estimated_map = None
        self.alive_id_list = [1,2,3,4,5]

    def reset(self):
        self.rp = lib.all_pattern.RolePattern(self.role_pattern_file)
        self.template = lib.util.read_template(self.template_file)

    def set_data(self, seer_co_id_list, divine_list, vote_list=None, dead_id_list=None, my_id=None, my_role=None):
        self.rp = lib.all_pattern.RolePattern(self.role_pattern_file)
        self.my_id = my_id
        self.dead_id_list = dead_id_list
        self.vote_list = vote_list

        if vote_list is None and dead_id_list is None:
            self.rp.day_one_update(seer_co_id_list, divine_list, my_id=my_id, my_role=my_role)
        else:
            self.rp.day_two_update(seer_co_id_list, divine_list, vote_list, dead_id_list, my_id=5, my_role="村")
        self.estimated_map = self.rp.get_estimated_role(my_id)

        if dead_id_list is not None:
            for id in dead_id_list:
                if id in self.alive_id_list:
                    self.alive_id_list.remove(id)

    def generate_estimate_uttr(self):
        if self.estimated_map is None:
            return None
        roles = ["占", "村", "狂", "狼"]
        random.shuffle(roles)
        roles += ["黒", "白"]
        uttr = None
        target_id = 0
        for r in roles:
            if len(self.estimated_map[r]) > 0 and r in self.template["推定"]:
                target_id = self.estimated_map[r].pop()
                if target_id not in self.alive_id_list:
                    continue
                random.shuffle(self.template["推定"][r])
                if len(self.template["推定"][r]) == 0:
                    return None
                t = self.template["推定"][r].pop()
                uttr = t.replace("《AGENTNAME》", "Agent[0" + str(target_id) + "]")
                break
        for r in roles:
            if target_id in self.estimated_map[r]:
                self.estimated_map[r].remove(target_id)

        return uttr

    def generate_vote_uttr(self, day):
        role_dic = self.rp.get_estimated_role(exclude_id=self.my_id)
        uttr_list = []
        if len(role_dic["狼"]) != 0:
            target_id = role_dic["狼"][0]
            uttr_list.extend(self.template["投票"]["狼"])
        elif len(role_dic["狂"]) != 0 and day == 1:
            target_id = role_dic["狂"][0]
            uttr_list.extend(self.template["投票"]["狂"])
        elif len(role_dic["黒"]) != 0:
            target_id = role_dic["黒"][0]
            if day == 1:
                uttr_list.extend(self.template["投票"]["黒"])

        else:
            all_id = [1, 2, 3, 4, 5]
            all_id.remove(self.my_id)
            if self.dead_id_list is not None:
                for id in self.dead_id_list:
                    all_id.remove(id)
            target_id = all_id[0]

        uttr_list.extend(self.template["投票"]["ALL"])
        random.shuffle(uttr_list)
        t = uttr_list.pop()
        uttr = t.replace("《AGENTNAME》", "Agent[0" + str(target_id) + "]")
        return uttr, target_id
