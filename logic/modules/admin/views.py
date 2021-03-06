from datetime import datetime, timedelta

from flask import render_template, request, \
    redirect, current_app, \
    session, url_for, g, jsonify, abort

from logic import constants, db
from logic.models import User, News, Category
from logic.modules.admin import admin_blu
from logic.tools.common import user_login_data
import time

from logic.tools.image_storage import storage


@admin_blu.route("/login", methods=["POST", "GET"])
def login():
    """管理员用户登录页"""
    if request.method == "GET":

        # 判断用户是否已登录,如果已经登录,则直接跳转到管理员首页
        user_id = session.get("user_id", None)
        is_admin = session.get("is_admin", False)

        if user_id and is_admin:
            return render_template("admin/index.html")

        return render_template("admin/login.html")

    # 取到表单的参数
    username = request.form.get("username")
    password = request.form.get("password")

    if not all([username, password]):
        return render_template("admin/login.html", errmsg="参数错误")

    try:
        user = User.query.filter(User.mobile == username, User.is_admin == True).first()
    except Exception as err:
        current_app.logger.error(err)
        return render_template("admin/login.html", errmsg="数据查询失败")

    if not user:
        return render_template("admin/login.html", errmsg="未查询到用户信息")

    if not user.check_passowrd(password):
        return render_template("admin/login.html", errmsg="用户名或密码错误")

    # 3. 保存用户登录状态
    session["user_id"] = user.id
    session["user_phone"] = user.mobile
    session["user_name"] = user.nick_name
    session["is_admin"] = user.is_admin

    # 登录成功后跳转页面
    return redirect(url_for("admin.index"))


@admin_blu.route("/index")
@user_login_data
def index():
    """管理员主页显示"""
    user = g.user
    if not user:
        return redirect("admin.login")

    return render_template("admin/index.html", data=user.to_dict())


@admin_blu.route("/user_count")
@user_login_data
def user_count():
    """日活跃&月活跃用户显示"""
    user = g.user

    user_total = 0
    # 用户总数
    try:
        user_total = User.query.filter(User.is_admin==False).count()
    except Exception as err:
        current_app.logger.error(err)

    # 月新增数
    mouth_total = 0
    t = time.localtime()
    begin_mon_time = datetime.strptime(("%d-%02d-01" % (t.tm_year, t.tm_mon)), "%Y-%m-%d")
    try:
        mouth_total = User.query.filter(User.is_admin==False, User.create_time > begin_mon_time).count()
    except Exception as err:
        current_app.logger.error(err)

    # 日新增数
    begin_day_time = datetime.strptime(("%d-%02d-%02d" % (t.tm_year, t.tm_mon, t.tm_mday)), "%Y-%m-%d")
    day_total = 0
    try:
        day_total = User.query.filter(User.is_admin==False, User.create_time > begin_day_time).count()
    except Exception as err:
        current_app.logger.error(err)

    active_count = []
    active_time = []
    datetime.now()
    # 去今天活跃的用户数据
    # 获取今天00:00:00
    now_date = datetime.strptime(datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d')
    # 依次添加数据，再反转
    for i in range(0, 31):
        begin_date = now_date - timedelta(days=i)
        end_date = now_date - timedelta(days=(i - 1))
        active_time.append(begin_date.strftime('%Y-%m-%d'))
        count = 0
        try:
            count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                      User.last_login < end_date).count()
        except Exception as e:
            current_app.logger.error(e)
        active_count.append(count)

    # 让最近的一天显示在最后面
    active_time.reverse()
    active_count.reverse()

    data = {
        "user_total": user_total,
        "mouth_total": mouth_total,
        "day_total": day_total,
        "active_time": active_time,
        "active_count": active_count
    }

    return render_template("admin/user_count.html", data=data)


@admin_blu.route("/user_list")
def user_list():
    """所有用户列表"""

    # 接收参数
    page = request.args.get("page", 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 设置变量默认值
    users = []
    current_page = 1
    total_page = 1

    try:
        paginate = User.query.filter(User.is_admin==False).order_by(User.last_login.desc()).paginate(page, 10, False)
        users = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as err:
        current_app.logger.error(err)

    user_lists = []
    for user in users:
        user_lists.append(user.to_admin_dict())

    data = {
        "current_page": current_page,
        "total_page": total_page,
        "user_lists": user_lists
    }

    return render_template("admin/user_list.html", data=data)


@admin_blu.route("/news_review")
def news_review():
    """审核页面显示"""
    page = request.args.get("page", 1)
    key_words = request.args.get("key_words", None)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    news_list = []
    current_page = 1
    total_page = 1
    filters = [News.status != 0]

    # 如果关键字存在,那么就吧关键字添加到条件中
    if key_words:
        filters.append(News.title.contains(key_words))

    try:
        paginate = News.query.filter(*filters) \
            .order_by(News.create_time.desc()) \
            .paginate(page, 10, False)

        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_review_dict())

    context = {"total_page": total_page,
               "current_page": current_page,
               "news_list": news_dict_list
           }

    return render_template('admin/news_review.html', data=context)


@admin_blu.route("/news_review_detail/<int:news_id>")
def news_review_detail(news_id):
    """详细审核页面显示"""
    if request.method == "GET":
        # 获取新闻id
        # 通过id查询新闻
        news = None
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)

        if not news:
            return render_template('admin/news_review_detail.html', data={"errmsg": "未查询到此新闻"})

        # 返回数据
        data = {"news": news.to_dict()}
        return render_template('admin/news_review_detail.html', data=data)


@admin_blu.route("/news_review_action", methods=["POST"])
def news_review_action():
    """审核逻辑"""
    # 1. 获取参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")

    # 2. 判断参数
    if not all([news_id, action]):
        return jsonify(errno="3500", errmsg="参数错误")

    if action not in ("accept", "refuse"):
        return jsonify(errno="3500", errmsg="参数错误")

    # 3. 查询指定的新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno="5600", errmsg="数据查询错误")

    if not news:
        current_app.logger.error("没有该数据")
        return jsonify(errno="3500", errmsg="没有该数据")

    if action == "accept":
        # 审核通过
        news.status = 0
    else:
        # 审核不通过
        reason = request.json.get("reason")
        if not reason:
            return jsonify(errno="3600", errmsg="请输入原因")
        news.status = -1
        news.reason = reason

    return jsonify(errno="2000", errmsg="ok")


@admin_blu.route("/news_edit")
def news_edit():
    """审核板式编辑页面显示"""
    page = request.args.get("page", 1)
    key_words = request.args.get("key_words", None)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    news_list = []
    current_page = 1
    total_page = 1
    filters = [News.status == 0]

    # 如果关键字存在,那么就吧关键字添加到条件中
    if key_words:
        filters.append(News.title.contains(key_words))

    try:
        paginate = News.query.filter(*filters) \
            .order_by(News.clicks.desc()) \
            .paginate(page, 10, False)

        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())

    context = {"total_page": total_page,
               "current_page": current_page,
               "news_list": news_dict_list
           }

    return render_template('admin/news_edit.html', data=context)


@admin_blu.route("/news_edit_detail", methods=["POST, GET"])
def news_edit_detail():

    if request.method == "GET":

        # 获取参数
        news_id = request.args.get("news_id")

        if not news_id:
            abort(404)

        try:
            news_id = int(news_id)
        except Exception as err:
            current_app.logger.error(err)
            return render_template("admin/news_edit_detail.html", errmsg="参数错误")

        try:
            news = News.query.get(news_id)
        except Exception as err:
            current_app.logger.error(err)
            return render_template("admin/news_edit_detail.html", errmsg="查询错误")

        if not news:
            return render_template("admin/news_edit_detail.html", errmsg="未查到新闻")

        #  查询分类数据
        try:
            categories = Category.query.all()
        except Exception as err:
            current_app.logger.error(err)
            return render_template("admin/news_edit_detail.html", errmsg="查询错误")

        if not categories:
            return render_template("admin/news_edit_detail.html", errmsg="未查到数据")

        categories_li = []
        for category in categories:
            c_dict = category.to_dict()
            c_dict["is_selected"] = False
            if category.id == news.category_id:
                c_dict["is_selected"] = True
            categories_li.append(c_dict)
        # 移除`最新`分类
        categories_li.pop(0)
        data = {
            "news": news.to_dict(),
            "categories": categories_li
        }

        return render_template("admin/news_edit_detail.html", data=data)

    # 获取参数
    news_id = request.form.get("news_id")
    title = request.form.get("title")
    digest = request.form.get("digest")
    content = request.form.get("content")
    index_image = request.files.get("index_image")
    category_id = request.form.get("category_id")
    # 1.1 判断数据是否有值
    if not all([title, digest, content, category_id]):
        return jsonify(errno="3500", errmsg="参数有误")

    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
    if not news:
        return jsonify(errno="3500", errmsg="未查询到新闻数据")

    # 1.2 尝试读取图片
    if index_image:
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
            return jsonify(errno="3500", errmsg="上传图片错误")
        news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    # 3. 设置相关数据
    news.title = title
    news.digest = digest
    news.content = content
    news.category_id = category_id

    # 4. 保存到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno="3500", errmsg="保存数据失败")
    # 5. 返回结果
    return jsonify(errno="2000", errmsg="编辑成功")


@admin_blu.route("/news_type", methods=["POST", "GET"])
def news_type():

    if request.method == "GET":
        # 查询分类数据
        try:
            categories = Category.query.all()
        except Exception as err:
            current_app.logger.error(err)
            return render_template("admin/news_type.html", errmsg="查询错误")
        if not categories:
            return render_template("admin/news_type.html", errmsg="未查到数据")

        categories_li = []
        for category in categories:
            c_dict = category.to_dict()
            categories_li.append(c_dict)
        # 移除`最新`分类
        categories_li.pop(0)

        data = {
            "categories": categories_li
        }
        return render_template("admin/news_type.html", data=data)

    # 如果是POST请求则添加或修改分类
    # 1. 获取参数
    category_name = request.json.get("name")
    category_id = request.json.get("id")

    # 如果category_id有值,代表要修改分类
    if category_id:
        try:
            category_id = int(category_id)
        except Exception as err:
            current_app.logger.error(err)
            return jsonify(errno="3500", errmsg="参数错误")

        try:
            category = Category.query.get(category_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno="3500", errmsg="查询数据失败")

        if not category:
            return jsonify(errno="3500", errmsg="未查询到分类信息")
        category.name = category_name

        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno="3500", errmsg="保存数据失败")
    else:
        # 如果没有值代表要添加分类
        category = Category()
        category.name = category_name
        try:
            db.session.add(category)
        except Exception as err:
            db.session.rollback()
            current_app.logger.error(err)

    return jsonify(errno="2000", errmsg="ok")
