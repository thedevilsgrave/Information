from logic.modules.news import news_blu
from flask import render_template, current_app, session, request
from logic.models import User, News, Category


@news_blu.route("/<int:news_id>")
def news_detail(news_id):
    """新闻详情页"""
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
        news_list = News.query.order_by(News.clicks.desc()).limit(8)
    except Exception as err:
        current_app.logger.error(err)

    news_dict = []
    for news in news_list:
        news_dict.append(news.to_basic_dict())
    data = {
        "user": user.to_dict() if user else None,
        "news_list": news_dict
    }
    return render_template("news/detail.html", data=data)





