from sqlalchemy import create_engine, exists
from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import *

# engine = create_engine('sqlite:///db_users.sqlite', echo=True)
engine = create_engine('postgresql://gen_user:440Herz440@188.225.24.153:5432/default_db', echo=True)

base = declarative_base()


class User(base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    balance = Column(Integer)
    model = Column(String)
    temperature = Column(Float)
    max_tokens = Column(Integer)
    top_p = Column(Float)
    frequency_penalty = Column(Float)
    presence_penalty = Column(Float)
    action = Column(String)

    def __init__(self, user_id, username, balance, model, temperature, max_tokens, top_p,
                 frequency_penalty, presence_penalty, action):
        self.user_id = user_id
        self.username = username
        self.balance = balance
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.action = action


def create_db_users():
    base.metadata.create_all(engine)


def create_user(user_id, username):
    balance = start_balance
    model = start_model
    temperature = start_temperature
    max_tokens = start_max_tokens
    top_p = start_top_p
    frequency_penalty = start_frequency_penalty
    presence_penalty = start_presence_penalty
    action = "no"
    add = User(user_id, username, balance, model, temperature, max_tokens, top_p, frequency_penalty, presence_penalty,
               action)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add(add)
    session.commit()


def user_exists(user_id):
    Session = sessionmaker(bind=engine)
    session = Session()
    if_exists = session.query(exists().where(User.user_id == user_id)).scalar()
    session.commit()
    return if_exists


def get_from_user(user_id, what_to_get):
    Session = sessionmaker(bind=engine)
    session = Session()
    result = session.query(User).filter(User.user_id == user_id).one()
    session.commit()
    return getattr(result, what_to_get)


def update_user(user_id, what_to_update, how_to_update):
    Session = sessionmaker(bind=engine)
    session = Session()
    session.query(User).filter(User.user_id == user_id).update({what_to_update: how_to_update})
    session.commit()


def decrease_users_balance(user_id, amount):
    balance = get_from_user(user_id, "balance")
    new_balance = balance - int(amount)
    update_user(user_id, "balance", new_balance)
    return True


def increase_users_balance(user_id, amount):
    balance = get_from_user(user_id, "balance")
    new_balance = balance + int(amount)
    update_user(user_id, "balance", new_balance)
    return True
