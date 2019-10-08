from flask import render_template, g, redirect
from logic.tools.common import user_login_data
from logic.modules.personal import user_blu


@user_blu.route("/info")
@user_login_data
def user_info():
    user = g.user
    if not user:
        return redirect("/")
    data = {"user": user.to_dict()}
    return render_template("news/user.html", data=data)



