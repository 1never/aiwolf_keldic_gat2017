#!/usr/bin/env python3
import random
import datetime
import time
import copy
import lib.util
import lib.recognize
import lib.all_pattern
import lib.utterance_generator

class SeerKeldic(object):
    def read_lines(self, filepath):
        data_list = []
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                data_list.append(line)
        return data_list

    def __init__(self, game_info, game_setting):
        # 乱数の設定
        now = datetime.datetime.now()
        random.seed(int(time.mktime(now.timetuple())))

        self.game_info = game_info
        self.game_setting = game_setting
        self.my_id = game_info['agent']
        self.rg = lib.recognize.Recognize("data/")

        # すでに占い師COしたかどうか
        self.seer_co = False

        # 今日の占い結果を発表したかどうか
        self.report_result = False

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

        # すでに占い師COしたかどうか
        self.seer_co = False

        # 今日の占い結果を発表したかどうか
        self.report_result = False

        # 投票先のid (占い先を決定する際使用)
        self.voted_id = -1

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
        self.game_info = game_info
        self.my_id = game_info['agent']
        self.talk_end = False
        self.report_result = False
        self.voted_id = -1
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

        elif self.game_info["day"] <= 1:
            self.my_divine_result_list.append(self.game_info['divineResult'])
            result = (self.my_id, self.game_info['divineResult']['target'], self.game_info['divineResult']['result'])
            if result not in self.divine_list:
                self.divine_list.append(result)
            self.ug.set_data(self.seer_co_list, self.divine_list, None, None, my_id=self.my_id,
                             my_role=lib.util.role_name(self.role))

        elif self.game_info["day"] >= 2:
            self.my_divine_result_list.append(self.game_info['divineResult'])
            result = (self.my_id, self.game_info['divineResult']['target'], self.game_info['divineResult']['result'])
            if result not in self.divine_list:
                self.divine_list.append(result)
            self.ug.set_data(self.seer_co_list, self.divine_list, self.vote_list, self.dead_id_list, my_id=self.my_id,
                             my_role=lib.util.role_name(self.role))

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

        if self.vote_target_id > 0:
            return self.vote_target_id
        else:
            target_ids = copy.copy(self.alive_id_list)
            target_ids.remove(self.my_id)
            random.shuffle(target_ids)
            return target_ids[0]



    def divine(self):
        divine_target_id = self.game_info["aliveAgentList"]
        if self.my_id in divine_target_id:
            divine_target_id.remove(self.my_id)

        target = -1
        #すでに占った占い先は除外
        for result in self.my_divine_result_list:
            if result["target"] in divine_target_id:
                divine_target_id.remove(result["target"])

        if self.dead_id_list is not None:
            for id in self.dead_id_list:
                if id in divine_target_id:
                    divine_target_id.remove(id)
        if self.vote_target_id in divine_target_id:
            divine_target_id.remove(self.vote_target_id)

        if self.ug.rp is None and len(divine_target_id) > 0:
            random.shuffle(divine_target_id)
            target = divine_target_id[0]

        if target > 0:
            return target

        estimated_dic = self.ug.rp.get_estimated_role()
        for id in estimated_dic["狼"]:
            if id in divine_target_id:
                return id
        for id in estimated_dic["狂"]:
            if id in divine_target_id:
                return id
        for id in estimated_dic["黒"]:
            if id in divine_target_id:
                return id

        if len(divine_target_id) == 0:
            return self.my_id


        return divine_target_id[0]

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

                        # 自身がCO済みなら反論コメントを言う
                        if self.seer_co:
                            candidates = self.templates["偽占い師"]["ALL"]
                            random.shuffle(candidates)
                            uttr = candidates[0].replace("《AGENTNAME》", lib.util.agent_name(talk["agent"]))

                # 占い結果報告は判定がゆるいので占い師COしたプレイヤーのみ登録
                elif res[0] == "DIVINED" and talk["agent"] in self.seer_co_list and talk["agent"] != self.my_id:
                    if (talk["agent"], res[1], res[2]) not in self.divine_list:
                        self.divine_list.append((talk["agent"], res[1], res[2]))
                        changed_state = True

        if uttr != "" and uttr is not None:
            return uttr


        #挨拶発話 (0日目)
        if self.game_info["day"] == 0 and len(talk_history) == 0:
            greetings = self.read_lines("data/greeting.txt")
            random.shuffle(greetings)
            return greetings[0]
        elif self.game_info["day"] == 0 and talk_history[0]["turn"] > 5:
            return "Over"

        # 1日目
        elif self.game_info["day"] == 1:
            if not self.seer_co:
                #COして同時に結果を言う

                # CO
                # 候補文を追加
                candidates = self.templates["CO"]["ALL"]
                #対抗が存在する場合
                if len(self.seer_co_list) > 0:
                    candidates.extend(self.templates["CO"]["対抗"])

                random.shuffle(candidates)
                uttr = candidates[0]
                if len(self.seer_co_list) > 0:
                    uttr = uttr.replace("《AGENTNAME》", lib.util.agent_name(self.seer_co_list[0]))


                # 占い結果
                candidates = self.templates["DIVINE"]["ALL"]
                if self.my_divine_result_list[-1]["result"] == "WEREWOLF":
                    candidates.extend(self.templates["DIVINE"]["黒"])
                    iden = "黒"
                else:
                    iden = "白"
                random.shuffle(candidates)
                uttr += candidates[0]
                uttr = uttr.replace("《AGENTNAME》",lib.util.agent_name(self.my_divine_result_list[-1]["target"]))
                uttr = uttr.replace("《IDENTITY》", iden)
                self.seer_co = True
                self.report_result = True
                self.seer_co_list.append(self.my_id)
                self.ug.set_data(self.seer_co_list, self.divine_list, None, None, my_id=self.my_id,
                                 my_role=lib.util.role_name(self.role))
                return uttr
        elif self.game_info["day"] >= 2:
            if not self.report_result:
                candidates = self.templates["DIVINE"]["ALL"]
                if self.my_divine_result_list[-1]["result"] == "WEREWOLF":
                    candidates.extend(self.templates["DIVINE"]["黒"])
                    iden = "黒"
                else:
                    iden = "白"
                random.shuffle(candidates)
                uttr += candidates[0]
                uttr = uttr.replace("《AGENTNAME》", lib.util.agent_name(self.my_divine_result_list[-1]["target"]))
                uttr = uttr.replace("《IDENTITY》", iden)

                self.report_result = True
                self.ug.set_data(self.seer_co_list, self.divine_list, self.vote_list, self.dead_id_list,
                                 my_id=self.my_id,
                                 my_role=lib.util.role_name(self.role))
                return uttr

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

