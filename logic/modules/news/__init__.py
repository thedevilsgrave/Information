# 新闻详情页的蓝图
from flask import Blueprint

# 创建蓝图，给视图函数添加前缀
news_blu = Blueprint("news", __name__, url_prefix="/news")

from . import views
