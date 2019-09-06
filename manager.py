from flask import Flask, session
from flask_wtf import CSRFProtect
from redis import StrictRedis
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session


class Config(object):
    """项目的配置"""
    DEBUG = True
    SECRET_KEY = "P+gASq3hwoH+ZNXDviyzqWscSgpbfDmsgOYwmAWvCoyVRORNFgNiCJBENpWCsloP"
    # 为Mysql添加配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 为Redis设置配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    # 为session配置
    SESSION_TYPE = "redis"
    # 设置session保存到redis
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 设置是否对session进行签名
    SESSION_USE_SIGNER = True
    # 设置session是否一直存在，设置过期时间
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = 86300 * 2


app = Flask(__name__)
app.config.from_object(Config)
# 初始化Mysql数据库对象
db = SQLAlchemy(app)
# 初始化Redis数据库对象
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# 开启CSRF保护
CSRFProtect(app)
# 设置 指定session保存位置
Session(app)


@app.route('/')
def index():
    session["name"] = "lishu"
    return "hello11world"


if __name__ == "__main__":
    app.run()