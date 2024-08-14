import random

import requests
import faker
from app import app
import pytest

fake = faker.Faker("ru_RU")
ENDPOINT = "http://127.0.0.1:5000"

import threading
import time
import pytest
import requests
import faker
from app import app

fake = faker.Faker("ru_RU")
ENDPOINT = "http://127.0.0.1:5000"


@pytest.fixture(scope="session", autouse=True)
def setup():
    def run_app():
        app.run()

    thread = threading.Thread(target=run_app)
    thread.daemon = True
    thread.start()
    time.sleep(1)
    yield


def create_payload():
    n = fake.name().split()
    first_name = "1"
    last_name = "1"
    if len(n) == 2:
        first_name, last_name = n
    elif len(n) == 1:
        first_name = n[0]
        last_name = ""
    elif len(n) == 3:
        first_name, _, last_name = n
    email = fake.email()
    return {"first_name": first_name, "last_name": last_name, "email": email}


def test_user_create():
    payload = create_payload()
    response = requests.post(f"{ENDPOINT}/users/create", json=payload)
    assert response.status_code == 201
    data = response.json()
    response = requests.post(f"{ENDPOINT}/users/create", json=payload)
    assert response.status_code == 409

    assert data["first_name"] == payload["first_name"]
    assert data["last_name"] == payload["last_name"]
    assert data["email"] == payload["email"]
    requests.delete(f'{ENDPOINT}/users/{data["id"]}')


def test_user_get():
    payload = create_payload()
    response = requests.post(f"{ENDPOINT}/users/create", json=payload)
    assert response.status_code == 201
    data = response.json()
    user_id = data["id"]

    response = requests.get(f"{ENDPOINT}/users/{user_id}")
    assert response.status_code == 200
    data = response.json()

    assert data["first_name"] == payload["first_name"]
    assert data["last_name"] == payload["last_name"]
    assert data["email"] == payload["email"]
    requests.delete(f"{ENDPOINT}/users/{user_id}")


def test_user_get_posts():
    payload = create_payload()
    response = requests.post(f"{ENDPOINT}/users/create", json=payload)
    assert response.status_code == 201
    data = response.json()
    user_id = data["id"]

    response = requests.get(f"{ENDPOINT}/users/{user_id}/posts", json={"sort": "asc"})
    assert response.status_code == 200
    data = response.json()

    assert data["posts"] == []
    requests.post(
        f"{ENDPOINT}/posts/create", json={"author_id": user_id, "text": "Hello, World!"}
    )
    response = requests.get(f"{ENDPOINT}/users/{user_id}/posts", json={"sort": "asc"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["posts"]) == 1
    assert data["posts"][0]["text"] == "Hello, World!"

    requests.delete(f"{ENDPOINT}/users/{user_id}")
    requests.delete(f'{ENDPOINT}/posts/{data["posts"][0]["id"]}')


def test_user_leaderboard():
    coeff = 0
    response = requests.get(
        f"{ENDPOINT}/users/leaderboard", json={"type": "table", "sort": "asc"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["users"] == []
    n = 50
    users = []
    posts = []
    for i in range(n):
        payload = create_payload()
        response = requests.post(f"{ENDPOINT}/users/create", json=payload)
        if response.status_code == 409:
            coeff -= 1
            continue
        assert response.status_code == 201
        data = response.json()
        user_id = data["id"]
        users.append(user_id)
        response = requests.post(
            f"{ENDPOINT}/posts/create",
            json={"author_id": user_id, "text": "Hello, World!"},
        )
        posts.append(response.json()["id"])
        reactions = random.randint(1, 10)
        for j in range(reactions):
            r = requests.post(
                f"{ENDPOINT}/posts/3/reaction",
                json={"user_id": user_id, "reaction": "like"},
            )
        response = requests.get(
            f"{ENDPOINT}/users/leaderboard", json={"type": "table", "sort": "asc"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["users"]) == i + 1 + coeff
        response = requests.get(f"{ENDPOINT}/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["total_reactions"] == reactions
    time.sleep(10)
    for i in users:
        requests.delete(f"{ENDPOINT}/users/{i}")
    for i in posts:
        requests.delete(f"{ENDPOINT}/posts/{i}")
