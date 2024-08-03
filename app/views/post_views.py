import json

from app import app, USERS, POSTS
from flask import request, Response, jsonify
from http import HTTPStatus
from app.models.Post import Post


@app.post("/posts/create")
def create_post():
    data = request.json
    author_id = data.get("author_id")
    text = data.get("text")
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
    post = Post(len(POSTS), author_id, text)
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


@app.delete("/posts/<int:post_id>")
def delete_post(post_id):
    if 0 <= post_id < len(USERS):
        POSTS[post_id].status = "deleted"
        return Response(status=HTTPStatus.NO_CONTENT)
    return Response(status=HTTPStatus.NOT_FOUND)
