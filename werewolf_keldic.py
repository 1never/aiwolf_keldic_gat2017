#!/usr/bin/env python3
import lib.util
import lib.recognize
import lib.all_pattern
import lib.utterance_generator
from villager_keldic import VillagerKeldic


class WerewolfKeldic(object):

    def __init__(self, game_info, game_setting):
        self.villager_keldic = VillagerKeldic(game_info, game_setting)
        self.my_id = game_info['agent']
        self.vote_id = -1

    def dayStart(self, game_info):
        self.vote_id = -1
        if game_info["day"] == 0:
            self.my_id = game_info['agent']

        self.villager_keldic.dayStart(game_info)
        return None

    def dayFinish(self, talk_history, whisper_history):
        self.villager_keldic.dayFinish(talk_history, whisper_history)
        return None

    def finish(self, game_info):
        self.villager_keldic.finish(game_info)
        return None

    def vote(self, talk_history, whisper_history):
        if self.villager_keldic.game_info["day"] == 1:
            return self.villager_keldic.vote(talk_history, whisper_history)
        #2日目以降は白に投票
        else:
            self.villager_keldic.ug.set_data(self.villager_keldic.seer_co_list, self.villager_keldic.divine_list,
                                         self.villager_keldic.vote_list, self.villager_keldic.dead_id_list,
                                         my_id=self.my_id, my_role="狼")
            estimated_dic = self.villager_keldic.ug.rp.get_estimated_role(exclude_id=self.my_id)
            for id in self.villager_keldic.alive_id_list:
                if id in estimated_dic["白"]:
                    self.vote_id = estimated_dic["白"][0]
                    return self.vote_id
            #白がいなかったら黒以外に投票
            for id in self.villager_keldic.alive_id_list:
                if id not in estimated_dic["黒"] and len(estimated_dic["黒"]) > 0:
                    self.vote_id = estimated_dic["黒"][0]
                    return self.vote_id
            #それでもいなかったらランダム
            if self.my_id in self.villager_keldic.alive_id_list:
                self.villager_keldic.alive_id_list.remove(self.my_id)
            for id in self.villager_keldic.dead_id_list:
                if id in self.villager_keldic.alive_id_list:
                    self.villager_keldic.alive_id_list.remove(id)
            self.vote_id = lib.util.random_select(self.villager_keldic.alive_id_list)
            return self.vote_id




    def talk(self, talk_history, whisper_history):
        return self.villager_keldic.talk(talk_history, whisper_history)

    def attack(self):
        self.villager_keldic.ug.set_data(self.villager_keldic.seer_co_list, self.villager_keldic.divine_list,
                                         self.villager_keldic.vote_list, self.villager_keldic.dead_id_list,
                                         my_id=self.my_id, my_role="狼")
        estimated_dic = self.villager_keldic.ug.rp.get_estimated_role(exclude_id=self.vote_id)
        for id in self.villager_keldic.alive_id_list:
            if id in estimated_dic["白"]:
                return estimated_dic["白"][0]
        # 白がいなかったら黒以外に投票
        for id in self.villager_keldic.alive_id_list:
            if id not in estimated_dic["黒"] and len(estimated_dic["黒"]) > 0:
                return estimated_dic["黒"][0]

        # それでもいなかったらランダム
        if self.my_id in self.villager_keldic.alive_id_list:
            self.villager_keldic.alive_id_list.remove(self.my_id)
        for id in self.villager_keldic.dead_id_list:
            if id in self.villager_keldic.alive_id_list:
                self.villager_keldic.alive_id_list.remove(id)
        return lib.util.random_select(self.villager_keldic.alive_id_list)

