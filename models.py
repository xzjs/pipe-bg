import json
from sqlalchemy import Column, Integer, String,Text
from database import Base


class Mark(Base):
    __tablename__ = 'marks'
    id = Column(Integer, primary_key=True)
    src = Column(Text())
    flaw = Column(Text())
    level = Column(Text())
    x = Column(Integer())
    y = Column(Integer())
    width = Column(Integer())
    height = Column(Integer())

    def __init__(self, src, flaw, level, x, y, width, height):
        self.src = src
        self.flaw = flaw
        self.level = level
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __repr__(self):
        return json.dumps(self)
