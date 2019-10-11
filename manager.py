import logging
from logic.models import User
from flask import session
from logic import create_app, db, models
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


@manager.option("-n", "-name", dest="name")
@manager.option("-p", "-password", dest="password")
def create_admin(name, password):

    if not all([name, password]):
        print("参数错误")

    user = User()
    user.nick_name = name
    user.mobile = name
    user.password = password
    user.is_admin = True

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as err:
        print(err)
        db.session.rollback()


if __name__ == "__main__":
    manager.run()
