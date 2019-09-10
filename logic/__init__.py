from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis

from config import config_dict

db = SQLAlchemy()


def create_app(config_name):
    """创建不同的app方法"""
    app = Flask(__name__)
    app.config.from_object(config_dict[config_name])
    # 初始化Mysql数据库对象
    db.init_app(app)
    # 初始化Redis数据库对象
    redis_store = StrictRedis(host=config_dict[config_name].REDIS_HOST, port=config_dict[config_name].REDIS_PORT)
    # 开启CSRF保护
    CSRFProtect(app)
    # 设置 指定session保存位置
    Session(app)

    return app
