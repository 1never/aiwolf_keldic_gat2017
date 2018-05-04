#!/usr/bin/env python3
import aiwolfpy
from villager_keldic import VillagerKeldic
from possessed_keldic import PossessedKeldic
from seer_keldic import SeerKeldic
from werewolf_keldic import WerewolfKeldic


class Keldic(object):
    def __init__(self, agent_name):
        self.agent_name = agent_name
        pass

    def initialize(self, game_info, game_setting):
        self.agentIdx = game_info['agent']
        self.game_setting = game_setting
        self.game_info = game_info

        alive_agents = []
        my_agent_list = []
        for idx, status in self.game_info["statusMap"].items():
            if status == "ALIVE":
                alive_agents.append(int(idx))
            my_agent_list.append(int(idx))

        self.game_info["aliveAgentList"] = alive_agents
        self.game_info["myAgentList"] = my_agent_list

        self.role = game_info["roleMap"][str(self.agentIdx)]
        if self.role == "VILLAGER":
            self.agent = VillagerKeldic(game_info, game_setting)
        elif self.role == "SEER":
            self.agent = SeerKeldic(game_info, game_setting)
        elif self.role == "POSSESSED":
            self.agent = PossessedKeldic(game_info, game_setting)
        elif self.role == "WEREWOLF":
            self.agent = WerewolfKeldic(game_info, game_setting)

    def _print_talk(self, talk_history):
        for t in talk_history:
            print("Turn{} Agent[0{}] : {}".format(t["turn"], t["agent"], t["text"]))

    def getName(self):
        return self.agent_name

    def dayStart(self):
        if self.game_info["day"] == 0:
            self.reset()

        alive_agents = []
        my_agent_list = []
        for idx, status in self.game_info["statusMap"].items():
            if status == "ALIVE":
                alive_agents.append(int(idx))
            my_agent_list.append(int(idx))

        self.game_info["aliveAgentList"] = alive_agents
        self.game_info["myAgentList"] = my_agent_list

        self.agent.dayStart(self.game_info)
        return None

def update(self, game_info, talk_history, whisper_history, request=None):
        self.game_info = game_info
        self.talk_history = talk_history
        self.whisper_history = whisper_history
        #self._print_talk(talk_history)
        pass

    def finish(self):
        self.agent.finish(self.game_info)
        return None

    def vote(self):
        return self.agent.vote(self.talk_history, self.whisper_history)

    def attack(self):
        return self.agent.attack()

    def divine(self):
        return self.agent.divine()

    def talk(self):
        return self.agent.talk(self.talk_history, self.whisper_history)

    def reset(self):
        self.agentIdx = self.game_info['agent']
        self.role = self.game_info["roleMap"][str(self.agentIdx)]

        alive_agents = []
        my_agent_list = []
        for idx, status in self.game_info["statusMap"].items():
            if status == "ALIVE":
                alive_agents.append(int(idx))
            my_agent_list.append(int(idx))

        self.game_info["aliveAgentList"] = alive_agents
        self.game_info["myAgentList"] = my_agent_list

        if self.role == "VILLAGER":
            self.agent = VillagerKeldic(self.game_info, self.game_setting)
        elif self.role == "SEER":
            self.agent = SeerKeldic(self.game_info, self.game_setting)
        elif self.role == "POSSESSED":
            self.agent = PossessedKeldic(self.game_info, self.game_setting)
        elif self.role == "WEREWOLF":
            self.agent = WerewolfKeldic(self.game_info, self.game_setting)


agent = Keldic("KELDIC")
# run
if __name__ == '__main__':
    aiwolfpy.connect(agent)
