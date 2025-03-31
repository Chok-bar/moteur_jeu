from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
import datetime
from .database import Base

class Party(Base):
    __tablename__ = 'parties'
    
    id_party = Column(Integer, primary_key=True, autoincrement=True)
    title_party = Column(String)
    
    # Relations
    players = relationship("PlayerInParty", back_populates="party")
    turns = relationship("Turn", back_populates="party")

class Role(Base):
    __tablename__ = 'roles'
    
    id_role = Column(Integer, primary_key=True)
    description_role = Column(String)
    
    # Relations
    players = relationship("PlayerInParty", back_populates="role")

class Player(Base):
    __tablename__ = 'players'
    
    id_player = Column(Integer, primary_key=True, autoincrement=True)
    pseudo = Column(String)
    
    # Relations
    parties = relationship("PlayerInParty", back_populates="player")
    plays = relationship("PlayerPlay", back_populates="player")

class PlayerInParty(Base):
    __tablename__ = 'players_in_parties'
    
    id_party = Column(Integer, ForeignKey('parties.id_party'), primary_key=True)
    id_player = Column(Integer, ForeignKey('players.id_player'), primary_key=True)
    id_role = Column(Integer, ForeignKey('roles.id_role'))
    is_alive = Column(Boolean, default=True)
    
    # Relations
    party = relationship("Party", back_populates="players")
    player = relationship("Player", back_populates="parties")
    role = relationship("Role", back_populates="players")

class Turn(Base):
    __tablename__ = 'turns'
    
    id_turn = Column(Integer, primary_key=True, autoincrement=True)
    id_party = Column(Integer, ForeignKey('parties.id_party'))
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    
    # Relations
    party = relationship("Party", back_populates="turns")
    player_plays = relationship("PlayerPlay", back_populates="turn")

class PlayerPlay(Base):
    __tablename__ = 'players_play'
    
    id_player = Column(Integer, ForeignKey('players.id_player'), primary_key=True)
    id_turn = Column(Integer, ForeignKey('turns.id_turn'), primary_key=True)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    action = Column(String(10))
    origin_position_row = Column(Integer)
    origin_position_col = Column(Integer)
    target_position_row = Column(Integer)
    target_position_col = Column(Integer)
    
    # Relations
    player = relationship("Player", back_populates="plays")
    turn = relationship("Turn", back_populates="player_plays")
