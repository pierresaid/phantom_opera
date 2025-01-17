import copy

passages = [{1, 4}, {0, 2}, {1, 3}, {2, 7}, {0, 5, 8},
            {4, 6}, {5, 7}, {3, 6, 9}, {4, 9}, {7, 8}]

pink_passages = [{1, 4}, {0, 2, 5, 7}, {1, 3, 6}, {2, 7}, {0, 5, 8, 9}, {
    4, 6, 1, 8}, {5, 7, 2, 9}, {3, 6, 9, 1}, {4, 9, 5}, {7, 8, 4, 6}]

def answer(self, question, who):
    data = question["data"]
    game_state = question["game state"]
    response_index = 0

    if question['question type'] == "select character":
        self.best_move = find_best_move(game_state, self.heuristic)
        response_index = next((index for (index, d) in enumerate(question['data']) if d["color"] == self.best_move["color"]), None)

    elif question["question type"] == 'activate red power':
        response_index = 1

    elif question["question type"] == 'activate grey power':
        response_index = 1

    elif question["question type"] == 'activate purple power':
        if self.best_move["power"] == True:
            response_index = 1
        else:
            response_index = 0

    elif question["question type"] == 'purple character power':
        response_index = next((index for (index, d) in enumerate(question['data']) if d == self.best_move["swap"]), None)

    elif question['question type'] == "select position":
        response_index = next((index for (index, d) in enumerate(question['data']) if d == self.best_move["pos"]), None)

    elif question['question type'] == "grey character power":
        best_shadow_room = 0
        best_shadow_room_heuristic = -100
        for new_shadow in range(10):
            if new_shadow != game_state["shadow"]:
                grey_game_state = copy.deepcopy(game_state["characters"])
                grey_heuristic = self.heuristic(grey_game_state, new_shadow)
                if grey_heuristic > best_shadow_room_heuristic:
                    best_shadow_room_heuristic = grey_heuristic
                    best_shadow_room = new_shadow
        # p(question)
        # print(best_shadow_room, who)
        response_index = best_shadow_room
        # print(best_shadow_room, best_shadow_room_heuristic)

    return response_index

def get_status(data, key, value):
    ret = []
    for elem in data:
        if elem[key] == value:
            ret.append(elem)
    return ret

def get_all_suspects(data):
    return get_status(data, "suspect", True)

def get_all_innocents(data):
    return get_status(data, "suspect", False)

def get_available_moves(character, game_state):
    character_passages = pink_passages if character["color"] == 'pink' else passages
    if character["color"] != 'purple' or character["power"]:
        disp = {x for x in character_passages[character["position"]]
                if character["position"] not in game_state["blocked"] or x not in game_state["blocked"]}
        available_positions = list(disp)
    return available_positions

def every_player_position(characters, exclude=[]):
    ret = {}
    for character in characters:
        if character["color"] not in exclude:
            ret[character["color"]] = character["position"]
    return ret

def swap_characters(game_state, pl1, pl2):
    idx_pl1 = next((index for (index, d) in enumerate(game_state) if d["color"] == pl1["color"]), None)
    idx_pl2 = next((index for (index, d) in enumerate(game_state) if d["color"] == pl2["color"]), None)
    tmp = copy.deepcopy(game_state[idx_pl1]["position"])
    game_state[idx_pl1]["position"] = game_state[idx_pl2]["position"]
    game_state[idx_pl2]["position"] = tmp
    return game_state

def get_all_possible_game_state_objects(game_state):
    ret = []
    for character in game_state["active tiles"]:
        new_pos = get_available_moves(character, game_state)
        for move in new_pos:
            cp_game_state = copy.deepcopy(game_state["characters"])
            idx = idx_by_c(game_state["characters"], character["color"])
            cp_game_state[idx]["position"] = move
            ret.append({"game state": cp_game_state, "player" : {"color": character["color"],
                                                                "power": False,
                                                                 "pos": move,
                                                                 "shadow": game_state["shadow"]}})
        if character["color"] == "purple":
            purple_idx = idx_by_c(game_state["characters"], "purple")
            for character in game_state["characters"]:
                if character["color"] != "purple" and character["position"] != game_state["characters"][purple_idx]["position"]:
                    idx = idx_by_c(game_state["characters"], character["color"])
                    cp_game_state = copy.deepcopy(game_state)
                    cp_game_state = swap_characters(cp_game_state["characters"], character, game_state["characters"][purple_idx])
                    ret.append({"game state": cp_game_state, "player": {"color": "purple",
                                                                        "power": True,
                                                                        "swap": character["color"],
                                                                        "shadow": game_state["shadow"]}})
    return ret

def idx_by_c(characters, color):
    return next((index for (index, d) in enumerate(characters) if d["color"] == color), None)

def alternatif_game_state(current_game_state, player, new_pos):
    idx = next((index for (index, d) in enumerate(current_game_state["active tiles"]) if d["color"] == player), None)
    current_game_state["active tiles"][idx]["position"] = new_pos
    return current_game_state

def game_over(game_state): # can be optimize
    nb_suspect = 0
    for character in game_state["characters"]:
        if character["suspect"]:
            nb_suspect += 1
    return nb_suspect == 1

def get_number_characters_in_pos(characters, pos):
    nb = 0
    for character in characters:
        if character["position"] == pos:
            nb += 1
    return nb

def find_best_move(game_state, func_ptr_heuristic):
    all_possible_game_state = get_all_possible_game_state_objects(game_state)
    best_heuristic = -100
    for possible_game_state_object in all_possible_game_state:
        possible_game_state = possible_game_state_object["game state"]
        heuristic = func_ptr_heuristic(possible_game_state, possible_game_state_object["player"]["shadow"])
        # heuristic = func_ptr_heuristic(possible_game_state, game_state["shadow"])
        # print("heuristic", heuristic)
        # print("best heuristic", best_heuristic)
        # print("")
        if heuristic > best_heuristic:
            best_heuristic = heuristic
            best_move = possible_game_state_object["player"]
    return best_move


import json

def p(ret):
    print(json.dumps(ret, indent=2))
