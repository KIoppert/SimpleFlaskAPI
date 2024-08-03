import json
import re

from app import USERS
from app.models import Post


class User:
    def __init__(self, id: int, first_name: str, second_name: str, email: str):
        self.id = id
        self.first_name = first_name
        self.last_name = second_name
        self.email = email
        self.total_reactions = 0
        self.posts = []
        self.status = "created"

    def to_json(self):
        return json.dumps(
            {
                "id": self.id,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "email": self.email,
                "total_reactions": self.total_reactions,
                "posts": [post.to_json() for post in self.posts],
            }
        )

    def add_post(self, post: Post):
        self.posts.append(post)

    def increase_reactions(self, i: int = 1):
        self.total_reactions += i

    def __lt__(self, other):
        return self.total_reactions < other.total_reactions

    @staticmethod
    def check_email_validity(email: str) -> bool:
        return (
            re.fullmatch(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", email)
            is not None
        )

    @staticmethod
    def is_valid_id(user_id):
        return 0 <= user_id < len(USERS) and USERS[user_id].status != "deleted"
