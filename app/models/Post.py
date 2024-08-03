from app import USERS


class Post:
    def __init__(self, id: int, author_id: int, text: str):
        self.id = id
        self.author_id = author_id
        self.text = text
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

    def __lt__(self, other):
        return len(self.reactions) < len(other.reactions)
