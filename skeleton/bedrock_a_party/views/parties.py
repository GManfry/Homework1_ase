from flakon import JsonBlueprint
from flask import abort, json, jsonify, request

from bedrock_a_party.classes.party import CannotPartyAloneError, ItemAlreadyInsertedByUser, NotExistingFoodError, NotInvitedGuestError, Party

parties = JsonBlueprint('parties', __name__)

_LOADED_PARTIES = {}  # dict of available parties
_PARTY_NUMBER = 0  # index of the last created party



# TODO: complete the decoration
@parties.route("/parties",methods = ['POST', 'GET'])
def all_parties():
    result = None
    if request.method == 'POST':
        try:
            result = create_party(request) 
        except CannotPartyAloneError:
            abort(400)              

    elif request.method == 'GET':
        result = get_all_parties()        

    return result


# TODO: complete the decoration
@parties.route("/parties/loaded",methods = ['GET'])
def loaded_parties():
    result = 0
    if 'GET' == request.method:
        for i in _LOADED_PARTIES:
            result = result + 1

    return  jsonify({'loaded_parties': result})
    # TODO: returns the number of parties currently loaded in the system


# TODO: complete the decoration
@parties.route("/party/<id>",methods = ['GET', 'DELETE'])
def single_party(id):
    global _LOADED_PARTIES
    result = ""

    # TODO: check if the party is an existing one
    exists_party(id) 

    if 'GET' == request.method:
        result = jsonify(Party.serialize(_LOADED_PARTIES[id]))
        # TODO: retrieve a party
        
    elif 'DELETE' == request.method:
        del _LOADED_PARTIES[id]
        # TODO: delete a party

    return result


# TODO: complete the decoration
@parties.route("/party/<id>/foodlist",methods = ['GET'])
def get_foodlist(id):
    global _LOADED_PARTIES
    result = ""

    # TODO: check if the party is an existing one
    exists_party(id) 

    if 'GET' == request.method:
        result = Party.get_food_list(_LOADED_PARTIES[id])
        result = jsonify({'foodlist':result.serialize()})
        # TODO: retrieve food-list of the party

    return result


# TODO: complete the decoration
@parties.route("/party/<id>/foodlist/<user>/<item>",methods = ['POST', 'DELETE'])
def edit_foodlist(id, user, item):
    global _LOADED_PARTIES

    # TODO: check if the party is an existing one
    exists_party(id) 
    # TODO: retrieve the party
    my_party = _LOADED_PARTIES[id]
    result = ""

    if 'POST' == request.method:
        try:
            result = Party.add_to_food_list(my_party, item, user)
            result = jsonify({'food':result.food, 'user':result.user})
        
        except ItemAlreadyInsertedByUser:
            abort(400)     
        except NotInvitedGuestError :
            abort(401)       
                            
        #result = jsonify({'food':item, 'user':user})
        # TODO: add item to food-list handling NotInvitedGuestError (401) and ItemAlreadyInsertedByUser (400)
     
    if 'DELETE' == request.method:
        try:
            my_party.remove_from_food_list(item,user)
            result = jsonify({'msg': "Food deleted!"})
        except NotExistingFoodError:
            abort(400)
        # TODO: delete item to food-list handling NotExistingFoodError (400)

    return result

#
# These are utility functions. Use them, DON'T CHANGE THEM!!
#

def create_party(req):
    global _LOADED_PARTIES, _PARTY_NUMBER

    # get data from request
    json_data = req.get_json()

    # list of guests
    try:
        guests = json_data['guests']
    except:
        raise CannotPartyAloneError("you cannot party alone!")

    # add party to the loaded parties lists
    _LOADED_PARTIES[str(_PARTY_NUMBER)] = Party(_PARTY_NUMBER, guests)
    _PARTY_NUMBER += 1

    return jsonify({'party_number': _PARTY_NUMBER - 1})


def get_all_parties():
    global _LOADED_PARTIES

    return jsonify(loaded_parties=[party.serialize() for party in _LOADED_PARTIES.values()])


def exists_party(_id):
    global _PARTY_NUMBER
    global _LOADED_PARTIES

    if int(_id) > _PARTY_NUMBER:
        abort(404)  # error 404: Not Found, i.e. wrong URL, resource does not exist
    elif not(_id in _LOADED_PARTIES):
        abort(410)  # error 410: Gone, i.e. it existed but it's not there anymore
