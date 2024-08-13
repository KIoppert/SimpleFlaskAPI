from app import USERS, POSTS


class Post:
    def __init__(self, id: int, author_id: int, text: str, title: str):
        self.id = id
        self.author_id = author_id
        self.text = text
        self.title = title
        self.reactions = []
        self.status = "created"
        USERS[author_id].add_post(self)

    def to_json(self) -> dict:
        return dict(
            {
                "id": self.id,
                "author_id": self.author_id,
                "text": self.text,
                "reactions": self.reactions,
            }
        )

    def set_reaction(self, reaction):
        self.reactions.append(reaction)

    def reactions_count(self):
        return len(self.reactions)

    @staticmethod
    def is_valid_id(post_id):
        return 0 <= post_id < len(POSTS) and POSTS[post_id].status != "deleted"

    def __lt__(self, other):
        return len(self.reactions) < len(other.reactions)
