import logging

from flask import session
from logic import create_app,db
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

# create_app类似于工厂方法
app = create_app('development')


# 将app与Manager关联
manager = Manager(app)
# 数据库迁移,将app与db关联
Migrate(app, db)
# 将迁移命令添加到manager
manager.add_command("db", MigrateCommand)


@app.route('/')
def index():
    # session["name"] = "lishu"
    # # 测试log日志
    # logging.debug('测试用的debug')
    # logging.error('测试用的error')
    # logging.warning('测试用的warning')
    return "hello11world"


if __name__ == "__main__":
    manager.run()