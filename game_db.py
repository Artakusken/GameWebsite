import sqlalchemy
import sqlalchemy as sa
import sqlalchemy.orm as orm
import datetime
from sqlalchemy_serializer import SerializerMixin
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


base_engines = {"users": sqlalchemy.create_engine('sqlite:///databases/Users.db?check_same_thread=False'),
                "cards": sqlalchemy.create_engine('sqlite:///databases/Cards.db?check_same_thread=False')}


CardsBase = orm.declarative_base()
UsersBase = orm.declarative_base()
__factory = None


def create_bases():
    CardsBase.metadata.create_all(base_engines["cards"])
    UsersBase.metadata.create_all(base_engines["users"])


def global_init(db_file):
    global __factory
    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    __factory = orm.sessionmaker(binds={CardsBase: base_engines["cards"], UsersBase: base_engines["users"]})

    create_bases()


def create_session() -> orm.Session:
    global __factory
    return __factory()


class User(UsersBase, UserMixin, SerializerMixin):
    __tablename__ = 'Users'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    nickname = sa.Column(sa.String, unique=True, nullable=False)
    email = sa.Column(sa.String, index=True, unique=True, nullable=True)
    hashed_password = sa.Column(sa.String, nullable=True)
    client_id = sa.Column(sa.Integer, default=0)
    game_version = sa.Column(sa.String, default="0.01")
    online = sa.Column(sa.Integer, default=0)
    online_check = sqlalchemy.Column(sqlalchemy.DateTime)
    is_playing = sa.Column(sa.Integer, default=0)
    ready_to_play = sa.Column(sa.Integer, default=0)
    games = sa.Column(sa.Integer, default=0)
    wins = sa.Column(sa.Integer, default=0)
    loses = sa.Column(sa.Integer, default=0)
    draws = sa.Column(sa.Integer, default=0)
    nilfgaard_games = sa.Column(sa.Integer, default=0)
    northern_realms_games = sa.Column(sa.Integer, default=0)
    scoiatael_games = sa.Column(sa.Integer, default=0)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f"<Player> {self.id} {self.nickname}"


class CardsParams(CardsBase, SerializerMixin):
    __tablename__ = "Cards"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    bp = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    armor = sqlalchemy.Column(sqlalchemy.Integer)
    provision = sqlalchemy.Column(sqlalchemy.Integer)
    card_type = sqlalchemy.Column(sqlalchemy.Integer)
    fraction = sqlalchemy.Column(sqlalchemy.String)
    tags = sqlalchemy.Column(sqlalchemy.String)
    deployment = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Methods.id"))
    order = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Methods.id"))
    turn_end = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Methods.id"))
    conditional = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Methods.id"))

    def __init__(self, name, bp, armor, provision, card_type, fraction, deployment, order, turn_end, conditional, *tags):
        self.name = name
        self.bp = bp
        self.armor = armor
        self.provision = provision
        self.card_type = card_type
        self.fraction = fraction
        self.tags = ";".join([i for i in tags])
        self.deployment = deployment
        self.order = order
        self.turn_end = turn_end
        self.conditional = conditional


class Methods(CardsBase, SerializerMixin):
    __tablename__ = "Methods"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    type = sqlalchemy.Column(sqlalchemy.Integer)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)

    def __init__(self, def_name, type):
        self.name = def_name
        self.type = type


class MethodsType(CardsBase, SerializerMixin):
    __tablename__ = "Methods_types"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String)


def clear_db(db_path):
    global_init(db_path)
    session = create_session()
    for i in session.query(User):
        session.delete(i)
    session.commit()


def add_user(nickname, email, hashed_password):
    return User(nickname=nickname, email=email, hashed_password=hashed_password)


def delete_db_elem(db_class, filter_exp, num, session):
    if num == 1:
        session.delete(session.query(db_class).filter(filter_exp).first())
    else:
        for job in session.query(db_class).filter(filter_exp).all():
            session.delete(job)
    session.commit()

