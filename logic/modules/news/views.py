from logic import db
from logic.modules.news import news_blu
from flask import render_template, current_app, session, request, g, abort, jsonify, json
from logic.models import User, News, Category, Comment, CommentLike
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

    # 需求:查询当前用户在当前新闻点赞了那几条评论
    comment_like_ids = []
    try:
        if g.user:
            # 1. 查询出所有的新闻评论的id
            comment_ids = [comment.id for comment in comments]
            # 2. 再查询出这些评论中有那些被用户点赞
            comment_likes = CommentLike.query.filter(CommentLike.comment_id.in_(comment_ids),
                                                     CommentLike.user_id == g.user.id)
            # 3. 取到所有被用户点赞的评论id
            comment_like_ids = [comment_liked.comment_id for comment_liked in comment_likes]
    except Exception as err:
        current_app.logger.error(err)

    comment_dict_li = []
    for comment in comments:
        comment_dict = comment.to_dict()
        comment_dict["is_liked"] = False
        if comment.id in comment_like_ids:
            comment_dict["is_liked"] = True
        comment_dict_li.append(comment_dict)

    news_dict = []
    for new in news_list:
        news_dict.append(new.to_basic_dict())

    is_follow = False
    # if 当前新闻有作者 并且 当前登录用户已经关注过这个作者
    if news.user and user:
        # 当前登录用户是否关注过作者
        if news.user in user.followed:
            is_follow = True
    data = {
        "user": user.to_dict() if user else None,
        "news_list": news_dict,
        "news": news.to_dict(),
        "is_liked": is_liked,
        "comments": comment_dict_li,
        "is_follow": is_follow
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


@news_blu.route("/comment_like", methods=["POST"])
@user_login_data
def comment_like():
    """评论点赞与取消点赞"""

    # 获取参数
    user = g.user

    if not user:
        return jsonify(errno="5465", errmsg="用户未登录")

    # 1. 接收参数
    news_id = request.json.get("news_id")
    comment_id = request.json.get("comment_id")
    action = request.json.get("action")

    # 判断参数
    if not all([comment_id, action]):
        return jsonify(errno="5000", errmsg="参数错误")

    if action not in ["add", "remove"]:
        return jsonify(errno="5000", errmsg="参数错误")

    # 查询评论数据
    try:
        comment = Comment.query.get(comment_id)
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno="5000", errmsg="参数错误")

    if not comment:
        return jsonify(errno="4500", errmsg="评论不存在")

    if action == "add":
        comment_like_model = CommentLike.query.filter(CommentLike.user_id == user.id,
                                                      CommentLike.comment_id == comment.id).first()
        if not comment_like_model:
            comment_like_model = CommentLike()
            comment_like_model.user_id = user.id
            comment_like_model.comment_id = comment.id
            db.session.add(comment_like_model)
            comment.like_count += 1
    else:     # 取消点赞
        comment_like_model = CommentLike.query.filter(CommentLike.user_id == user.id,
                                                      CommentLike.comment_id == comment.id).first()
        if comment_like_model:
            db.session.delete(comment_like_model)
            comment.like_count -= 1
    try:
        db.session.commit()
    except Exception as err:
        db.session.rollback(err)
        current_app.logger.error(err)
        return jsonify(errno="5100", errmsg="数据库操作失败")
    return jsonify(errno="2000", errmsg="点赞成功!")


@news_blu.route('/followed_user', methods=["POST"])
@user_login_data
def followed_user():
    """关注/取消关注用户"""
    if not g.user:
        return jsonify(errno="3500", errmsg="用户未登录")

    user_id = request.json.get("user_id")
    action = request.json.get("action")

    if not all([user_id, action]):
        return jsonify(errno="3500", errmsg="参数错误")

    if action not in ("follow", "unfollow"):
        return jsonify(errno="3500", errmsg="参数错误")

    # 查询到关注的用户信息
    try:
        target_user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno="4500", errmsg="查询数据库失败")

    if not target_user:
        return jsonify(errno="3000", errmsg="未查询到用户数据")

    # 根据不同操作做不同逻辑
    if action == "follow":
        if target_user.followers.filter(User.id == g.user.id).count() > 0:
            return jsonify(errno="3540", errmsg="当前已关注")
        target_user.followers.append(g.user)
    else:
        if target_user.followers.filter(User.id == g.user.id).count() > 0:
            target_user.followers.remove(g.user)

    # 保存到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno="3100", errmsg="数据保存错误")

    return jsonify(errno="2000", errmsg="操作成功")
