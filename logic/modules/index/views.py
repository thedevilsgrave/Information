from flask import render_template, current_app, session

from logic.models import User, News
from . import index_blu
from logic import redis_store


@index_blu.route('/')
def index():
    """显示主页面"""
    # 1. 如果用户已登录,则将数据库中数据查出替换模板
    # 1.1 取到用户id
    user_id = session.get("user_id", None)
    user = None

    if user_id:
        # 尝试查询用户模型
        try:
            user = User.query.get(user_id)
        except Exception as err:
            current_app.logger.error(err)

    news_list = []

    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(6)
    except Exception as err:
        current_app.logger.error(err)

    news_dict = []
    for news in news_list:
        news_dict.append(news.to_basic_dict())

    data = {
        "user": user.to_dict() if user else None,
        "news_list": news_dict
    }

    return render_template("news/index.html", data=data)


@index_blu.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")
