#!/usr/bin/env python3
import random

def read_lines(filepath):
    data_list = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            data_list.append(line)
    return data_list

def read_template(filepath):
    template = {}
    template["CO"] = {"ALL":[], "対抗":[]}
    template["DIVINE"] = {"ALL": [], "黒": []}
    template["偽占い師"] = {"ALL": []}
    template["推定"] = {"白": [], "黒": [], "占": [], "狂": [], "狼": [], "UNK": []}
    template["投票"] = {"ALL": [], "黒": [], "狂": [], "狼": [], "UNK": []}
    template["被黒判定"] = {"ALL": []}
    template["襲撃"] = {"あり": [], "なし": []}
    with open(filepath) as f:
        for line in f:
            line = line.strip()

            splitted = line.split(",")
            if len(splitted) > 2:
                template[splitted[0]][splitted[1]].append(splitted[2])
    return template

def agent_name(id):
    if id < 10:
        return "Agent[0" + str(id) + "]"
    else:
        return "Agent[" + str(id) + "]"

def random_select(list):
    random.shuffle(list)
    return list[0]

def role_name(role):
    role_dic ={"SEER":"占", "VILLAGER":"村", "POSSESSED":"狂", "WEREWOLF":"狼"}
    if role in role_dic:
        return role_dic[role]
    return role

def add_attack_info(game_info, prev_alive_id_list):
    if game_info["day"] <= 1:
        return game_info

    new_dead_id_list = []
    for aid in prev_alive_id_list:
        if aid not in game_info["aliveAgentList"]:
            new_dead_id_list.append(aid)

    if len(new_dead_id_list) == 0:
        return game_info

    if game_info["executedAgent"] in new_dead_id_list:
        new_dead_id_list.remove(game_info["executedAgent"])
    if len(new_dead_id_list) > 0:
        game_info["attackedAgent"] = new_dead_id_list[0]
    return game_info


