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
    pprint.pprint(data)
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
    user_id = data.get("user_id")
    reaction = data.get("reaction")
    if not (0 <= user_id < len(USERS)):
        return Response(
            "Author of the reaction not found",
            status=HTTPStatus.NOT_FOUND,
        )
    post = POSTS[post_id]
    post.set_reaction(reaction)
    user = USERS[user_id]
    user.increase_reactions()
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
    return render_template("posts.html", POSTS=POSTS)


@app.route("/site/post/create", methods=["GET", "POST"])
def site_post_create():
    data = dict()
    form = forms.PostCreateForm()
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
    return render_template("post_create.html", form=form)


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
    return render_template("posts.html", POSTS=user_posts)

@app.delete("/posts/<int:post_id>")
def delete_post(post_id):
    if 0 <= post_id < len(USERS):
        POSTS[post_id].status = "deleted"
        return Response(status=HTTPStatus.NO_CONTENT)
    return Response(status=HTTPStatus.NOT_FOUND)
