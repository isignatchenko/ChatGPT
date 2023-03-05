from sqlalchemy import create_engine, exists, PickleType
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///db_content.sqlite', echo=True)
# engine = create_engine('postgresql://gen_user:440Herz440@188.225.24.153:5432/default_db', echo=True)

base = declarative_base()


class Messages(base):
    __tablename__ = 'messages'

    chat_id = Column(Integer, primary_key=True)
    messages = Column(MutableList.as_mutable(PickleType), default=[])
    total_tokens = Column(Integer)

    def __init__(self, chat_id, messages, total_tokens):
        self.chat_id = chat_id
        self.messages = messages
        self.total_tokens = total_tokens


def create_db_content():
    base.metadata.create_all(engine)


def chat_id_exists(chat_id):
    Session = sessionmaker(bind=engine)
    session = Session()
    user_exists = session.query(exists().where(Messages.chat_id == chat_id)).scalar()
    session.commit()
    return user_exists


def create_messages(chat_id, request_text):
    start_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": request_text}
    ]
    add = Messages(chat_id, start_messages, 0)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add(add)
    session.commit()


def get_messages(chat_id):
    Session = sessionmaker(bind=engine)
    session = Session()
    result = session.query(Messages.messages).filter(Messages.chat_id == chat_id).one()
    session.commit()
    return result[0]


def get_total_tokens(chat_id):
    Session = sessionmaker(bind=engine)
    session = Session()
    result = session.query(Messages.total_tokens).filter(Messages.chat_id == chat_id).one()
    session.commit()
    return result[0]


def update_total_tokens(chat_id, total_tokens):
    Session = sessionmaker(bind=engine)
    session = Session()
    session.query(Messages).filter(Messages.chat_id == chat_id).update({Messages.total_tokens: total_tokens})
    session.commit()


def update_messages(chat_id, role, text):
    current_dict = get_messages(chat_id)
    dict_to_append = {"role": role, "content": text}
    current_dict.append(dict_to_append)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.query(Messages).filter(Messages.chat_id == chat_id).update({Messages.messages: current_dict})
    session.commit()


def count_messages_text_len(chat_id):
    Session = sessionmaker(bind=engine)
    session = Session()
    result = session.query(Messages.messages).filter(Messages.chat_id == chat_id).one()
    session.commit()
    counter = 0
    for i in result[0]:
        counter += len(i["content"])
    return counter


def delete_record(chat_id):
    Session = sessionmaker(bind=engine)
    session = Session()
    session.query(Messages).filter(Messages.chat_id == chat_id).delete()
    session.commit()
