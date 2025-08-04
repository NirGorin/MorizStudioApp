
#models file:

from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship

from .database import Base



trainer_limitation= Table('trainer_limitation', Base.metadata,
                          Column('trainer_id', Integer, ForeignKey('trainers.ID')),
                          Column('limitation_id', Integer, ForeignKey('limitations.ID'))
                         )


class Trainer(Base):
    __tablename__='trainers'
    ID=Column(Integer,primary_key=True,index=True)
    First_Name=Column(String(100))
    Last_Name=Column(String(100))
    username=Column(String(100),unique=True)
    Email=Column(String(100),unique=True)
    Password=Column(String(100))
    Level=Column(String(100))
    Number_Of_Training=Column(Integer)
    Role=Column(String(100))
    Phone_Number=Column(String(20),unique=True)
    Limitations=relationship("Limitation",secondary=trainer_limitation,back_populates="Trainers")

class Limitation(Base):
    __tablename__='limitations'
    ID=Column(Integer,primary_key=True,index=True)
    limitation = Column(String(100))
    Trainers=relationship("Trainer",secondary=trainer_limitation,back_populates="Limitations")
