from logic import db
from logic.modules.news import news_blu
from flask import render_template, current_app, session, request, g, abort, jsonify, json
from logic.models import User, News, Category, Comment
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
    # 是否收藏过了
    is_liked = False
    # 如果用户已登录
    # 判断用户是否已收藏
    # is_liked  = True
    if user:
        if news in user.collection_news:
            is_liked = True

    # 查评论数据
    comments = []
    try:
        comments = Comment.query.filter(Comment.news_id == news.id).order_by(Comment.create_time.desc()).all()
    except Exception as err:
        current_app.logger.error(err)

    comment_dict_li = []
    for comment in comments:
        comment_dict_li.append(comment.to_dict())

    news_dict = []
    for new in news_list:
        news_dict.append(new.to_basic_dict())
    data = {
        "user": user.to_dict() if user else None,
        "news_list": news_dict,
        "news": news.to_dict(),
        "is_liked": is_liked,
        "comments": comment_dict_li
    }
    return render_template("news/detail.html", data=data)


@news_blu.route("/news_collect", methods=["POST"])
@user_login_data
def news_liked():
    """用户新闻收藏"""
    user = g.user

    if not user:
        return jsonify(errno="5465", errmsg="用户未登录")

    # 1.接收参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")

    # 2.判断参数
    if not all([news_id, action]):
        return jsonify(errno="4013", errmsg="参数错误")
    if action not in ["collect", "cancel_collect"]:
        return jsonify(errno="4013", errmsg="参数错误")

    try:
        news_id = int(news_id)
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno="4013", errmsg="参数错误")

    # 3.查询新闻,并判断新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno="5000", errmsg="参数错误")

    if not news:
        return jsonify(errno="4500", errmsg="未查询到新闻数据")

    if action == "cancel_collect":
        if news in user.collection_news:
            user.collection_news.remove(news)
        else:
            return jsonify(errno="4500", errmsg="未查询到新闻数据")
    else:
        # 4.将新闻添加到用户收藏列表
        if news not in user.collection_news:
            user.collection_news.append(news)

    return jsonify(errno="2000", errmsg="收藏成功!")


@news_blu.route("/news_comment", methods=["POST"])
@user_login_data
def comment_news():
    """新闻评论&评论的评论"""
    user = g.user

    if not user:
        return jsonify(errno="5465", errmsg="用户未登录")

    # 1. 接收参数
    news_id = request.json.get("news_id")
    comment_contents = request.json.get("comment")
    parent_id = request.json.get("parent_id")

    # 2. 判断参数
    if not all([news_id, comment_contents]):
        return jsonify(errno="5000", errmsg="参数错误")

    try:
        news_id = int(news_id)
        # parent_id = int(parent_id)
    except Exception as err:
        return jsonify(errno="5000", errmsg="参数错误")
    # 3.查询新闻,并判断新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno="5000", errmsg="参数错误")

    if not news:
        return jsonify(errno="4500", errmsg="未查询到新闻数据")

    # 3. 创建评论模型,添加到数据库
    comment = Comment()

    comment.user_id = user.id
    comment.news_id = news.id
    comment.content = comment_contents
    if parent_id:
        comment.parent_id = parent_id
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as err:
        current_app.logger.error(err)
        db .session.rollback()

    return jsonify(errno="2000", errmsg="OK", data=comment.to_dict())

