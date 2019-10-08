# 个人中心页的蓝图
from flask import Blueprint

# 创建蓝图，给视图函数添加前缀
user_blu = Blueprint("user", __name__, url_prefix="/user")

from . import views
