from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis

from config import config_dict

app = Flask(__name__)
app.config.from_object(config_dict["development"])
# 初始化Mysql数据库对象
db = SQLAlchemy(app)
# 初始化Redis数据库对象
redis_store = StrictRedis(host=config_dict["development"].REDIS_HOST, port=config_dict["development"].REDIS_PORT)
# 开启CSRF保护
CSRFProtect(app)
# 设置 指定session保存位置
Session(app)
