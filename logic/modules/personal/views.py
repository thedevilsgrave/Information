from flask import render_template, g, redirect, request, jsonify, current_app

from logic import db
from logic.tools.common import user_login_data
from logic.modules.personal import user_blu
from logic.tools.image_storage import storage
from logic.models import User, News, Category, Comment, CommentLike


@user_blu.route("/info")
@user_login_data
def user_info():
    """用户信息主页面"""
    user = g.user
    if not user:
        return redirect("/")
    data = {"user": user.to_dict()}
    return render_template("news/user.html", data=data)


@user_blu.route("/base_info", methods=["GET", "POST"])
@user_login_data
def base_info():
    """修改用户基本信息"""
    user = g.user
    if not user:
        return redirect("/")

    # 不同的请求方式做不同的事
    if request.method == "GET":
        return render_template("news/user_base_info.html", data={"user": user.to_dict()})

    # 接收参数
    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")

    # 判断参数
    if not all([nick_name, signature, gender]):
        return jsonify(errno="3500", errmsg="参数错误")
    if gender not in ("MAN", "WOMAN"):
        return jsonify(errno="3500", errmsg="参数错误")

    user.nick_name = nick_name
    user.gender = gender
    user.signature = signature

    return jsonify(errno="2000", errmsg="OK")


@user_blu.route("/pic_info", methods=["POST", "GET"])
@user_login_data
def pic_info():
    """修改用户头像"""
    user = g.user
    user_avatar_url = "http://oyucyko3w.bkt.clouddn.com/"
    if request.method == "GET":
        return render_template("news/user_pic_info.html", data={"user": user.to_dict()})
    #  如果是POST请求则修改头像
    # 1. 获取参数
    try:
        avatar = request.files.get("avatar").read()
    except Exception as err:
        return jsonify(errno="3500", errmsg="参数错误")

    # 2.上传头像
    try:
        # 使用自己封装的上传图片的方法
        key = storage(avatar)
    except Exception as err:
        return jsonify(errno="5666", errmsg="上传失败")

    # 3. 保存头像地址
    user.avatar_url = key

    return jsonify(errno="2000", errmsg="OK", data={"avatar_url": user_avatar_url+key})


@user_blu.route("/change_pwd", methods=["POST", "GET"])
@user_login_data
def change_pwd():
    """用户修改密码"""
    user = g.user
    if not user:
        return redirect("/")
    if request.method == "GET":
        return render_template("news/user_pass_info.html")

    # 1. 获取参数
    old_pwd = request.json.get("old_password")
    new_pwd = request.json.get("new_password")

    # 2. 判断参数
    if not all([old_pwd, new_pwd]):
        return jsonify(errno="3500", errmsg="参数错误")

    # 3. 判断旧密码是否正确
    if not user.check_passowrd(old_pwd):
        return jsonify(errno="5455", errmsg="旧密码错误")

    # 4. 设置新密码
    user.password = new_pwd

    return jsonify(errno="2000", errmsg="OK")


@user_blu.route("/user_collection", methods=["GET"])
@user_login_data
def user_collection():
    """ 显示用户新闻收藏页面 """
    user = g.user

    # 1. 获取参数
    page = request.args.get("p", 1)

    # 2. 判断参数
    try:
        page = int(page)
    except Exception as err:
        current_app.logger.error(err)
        page = 1

    # 3. 查询用户指定的新闻收藏页
    current_page = 1
    total_page = 1
    news_list = []
    try:
        paginate = user.collection_news.paginate(page, 8, False)
        current_page = paginate.page  # 显示第几页
        total_page = paginate.pages  # 总页数
        news_list = paginate.items  # 查询出的新闻列表对象
    except Exception as err:
        current_app.logger.error(err)

    news_dict_li = []
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    data = {
        "current_page": current_page,
        "total_page": total_page,
        "news_collection": news_dict_li
    }

    return render_template("news/user_collection.html", data=data)


@user_blu.route("/news_release", methods=["GET", "POST"])
@user_login_data
def news_release():
    """ 用户发布新闻页面 """
    user = g.user
    user_avatar_url = "http://oyucyko3w.bkt.clouddn.com/"

    # 如果是GET请求则渲染模板
    if request.method == "GET":
        # 加载新闻分类
        categories = []
        try:
            categories = Category.query.all()
        except Exception as err:
            current_app.logger.error(err)

        category_li = []

        for category in categories:
            category_li.append(category.to_dict())
        # 移除`最新`分类
        category_li.pop(0)

        return render_template("news/user_news_release.html", data={"categories":category_li})

    # 如果是POST请求则进行新闻发布
    # 1. 获取要提交的数据

    # 新闻标题
    title = request.form.get("title")
    source = "个人发布"
    # 新闻摘要
    digest = request.form.get("digest")
    # 新闻内容
    content = request.form.get("content")
    # 索引图片
    index_image = request.files.get("index_image")
    # 分类id
    category_id = request.form.get("category_id")

    # 2. 校验参数
    # 2.1 判断数据是否有值
    if not all([title, source, digest, content, index_image, category_id]):
        return jsonify(errno="3500", errmsg="参数有误")
    try:
        category_id = int(category_id)
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno="3500", errmsg="参数有误")

    # 1.2 尝试读取图片
    try:
        index_image = index_image.read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno="3500", errmsg="参数有误")

    # 2. 将标题图片上传到七牛
    try:
        key = storage(index_image)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno="5689", errmsg="上传图片错误")

    # 3. 初始化新闻模型，并设置相关数据
    news = News()
    news.title = title
    news.digest = digest
    news.source = source
    news.content = content
    news.index_image_url = user_avatar_url + key
    news.category_id = category_id
    news.user_id = user.id
    # 1代表待审核状态
    news.status = 1

    # 4. 保存到数据库
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno="4000", errmsg="保存数据失败")
    # 5. 返回结果
    return jsonify(errno="2000", errmsg="发布成功，等待审核")


@user_blu.route("/news_list", methods=["GET", "POST"])
@user_login_data
def news_list():
    """用户新闻列表"""

    # 获取参数
    user = g.user
    page = request.args.get("p", 1)
    news_dict_li = []
    news_li = []
    current_page = 1
    total_page = 1

    # 判断参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno="3500", errmsg="参数错误!")
    try:
        paginate = News.query.filter(News.user_id == user.id).paginate(page, 10, False)
        current_page = paginate.page
        total_page = paginate.pages
        news_li = paginate.items
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno="6500", errmsg="数据查询失败!")

    for news in news_li:
        news_dict_li.append(news.to_review_dict())

    data = {
        "news_list": news_dict_li,
        "current_page": current_page,
        "total_page": total_page
    }

    return render_template("news/user_news_list.html", data=data)


@user_blu.route('/user_follow')
@user_login_data
def user_follow():
    # 获取页数
    page = request.args.get("page", 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    user = g.user

    follows = []
    current_page = 1
    total_page = 1
    try:
        paginate = user.followed.paginate(page, 4, False)
        # 获取当前页数据
        follows = paginate.items
        # 获取当前页
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    user_dict_li = []

    for follow_user in follows:
        user_dict_li.append(follow_user.to_dict())
    data = {
            "users": user_dict_li,
            "total_page": total_page,
            "current_page": current_page
            }
    return render_template('news/user_follow.html', data=data)


@user_blu.route('/other_info')
@user_login_data
def other_info():

    user = g.user

    data = {
        "user": user.to_dict() if user else None
    }
    return render_template("news/other.html", data=data)
