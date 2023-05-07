import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Column,String,Integer,Float,ForeignKey,DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base=declarative_base()


class User(Base):
    __tablename__='user'
    id = Column (Integer, primary_key=True)
    email = Column(String(50), unique=True)
    name = Column(String(50))
    password = Column(String(64))
    group = Column(Integer, default=1)
    created_at = Column (DateTime, default=datetime.utcnow, nullable=False )
    
    def __repr__(self) -> str:
        return f"{self.id}|{self.name}|{self.group}"
    
class Patient(Base):
    __tablename__ = 'patients'
    id = Column (Integer, primary_key=True)
    name = Column(String(50))
    age=Column(Integer)
    is_hepatitis = Column(Boolean, default=False)
    steroid=Column(Boolean,default=False)
    antivirals=Column(Boolean,default=False)
    fatigue=Column(Boolean,default=False)
    malaise=Column(Boolean,default= False)
    anorexia=Column(Boolean,default=False)
    is_liver_big=Column(Boolean,default=False)
    is_liver_firm=Column(Boolean,default=False)
    spleen=Column(Boolean,default=False)
    spiders=Column(Boolean,default=False)
    iascites=Column(Boolean,default=False)
    varices=Column(Boolean,default=False)
    bilirubin=Column(Float)
    alk_phosphate=Column(Float)
    sgot=Column(Float)
    albumin=Column(Float)
    protime=Column(Float)
    histology=Column(Boolean,default=False)

    def __str__(self):
        return self.name

if __name__ == "__main__": 
    engine = create_engine('sqlite:///project_db.sqlite3')
    Base.metadata.create_all(engine)
