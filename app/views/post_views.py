import json
import pprint

import requests

from app import app, USERS, POSTS, forms
from flask import request, Response, jsonify, render_template, url_for, flash, redirect
from http import HTTPStatus
from app.models.Post import Post
from app.models.User import User


@app.post("/posts/create")
def create_post():
    data = request.json
    author_id = int(data.get("author_id"))
    text = data.get("text")
    title = 'Без заголовка' if data.get("title") is None else data.get("title")
    if author_id is None or not text:
        print(author_id, text)
        return Response(
            "Missing required fields",
            status=HTTPStatus.BAD_REQUEST,
        )
    if not (0 <= author_id < len(USERS)):
        return Response(
            "Author not found",
            status=HTTPStatus.NOT_FOUND,
        )
    post = Post(len(POSTS), author_id, text, title)
    POSTS.append(post)
    return Response(
        json.dumps(post.to_json()),
        status=HTTPStatus.CREATED,
        mimetype="application/json",
    )


@app.post("/posts/<int:post_id>/reaction")
def set_reaction_on_post(post_id):
    if not (0 <= post_id < len(POSTS)):
        return Response(
            "Post not found",
            status=HTTPStatus.NOT_FOUND,
        )
    data = request.json
    user_id = int(data.get("user_id"))
    reaction = data.get("reaction")
    if not (0 <= user_id < len(USERS)):
        flash("Автор реакции не найден", "danger")
        return Response(
            "Author of the reaction not found",
            status=HTTPStatus.NOT_FOUND,
        )
    # if user_id == POSTS[post_id].author_id:
    #     flash("Автор реакции не может быть автором поста", "danger")
    #     return Response(
    #         "Author of the reaction can't be the author of the post",
    #         status=HTTPStatus.BAD_REQUEST,
    #     )
    post = POSTS[post_id]
    post.set_reaction(reaction)
    user = USERS[user_id]
    user.increase_reactions()
    flash("Реакция успешно установлена", "success")
    return Response(status=HTTPStatus.OK)


@app.get("/posts/<int:post_id>")
def get_post(post_id):
    if 0 <= post_id < len(POSTS):
        post = POSTS[post_id]
        return Response(
            json.dumps(post.to_json()),
            status=HTTPStatus.OK,
            mimetype="application/json",
        )
    return Response(status=HTTPStatus.NOT_FOUND)


@app.get("/site/posts")
def get_posts_for_site():
    return render_template("posts.html", POSTS=POSTS, user=None)


@app.route("/site/post/create", methods=["GET", "POST"])
def site_post_create():
    data = dict()
    form = forms.PostCreateForm()
    user_id = request.args.get('user_id')
    if request.method == "GET" and user_id is not None:
        form.author_id.data = user_id
    if form.validate_on_submit():
        data["author_id"] = form.author_id.data
        data['title'] = form.title.data
        data["text"] = form.text.data
        form.author_id.data = ""
        form.text.data = ""
        form.title.data = ""
        response = requests.post(url_for("create_post", _external=True), json=data)
        if response.status_code == HTTPStatus.CREATED:
            flash("Пост успешно создан", "success")
            return redirect(url_for("get_posts_for_site"))
        elif response.status_code == HTTPStatus.NOT_FOUND:
            flash("Пользователь не найден", "danger")
            return redirect(url_for("site_post_create"))
        return redirect(url_for("site_post_create"))
    return render_template("post_changes.html", form=form, editing=False)


@app.get('/site/post')
def get_post_for_site():
    post_id = int(request.args.get("id"))
    if not Post.is_valid_id(post_id):
        return render_template("404.html"), 404
    post = POSTS[post_id]
    return render_template("post.html", post=post)


@app.get("/site/user_posts")
def get_user_posts_for_site():
    user_id = int(request.args.get('author_id'))
    if not User.is_valid_id(user_id):
        return render_template("404.html"), 404
    user_posts = [post for post in POSTS if post.author_id == user_id]
    return render_template("posts.html", POSTS=user_posts, user=USERS[user_id])


@app.route("/site/post/edit", methods=["GET", "POST"])
def site_post_edit():
    post_id = int(request.args.get("id"))
    if not Post.is_valid_id(post_id):
        return render_template("404.html"), 404
    post = POSTS[post_id]
    data = dict()
    form = forms.PostCreateForm()
    if request.method == "GET":
        form.author_id.data = post.author_id
        form.text.data = post.text
        form.title.data = post.title
    if form.validate_on_submit():
        data["author_id"] = form.author_id.data
        data['title'] = form.title.data
        data["text"] = form.text.data
        form.author_id.data = ""
        form.text.data = ""
        form.title.data = ""
        if not User.is_valid_id(int(data["author_id"])):
            flash("Автор не найден", "danger")
            return redirect(url_for("site_post_edit", id=post_id))
        post.author_id = data["author_id"]
        post.text = data["text"]
        post.title = data['title']
        flash("Данные поста успешно изменены", "success")
        return redirect(url_for("get_posts_for_site"))
    return render_template("post_changes.html", form=form, editing=True)


@app.delete("/posts/<int:post_id>")
def delete_post(post_id):
    if 0 <= post_id < len(USERS):
        POSTS[post_id].status = "deleted"
        flash("Пост удален", "danger")
        return Response(status=HTTPStatus.NO_CONTENT)
    return Response(status=HTTPStatus.NOT_FOUND)
