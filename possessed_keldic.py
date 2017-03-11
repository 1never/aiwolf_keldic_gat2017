#!/usr/bin/env python3
import random
import lib.util
import lib.recognize
import lib.all_pattern
import lib.utterance_generator
from seer_keldic import  SeerKeldic


class PossessedKeldic(object):

    def __init__(self, game_info, game_setting):
        self.seer_keldic = SeerKeldic(game_info, game_setting)
        self.my_id = game_info['agent']
        self.game_setting = game_setting


        self.fake_divine_target_id = [1,2,3,4,5]
        self.fake_divine_target_id.remove(self.my_id)
        self.fake_divined_werewolf = False

    def reset(self, game_info, game_setting):
        self.seer_keldic = SeerKeldic(game_info, game_setting)
        self.my_id = game_info['agent']
        self.game_setting = game_setting


        self.fake_divine_target_id = [1,2,3,4,5]
        self.fake_divine_target_id.remove(self.my_id)
        self.fake_divined_werewolf = False


    def dayStart(self, game_info):
        if game_info["day"] == 0:
            self.my_id = game_info['agent']
            self.fake_divine_target_id = [1, 2, 3, 4, 5]
            self.fake_divine_target_id.remove(self.my_id)
            self.fake_divined_werewolf = False
            self.reset(game_info, self.game_setting)

        elif game_info["day"] == 1:
            game_info['divineResult'] = {}
            game_info['divineResult']['target'] = lib.util.random_select(self.fake_divine_target_id)
            if random.random() > 0.75:
                game_info['divineResult']["result"] = "WEREWOLF"
                self.fake_divined_werewolf = True
            else:
                game_info['divineResult']["result"] = "HUMAN"

        elif game_info["day"] >= 2:
            game_info['divineResult'] = {}
            game_info = lib.util.add_attack_info(game_info, self.seer_keldic.alive_id_list)
            if game_info["executedAgent"] > 0:
                self.fake_divine_target_id.remove(game_info["executedAgent"])
                game_info['divineResult']['target'] = lib.util.random_select(self.fake_divine_target_id)
                if self.fake_divined_werewolf:
                    game_info['divineResult']["result"] = "HUMAN"
                else:
                    if random.random() > 0.75:
                        game_info['divineResult']["result"] = "WEREWOLF"
                        self.fake_divined_werewolf = True
                    else:
                        game_info['divineResult']["result"] = "HUMAN"

        self.seer_keldic.dayStart(game_info)
        return None

    def dayFinish(self, talk_history, whisper_history):
        self.seer_keldic.dayFinish(talk_history, whisper_history)
        return None

    def finish(self, game_info):
        self.seer_keldic.finish(game_info)

        return None

    def vote(self, talk_history, whisper_history):
        if self.seer_keldic.game_info["day"] == 1:
            return self.seer_keldic.vote(talk_history, whisper_history)
        #2日目以降は白に投票
        else:
            self.seer_keldic.ug.set_data(self.seer_keldic.seer_co_list, self.seer_keldic.divine_list,
                                         self.seer_keldic.vote_list, self.seer_keldic.dead_id_list,
                                         my_id=self.my_id, my_role="狂")
            estimated_dic = self.seer_keldic.ug.rp.get_estimated_role(exclude_id=self.my_id)
            for id in self.seer_keldic.alive_id_list:
                if id in estimated_dic["白"]:
                    return id
            #白がいなかったら人狼以外に投票
            for id in self.seer_keldic.alive_id_list:
                if id not in estimated_dic["黒"] and len(estimated_dic["黒"]) > 0:
                    return id
            #それでもいなかったらランダム
            if self.my_id in self.seer_keldic.alive_id_list:
                self.seer_keldic.alive_id_list.remove(self.my_id)
            return lib.util.random_select(self.seer_keldic.alive_id_list)

    def talk(self, talk_history, whisper_history):
        return self.seer_keldic.talk(talk_history, whisper_history)

