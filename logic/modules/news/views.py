from logic.modules.news import news_blu
from flask import render_template, current_app, session, request, g
from logic.models import User, News, Category
from logic.tools.common import user_login_data


@news_blu.route("/<int:news_id>")
@user_login_data
def news_detail(news_id):
    """新闻详情页"""

    # 查询用户登录的信息
    user = g.user

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





