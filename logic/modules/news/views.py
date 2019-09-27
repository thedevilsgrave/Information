from logic.modules.news import news_blu
from flask import render_template, current_app, session, request, g, abort
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

    # 查询新闻数据
    news = None

    try:
        news = News.query.get(news_id)
    except Exception as err:
        current_app.logger.error(err)

    if not news:
        abort(404)
    # 新闻点击次数更新
    news.clicks += 1

    news_dict = []
    for new in news_list:
        news_dict.append(new.to_basic_dict())
    data = {
        "user": user.to_dict() if user else None,
        "news_list": news_dict,
        "news": news.to_dict()
    }
    return render_template("news/detail.html", data=data)





