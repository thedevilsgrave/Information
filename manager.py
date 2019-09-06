from flask import Flask
from flask_wtf import CSRFProtect
from redis import StrictRedis
from flask_sqlalchemy import SQLAlchemy


class Config(object):
    """项目的配置"""
    DEBUG = True
    # 为Mysql添加配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 为Redis设置配置
    REDIS_HOST = "192.168.0.102"
    REDIS_PORT = 6379


app = Flask(__name__)
app.config.from_object(Config)
# 初始化Mysql数据库对象
db = SQLAlchemy(app)
# 初始化Redis数据库对象
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# 开启CSRF保护
CSRFProtect(app)


@app.route('/')
def index():
    return "hello11world"


if __name__ == "__main__":
    app.run()