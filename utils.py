def get_status(data, key, value):
    ret = []
    for elem in data:
        if elem[key] == value:
            ret.append(elem)
    return ret

def get_all_suspects(data):
    get_status(data, "suspect", True)

def get_all_innocents(data):
    get_status(data, "suspect", False)