from flask import jsonify
from flask_restful import Resource

from game_db import *


def card_params_list(params, ses):
    name = params.name
    bp = params.bp
    armor = params.armor
    provision = params.provision
    card_type = params.card_type
    fraction = params.fraction
    tags = params.tags
    if ses.query(Methods).filter(Methods.id == params.deployment).first():
        deployment = ses.query(Methods).filter(Methods.id == params.deployment).first().name
    else:
        deployment = None
    if ses.query(Methods).filter(Methods.id == params.order).first():
        order = ses.query(Methods).filter(Methods.id == params.order).first().name
    else:
        order = None
    if ses.query(Methods).filter(Methods.id == params.turn_end).first():
        turn_end = ses.query(Methods).filter(Methods.id == params.turn_end).first().name
    else:
        turn_end = None
    if ses.query(Methods).filter(Methods.id == params.conditional).first():
        conditional = ses.query(Methods).filter(Methods.id == params.conditional).first().name
    else:
        conditional = None
    return [name, bp, armor, provision, card_type, fraction, deployment, order, turn_end, conditional, tags]


class DeckResource(Resource):
    def create_deck(self, cards_ids):
        global_init("cards")
        session = create_session()
        cards = []
        for card_id in [int(i) for i in cards_ids.split(";")]:
            params = session.query(CardsParams).filter(CardsParams.id == card_id).first()
            cards.append(card_params_list(params, session))
        return cards

    def get(self, deck_cards):
        return jsonify(self.create_deck(deck_cards))


class CardsResource(Resource):
    def get_all_cards(self):
        global_init("cards")
        session = create_session()
        cards = {}
        for params in session.query(CardsParams).all():
            cards[params.name] = card_params_list(params, session)
        return cards

    def get(self):
        return jsonify(self.get_all_cards())


class PlayerResource(Resource):
    game_version = None

    def get(self, email, password, cid, conn_type):
        global_init("users")
        session = create_session()
        if conn_type == "in_email":
            player = session.query(User).filter(User.email == email).first()
        elif conn_type == "in_cid":
            player = session.query(User).filter(User.client_id == int(cid)).first()
        if player:
            if player.game_version != self.game_version:
                return jsonify(f"Версия игры должна быть {self.game_version}. Ваша {player.game_version}")
            if conn_type == "in_cid":
                player.online = 1
                session.commit()
                return jsonify([player.id, player.nickname, player.client_id])
            if player.check_password(password):
                if conn_type == "in_email":
                    player.online = 1
                    session.commit()
                    return jsonify([player.id, player.nickname, player.client_id])
                elif conn_type == "out":
                    player.online = 0
                    session.commit()
                    return
            return jsonify("Неверный пароль")
        return jsonify("Игрока с данной почтой не существует")
