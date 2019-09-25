from logic.modules.news import news_blu
from flask import render_template, current_app, session, request


@news_blu.route("/<int:news_id>")
def news_detail(news_id):
    """新闻详情页"""
    data = {

    }
    return render_template("news/detail.html", data=data)





