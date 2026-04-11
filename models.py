from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    email = Column(String)
    polls = relationship("Poll", back_populates="creator")
    votes_cast = relationship("Vote", back_populates="voter")

class Poll(Base):
    __tablename__ = "poll"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    category = Column(String)
    location = Column(String)
    privacy = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("user.id"))
    creator = relationship("User", back_populates="polls")
    options = relationship("Option", back_populates="poll")
    votes = relationship("Vote", back_populates="poll")

class Option(Base):
    __tablename__ = "option"
    id = Column(Integer, primary_key=True)
    optionname = Column(String)
    votes_total = Column(Integer, default=0)
    poll_id = Column(Integer, ForeignKey("poll.id"))
    poll = relationship("Poll", back_populates="options")
    votes = relationship("Vote", back_populates="option")

class Vote(Base):
    __tablename__ = "vote"
    id = Column(Integer, primary_key=True)
    poll_id = Column(Integer, ForeignKey("poll.id"))
    option_id = Column(Integer, ForeignKey("option.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    poll = relationship("Poll", back_populates="votes")
    option = relationship("Option", back_populates="votes")
    voter = relationship("User", back_populates="votes_cast")

engine = create_engine("sqlite:///polls.db")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)