from flask import Blueprint

# 创建蓝图，给视图函数添加前缀
logter_blu = Blueprint("logter", __name__, url_prefix="/passport")

from . import views
