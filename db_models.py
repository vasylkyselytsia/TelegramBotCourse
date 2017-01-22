import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.sqlite import INTEGER, VARCHAR
from sqlalchemy import Sequence

Base = declarative_base()


class BotUser(Base):
    __tablename__ = 'bot_users'
    id = sqlalchemy.Column(INTEGER, Sequence('bot_users_id_seq'), primary_key=True)
    chat_id = sqlalchemy.Column(INTEGER, unique=True)
    longitude = sqlalchemy.Column(VARCHAR(20))
    latitude = sqlalchemy.Column(VARCHAR(20))
    user_name = sqlalchemy.Column(VARCHAR(250))

    def __repr__(self):
        return "<User(fullname='%s'>)" % self.user_name
