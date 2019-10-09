from flask import render_template, g, redirect, request, jsonify, current_app
from logic.tools.common import user_login_data
from logic.modules.personal import user_blu
from logic.tools.image_storage import storage


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

