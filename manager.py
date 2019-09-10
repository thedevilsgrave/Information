from flask import Flask, session
from flask_wtf import CSRFProtect
from redis import StrictRedis
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from config import Config

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
# 将app与Manager关联
manager = Manager(app)
# 数据库迁移,将app与db关联
Migrate(app, db)
# 将迁移命令添加到manager
manager.add_command("db", MigrateCommand)


@app.route('/')
def index():
    session["name"] = "lishu"
    return "hello11world"


if __name__ == "__main__":
    manager.run()