#!/usr/bin/env python3run_auto.sh
import random
import datetime
import time
import lib.util
import lib.recognize
import lib.all_pattern
import lib.utterance_generator

class VillagerKeldic(object):
    def __init__(self, game_info, game_setting):
        # 乱数の設定
        now = datetime.datetime.now()
        random.seed(int(time.mktime(now.timetuple())))

        self.game_info = game_info
        self.game_setting = game_setting
        self.my_id = game_info['agent']
        self.rg = lib.recognize.Recognize("data/")

        # 投票先のid
        self.vote_target_id = -1

        self.alive_id_list = []
        self.dead_id_list = []
        for ids, status in game_info['statusMap'].items():
            if status == "ALIVE":
                self.alive_id_list.append(int(ids))
            else:
                self.dead_id_list.append(int(ids))
        self.my_divine_result_list = []

        #pattern用
        self.seer_co_list = []
        self.divine_list = []
        self.vote_list = []

        self.chat_uttrs = lib.util.read_lines("data/chat.txt")
        self.short_uttrs = lib.util.read_lines("data/chat_short.txt")
        self.templates = lib.util.read_template("data/template.txt")

        self.role = game_info["roleMap"][str(self.my_id)]

        # もう話すことはない場合はTrue
        self.talk_end = False

        self.ug = lib.utterance_generator.UtteranceGenerator("data/role_pattern.json", "data/template.txt")

    def reset(self, game_info):
        #乱数の設定
        now = datetime.datetime.now()
        random.seed(int(time.mktime(now.timetuple())))

        self.my_id = game_info['agent']
        self.rg = lib.recognize.Recognize("data/")

        self.alive_id_list = game_info['aliveAgentList']

        self.my_divine_result_list = []

        #pattern用
        self.seer_co_list = []
        self.divine_list = []
        self.vote_list = []

        self.alive_id_list = []
        self.dead_id_list = []
        for ids, status in game_info['statusMap'].items():
            if status == "ALIVE":
                self.alive_id_list.append(int(ids))
            else:
                self.dead_id_list.append(int(ids))



        self.chat_uttrs = lib.util.read_lines("data/chat.txt")
        self.short_uttrs = lib.util.read_lines("data/chat_short.txt")
        self.templates = lib.util.read_template("data/template.txt")

        self.role = game_info["roleMap"][str(self.my_id)]

        self.ug = lib.utterance_generator.UtteranceGenerator("data/role_pattern.json", "data/template.txt")

    def dayStart(self, game_info):
        self.game_info = lib.util.add_attack_info(game_info, self.alive_id_list)
        self.talk_end = False
        self.vote_target_id = -1
        self.alive_id_list = []
        self.dead_id_list = []
        for ids, status in game_info['statusMap'].items():
            if status == "ALIVE":
                self.alive_id_list.append(int(ids))
            else:
                self.dead_id_list.append(int(ids))

        for res in game_info["voteList"]:
            self.vote_list.append((res["agent"], res["target"]))

        # 初日の場合は初期化
        if self.game_info["day"] == 0:
            self.reset(self.game_info)
        elif self.game_info["day"] == 1:
            self.ug.set_data(self.seer_co_list, self.divine_list, None, None, my_id=self.my_id,
                             my_role=lib.util.role_name(self.role))
        elif self.game_info["day"] >= 2:
            self.ug.set_data(self.seer_co_list, self.divine_list, self.vote_list, self.dead_id_list,
                             my_id=self.my_id,
                             my_role=lib.util.role_name(self.role))
        return None

    def dayFinish(self, talk_history, whisper_history):
        return None

    def finish(self, game_info):
        return None



    def vote(self, talk_history, whisper_history):
        if self.vote_target_id == -1:
            if self.game_info["day"] <= 1:

                self.ug.set_data(self.seer_co_list, self.divine_list, None, None, my_id=self.my_id,
                                 my_role=lib.util.role_name(self.role))
            elif self.game_info["day"] >= 2:
                self.ug.set_data(self.seer_co_list, self.divine_list, self.vote_list, self.dead_id_list,
                                 my_id=self.my_id,
                                 my_role=lib.util.role_name(self.role))
            _, self.vote_target_id = self.ug.generate_vote_uttr(self.game_info["day"])

        return self.vote_target_id



    def talk(self, talk_history, whisper_history):
        # COなどで状況が変わったらTrue
        changed_state = False


        uttr = ""
        for talk in talk_history:
            if talk["agent"] == self.my_id:
                continue

            r_result = self.rg.recognize(talk["text"])

            if len(r_result) == 0:
                continue

            for res in r_result:
                # 占い師COのみ対応
                if res[0] == "CO":
                    if res[1] == "占" and talk["agent"] not in self.seer_co_list:
                        self.seer_co_list.append(talk["agent"])
                        changed_state = True

                # 自分に黒判定を出してきた占い師に反論
                elif res[0] == "DIVINED" and talk["agent"] in self.seer_co_list and res[1] == self.my_id and res[2] == "WEREWOLF":
                    if (talk["agent"], res[1], res[2]) not in self.divine_list:
                        self.divine_list.append((talk["agent"], res[1], res[2]))
                        changed_state = True
                        uttr = lib.util.random_select(self.templates["被黒判定"]["ALL"])
                        uttr = uttr.replace("《AGENTNAME》", lib.util.agent_name(talk["agent"]))

        if uttr != "" and uttr is not None:
            return uttr


        #挨拶発話 (0日目)

        if self.game_info["day"] == 0 and len(talk_history) == 0:
            greetings = lib.util.read_lines("data/greeting.txt")
            random.shuffle(greetings)
            return greetings[0]
        elif self.game_info["day"] == 0 and talk_history[0]["turn"] > 5:
            return "Over"

        elif self.game_info["day"] > 0 and len(talk_history) == 0:
            if self.game_info["attackedAgent"] != self.game_info["executedAgent"] and self.game_info["attackedAgent"] > 0:

                return lib.util.random_select(self.templates["襲撃"]["あり"]).replace("《AGENTNAME》", lib.util.agent_name(self.game_info["attackedAgent"]))


        if changed_state:
            if self.game_info["day"] <= 1:
                self.ug.set_data(self.seer_co_list, self.divine_list, None, None,my_id=self.my_id, my_role=lib.util.role_name(self.role))
            elif self.game_info["day"] >= 2:
                self.ug.set_data(self.seer_co_list, self.divine_list, self.vote_list, self.dead_id_list, my_id=self.my_id,
                                 my_role=lib.util.role_name(self.role))

        uttr = self.ug.generate_estimate_uttr()
        if uttr is None:
            uttr = ""


        if len(uttr) > 0 and uttr is not None:
            return uttr

        if len(talk_history) > 0:
            if talk_history[0]["turn"] > 7 and self.vote_target_id < 0 and self.game_info["day"] >= 1:
                uttr, self.vote_target_id = self.ug.generate_vote_uttr(self.game_info["day"])
                return uttr
        uttr = "Skip"


        # 一定確率で雑談発話
        if random.random() > 0.7:
            random.shuffle(self.chat_uttrs)
            uttr = self.chat_uttrs.pop()
        elif random.random() < 0.2:
            random.shuffle(self.short_uttrs)
            uttr = self.short_uttrs.pop()

        return uttr