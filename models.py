import json
from sqlalchemy import Column, Integer, String, Text, ForeignKey, create_engine
from sqlalchemy.orm import Mapped, DeclarativeBase, Mapped, mapped_column, relationship, MappedAsDataclass, scoped_session, sessionmaker
from typing import List
from sqlalchemy_serializer import SerializerMixin


class Base(MappedAsDataclass, DeclarativeBase, SerializerMixin):
    pass
    # query = db_session.query_property()


class Mark(Base):
    __tablename__ = 'marks'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    src: Mapped[str] = mapped_column(String(30))
    flaw: Mapped[str] = mapped_column(String(30))
    level: Mapped[str] = mapped_column(String(30))
    x: Mapped[int]
    y: Mapped[int]
    width: Mapped[int]
    height: Mapped[int]
    img_id: Mapped[int] = mapped_column(ForeignKey('imgs.id'))
    img: Mapped['Img'] = relationship(back_populates='mark', init=False)


class Video(Base):
    __tablename__ = 'videos'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    src: Mapped[str] = mapped_column(String(30))
    imgs: Mapped[List['Img']] = relationship(
        back_populates="video", init=False)


class Img(Base):
    __tablename__ = 'imgs'

    serialize_rules = ('-video.imgs', '-mark.img')
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    src: Mapped[str] = mapped_column(String(30))
    video_id: Mapped[int] = mapped_column(ForeignKey('videos.id'))
    video: Mapped['Video'] = relationship(back_populates='imgs', init=False)
    mark: Mapped['Mark'] = relationship(back_populates='img', init=False)
    width:Mapped[int]
    height:Mapped[int]
