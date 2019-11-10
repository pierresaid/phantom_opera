import copy

passages = [{1, 4}, {0, 2}, {1, 3}, {2, 7}, {0, 5, 8},
            {4, 6}, {5, 7}, {3, 6, 9}, {4, 9}, {7, 8}]

pink_passages = [{1, 4}, {0, 2, 5, 7}, {1, 3, 6}, {2, 7}, {0, 5, 8, 9}, {
    4, 6, 1, 8}, {5, 7, 2, 9}, {3, 6, 9, 1}, {4, 9, 5}, {7, 8, 4, 6}]

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

def get_available_moves(character, blocked):
    character_passages = pink_passages if character["color"] == 'pink' else passages
    if character["color"] != 'purple' or character["power"]:
        disp = {x for x in character_passages[character["position"]]
                if character["position"] not in blocked or x not in blocked}
        available_positions = list(disp)
    return available_positions

def get_all_possible_game_state_objects(game_state):
    ret = []
    for character in game_state["active tiles"]:
        new_pos = get_available_moves(character, game_state["blocked"])
        for move in new_pos:
            cp_game_state = copy.deepcopy(game_state["characters"])
            idx = next((index for (index, d) in enumerate(cp_game_state) if d["color"] == character["color"]), None)
            cp_game_state[idx]["position"] = move
            ret.append({"game state": cp_game_state, "player" : {"color": character["color"], "pos": move}})
    return ret

def alternatif_game_state(current_game_state, player, new_pos):
    #print(current_game_state, player, new_pos)
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
    # best_heuristic = -1
    best_heuristic = -100
    for possible_game_state_object in all_possible_game_state:
        possible_game_state = possible_game_state_object["game state"]
        heuristic = func_ptr_heuristic(possible_game_state, game_state["shadow"])
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
