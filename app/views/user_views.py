import json

from app.models.User import User
from app import USERS, app, forms
from flask import (
    request,
    Response,
    render_template,
    flash,
    url_for,
    get_flashed_messages,
    redirect,
)
from http import HTTPStatus
import matplotlib.pyplot as plt
import requests


@app.post("/users/create")
def create_user():
    data = request.json
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    if any(email == user.email for user in USERS if user.status != "deleted"):
        return Response(
            "Email already exists",
            status=HTTPStatus.CONFLICT,
        )
    if not first_name or not last_name or not email:
        return Response(
            "Missing required fields",
            status=HTTPStatus.BAD_REQUEST,
        )
    if not User.check_email_validity(email):
        return Response(
            "Invalid email",
            status=HTTPStatus.BAD_REQUEST,
        )
    user = User(len(USERS), first_name, last_name, email)
    USERS.append(user)
    return Response(
        user.to_json(),
        status=HTTPStatus.CREATED,
        mimetype="application/json",
    )


@app.get("/users/<int:user_id>")
def get_user(user_id):
    if not User.is_valid_id(user_id):
        return Response(status=HTTPStatus.NOT_FOUND)
    user = USERS[user_id]
    return Response(
        user.to_json(),
        status=HTTPStatus.OK,
        mimetype="application/json",
    )


@app.get("/users/<int:user_id>/posts")
def get_user_posts(user_id):
    if not User.is_valid_id(user_id):
        return Response(
            "User not found",
            status=HTTPStatus.NOT_FOUND,
        )
    data = request.json
    sort_type = data["sort"]
    user = USERS[user_id]
    if sort_type == "asc":
        user_posts = sorted(user.posts)
    elif sort_type == "desc":
        user_posts = sorted(user.posts, reverse=True)
    else:
        return Response(status=HTTPStatus.BAD_REQUEST)
    return Response(
        json.dumps(
            {
                "posts": [
                    post.to_json() for post in user_posts if post.status != "deleted"
                ]
            }
        ),
        status=HTTPStatus.OK,
        mimetype="application/json",
    )


@app.get("/users/leaderboard")
def leaderboard():
    data = request.json
    data_type = data["type"]
    sort_type = data["sort"]

    if not data_type or not sort_type:
        return Response("Missing required fields", status=HTTPStatus.BAD_REQUEST)

    if sort_type == "asc":
        users = sorted(USERS)
    elif sort_type == "desc":
        users = sorted(USERS, reverse=True)
    else:
        return Response(status=HTTPStatus.BAD_REQUEST)
    users = list(filter(lambda user: user.status != "deleted", users))

    if data_type == "table":
        return Response(
            json.dumps({"users": [json.loads(user.to_json()) for user in users]}),
            status=HTTPStatus.OK,
            mimetype="application/json",
        )
    elif data_type == "graph":
        if len(users) >= 25:
            users = users[:25]
        ax, fig = plt.subplots(figsize=(12, 12))
        fig.bar(
            [f"{user.id}) {user.first_name} {user.last_name}" for user in users],
            [user.total_reactions for user in users],
        )
        fig.set_xlabel("Users")
        fig.set_xticklabels(
            [f"{user.id}) {user.first_name} {user.last_name}" for user in users],
            rotation=45,
            ha="right",
        )

        fig.set_ylabel("Reactions")
        plt.savefig("leaderboard.png")

        return Response(
            open("leaderboard.png", "rb"),
            status=HTTPStatus.OK,
            mimetype="image/png",
        )

    else:
        return Response(status=HTTPStatus.BAD_REQUEST)


@app.get("/site/users")
def get_users_for_site():
    return render_template("users.html", USERS=USERS)


@app.route("/site/user/create", methods=["GET", "POST"])
def site_user_create():
    data = dict()
    form = forms.UserCreateForm()
    if form.validate_on_submit():
        data["first_name"] = form.first_name.data
        data["last_name"] = form.last_name.data
        data["email"] = form.email.data
        form.email.data = ""
        form.first_name.data = ""
        form.last_name.data = ""
        response = requests.post(url_for("create_user", _external=True), json=data)
        if response.status_code == 201:
            flash("Пользователь успешно создан", "success")
            return redirect(url_for("get_users_for_site"))
        elif response.status_code == HTTPStatus.CONFLICT:
            flash("Пользователь с таким email уже существует", "danger")
            return redirect(url_for("site_user_create"))
    return render_template("user_changes.html", form=form, flag=False)


@app.get("/site/user")
def get_user_for_site():
    user_id = int(request.args.get("id"))
    if not User.is_valid_id(user_id):
        return render_template("404.html"), 404
    user = USERS[user_id]
    return render_template("user.html", user=user)


@app.route("/site/user/edit", methods=["GET", "POST"])
def site_user_edit():
    user_id = int(request.args.get("id"))
    if not User.is_valid_id(user_id):
        return render_template("404.html"), 404
    user = USERS[user_id]
    data = dict()
    form = forms.UserCreateForm()
    if form.validate_on_submit():
        data["first_name"] = form.first_name.data
        data["last_name"] = form.last_name.data
        data["email"] = form.email.data
        form.email.data = ""
        form.first_name.data = ""
        form.last_name.data = ""
        if any(
            data["email"] == user.email
            for user in USERS
            if (user.status != "deleted" and user.id != user_id)
        ):
            flash("Пользователь с таким email уже существует", "danger")
            return redirect(url_for("site_user_edit", id=user_id))
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        user.email = data["email"]
        flash("Данные пользователя успешно изменены", "success")
        return redirect(url_for("get_users_for_site"))
    return render_template("user_changes.html", form=form, flag=True)


@app.delete("/users/<int:user_id>")
def delete_user(user_id):
    if 0 <= user_id < len(USERS):
        USERS[user_id].del_user()
        flash("Пользователь удален", "danger")
        return Response(status=HTTPStatus.NO_CONTENT)
    return Response(status=HTTPStatus.NOT_FOUND)
