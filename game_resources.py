from flask import jsonify
from flask_restful import Resource

from game_db import *


class DeckResource(Resource):
    def create_deck(self, cards_ids):
        global_init("cards")
        session = create_session()
        cards = []
        for card_id in [int(i) for i in cards_ids.split(";")]:
            params = session.query(CardsParams).filter(CardsParams.id == card_id).first()
            name = params.name
            bp = params.bp
            armor = params.armor
            provision = params.provision
            card_type = params.card_type
            fraction = params.fraction
            tags = params.tags
            if session.query(Methods).filter(Methods.id == params.deployment).first():
                deployment = session.query(Methods).filter(Methods.id == params.deployment).first().name
            else:
                deployment = None
            if session.query(Methods).filter(Methods.id == params.order).first():
                order = session.query(Methods).filter(Methods.id == params.order).first().name
            else:
                order = None
            if session.query(Methods).filter(Methods.id == params.turn_end).first():
                turn_end = session.query(Methods).filter(Methods.id == params.turn_end).first().name
            else:
                turn_end = None
            if session.query(Methods).filter(Methods.id == params.conditional).first():
                conditional = session.query(Methods).filter(Methods.id == params.conditional).first().name
            else:
                conditional = None
            cards.append([name, bp, armor, provision, card_type, fraction, deployment, order, turn_end, conditional, tags])
        return cards

    def get(self, deck_cards):
        return jsonify(self.create_deck(deck_cards))


class CardsResource(Resource):
    def get_all_cards(self):
        global_init("cards")
        session = create_session()
        cards = {}
        for params in session.query(CardsParams).all():
            # params = session.query(CardsParams).filter(CardsParams.id == card_id).first()
            name = params.name
            bp = params.bp
            armor = params.armor
            provision = params.provision
            card_type = params.card_type
            fraction = params.fraction
            tags = params.tags
            if session.query(Methods).filter(Methods.id == params.deployment).first():
                deployment = session.query(Methods).filter(Methods.id == params.deployment).first().name
            else:
                deployment = None
            if session.query(Methods).filter(Methods.id == params.order).first():
                order = session.query(Methods).filter(Methods.id == params.order).first().name
            else:
                order = None
            if session.query(Methods).filter(Methods.id == params.turn_end).first():
                turn_end = session.query(Methods).filter(Methods.id == params.turn_end).first().name
            else:
                turn_end = None
            if session.query(Methods).filter(Methods.id == params.conditional).first():
                conditional = session.query(Methods).filter(Methods.id == params.conditional).first().name
            else:
                conditional = None
            cards[name] = [name, bp, armor, provision, card_type, fraction, deployment, order, turn_end, conditional, tags]
        return cards

    def get(self):
        return jsonify(self.get_all_cards())


class PlayerResource(Resource):
    def get(self, email, password):
        global_init("users")
        session = create_session()
        player = session.query(User).filter(User.email == email).first()
        if player:
            if player.game_version != "0.01":
                return jsonify(f"Версия игры должна быть 0.01. Ваша {player.game_version}")
            if player.check_password(password):
                if player.online == 0:
                    player.online = 1
                    session.commit()
                    return jsonify([player.id, player.nickname])
                else:
                    player.online = 0
                    session.commit()
                    return
            return jsonify("Неверный пароль")
        return jsonify("Игрока с данной почтой не существует")
