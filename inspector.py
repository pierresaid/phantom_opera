import socket
import os
import logging
from logging.handlers import RotatingFileHandler
import json
import protocol
import copy
from random import randrange
import random

# Local import
import utils

host = "localhost"
port = 12000
# HEADERSIZE = 10

"""
set up inspector logging
"""
inspector_logger = logging.getLogger()
inspector_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s :: %(levelname)s :: %(message)s", "%H:%M:%S")
# file
if os.path.exists("./logs/inspector.log"):
    os.remove("./logs/inspector.log")
file_handler = RotatingFileHandler('./logs/inspector.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
inspector_logger.addHandler(file_handler)
# stream
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
inspector_logger.addHandler(stream_handler)


class Player():

    def __init__(self):
        self.best_move = None
        self.end = False
        # self.old_question = ""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def connect(self):
        self.socket.connect((host, port))

    def reset(self):
        self.socket.close()

    def answer(self, question):
        # work
        data = question["data"]
        game_state = question["game state"]
        response_index = 0

        # import ipdb; ipdb.set_trace()
        if question['question type'] == "select character":
            self.best_move = utils.find_best_move(game_state, self.heuristic)
            response_index = next((index for (index, d) in enumerate(question['data']) if d["color"] == self.best_move["color"]), None)

        elif question["question type"] == 'activate red power':
            response_index = 1

        # elif question["question type"] == 'activate purple power':
        #     # print("ICIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIii")
        #     # print(question["game state"]["num_tour"])
        #     import ipdb; ipdb.set_trace()
        #     response_index = 1

        if question['question type'] == "activate grey power":
            best_shadow_room = 0
            best_shadow_room_heuristic = -100
            for new_shadow in range(8):
                if new_shadow != game_state["shadow"]:
                    grey_game_state = copy.deepcopy(game_state["characters"])
                    grey_heuristic = self.heuristic(grey_game_state, new_shadow)
                    if grey_heuristic > best_shadow_room_heuristic:
                        best_shadow_room_heuristic = grey_heuristic
                        best_shadow_room = new_shadow
            print(best_shadow_room, best_shadow_room_heuristic)

        elif question['question type'] == "select position":
            response_index = next((index for (index, d) in enumerate(question['data']) if d == self.best_move["pos"]), None)
        # log
        inspector_logger.debug("|\n|")
        inspector_logger.debug("inspector answers")
        inspector_logger.debug(f"question type ----- {question['question type']}")
        inspector_logger.debug(f"data -------------- {data}")
        inspector_logger.debug(f"response index ---- {response_index}")
        inspector_logger.debug(f"response ---------- {data[response_index]}")
        return response_index

    # def find_best_move(self, game_state):
    #     all_possible_game_state = utils.get_all_possible_game_state_objects(game_state)
    #     best_heuristic = -1
    #     for  possible_game_state_object in all_possible_game_state:
    #         possible_game_state = possible_game_state_object["game state"]
    #         heuristic = self.heuristic(possible_game_state, game_state["shadow"])
    #         if heuristic > best_heuristic:
    #             best_heuristic = heuristic
    #             best_move = possible_game_state_object["player"]
    #     return best_move

    def heuristic(self, game_state, shadow):
        screaming_players = []
        # print("lolokofkfoekfeofkeofkeofkeofkoef")
        # print(game_state)
        # p(game_state);
        suspects = utils.get_all_suspects(game_state)
        # p(suspects)
        for character in suspects:
            if utils.get_number_characters_in_pos(game_state, character["position"]) == 1 or \
                    character[
                        "position"] == shadow:
                screaming_players.append(character)
        nbr_screaming = len(screaming_players)
        nbr_not_screaming = len(suspects) - nbr_screaming
        nbr_max = max(nbr_screaming, nbr_not_screaming)
        nbr_min = min(nbr_screaming, nbr_not_screaming)
        heuristic = (nbr_min / nbr_max) * 100
        return heuristic

    def handle_json(self, data):
        data = json.loads(data)
        response = self.answer(data)
        # send back to server
        bytes_data = json.dumps(response).encode("utf-8")
        protocol.send_json(self.socket, bytes_data)

    def run(self):

        self.connect()

        while self.end is not True:
            received_message = protocol.receive_json(self.socket)
            if received_message:
                self.handle_json(received_message)
            else:
                print("no message, finished learning")
                self.end = True

    # def heurisitc(self, game_state, shadow):
    #     scream_list = []
    #     not_scream_list = []
    #     suspects = utils.get_all_suspects(game_state)
    #     for character in suspects:
    #         if utils.get_number_characters_in_pos(game_state, character["position"]) == 1 or \
    #                 character[
    #                     "position"] == shadow:
    #             scream_list.append(character)
    #         else:
    #             not_scream_list.append(character)
    #     print(f"nb suspect", len(suspects), "\n")
    #     print(f"scream {len(scream_list)}\n")
    #     print(f"not scream {len(not_scream_list)}\n")
    #     scream_len = len(scream_list)
    #     not_scream_len = len(not_scream_list)
    #     bigger = max(scream_len, not_scream_len)
    #     smaller = min(scream_len, not_scream_len)
    #     heursitic = (smaller / bigger) * 100
    #     print("\nheuristic: ", heursitic, "\n")
    #     return heursitic


p = Player()

p.run()
