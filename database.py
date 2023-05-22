import json
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

with open('config.json') as f:
    config = json.load(f)
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{config['USERNAME']}:{config['PWD']}@{config['HOST']}:{config['PORT']}/{config['DATABASE']}?charset=utf8mb4"
engine = create_engine(SQLALCHEMY_DATABASE_URI)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # 在这里导入定义模型所需要的所有模块，这样它们就会正确的注册在
    # 元数据上。否则你就必须在调用 init_db() 之前导入它们。
    import models
    Base.metadata.create_all(bind=engine)
