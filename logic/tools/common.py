from logic.models import User, News
from flask import current_app, session, g
import functools
# 这个文件用于存放公共的工具


def do_index_class(index):
    if index == 1:
        return "first"
    elif index == 2:
        return "second"
    elif index == 3:
        return "third"
    return ""


# def query_user_data():
#     # 1. 如果用户已登录,则将数据库中数据查出替换模板
#     # 1.1 取到用户id
#     user_id = session.get("user_id", None)
#     user = None
#
#     if user_id:
#         # 尝试查询用户模型
#         try:
#             user = User.query.get(user_id)
#         except Exception as err:
#             current_app.logger.error(err)
#         return user
#     return None


def user_login_data(f):
    @functools.wraps(f)      # 使用functools去装饰内层函数,可以保持装饰的当前函数的"__name__"不变
    def wappwer(*args, **kwargs):
        user_id = session.get("user_id", None)
        user = None

        if user_id:
            # 尝试查询用户模型
            try:
                user = User.query.get(user_id)
            except Exception as err:
                current_app.logger.error(err)
            # 把查询出来的数据赋值给g变量
        g.user = user
        return f(*args, **kwargs)
    return wappwer