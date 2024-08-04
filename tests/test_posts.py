import random
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

def create_user_payload():
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


def create_post_payload(id):
    return {"author_id": id, "text": fake.text()}


def test_post_create():
    user_payload = create_user_payload()
    user_response = requests.post(f"{ENDPOINT}/users/create", json=user_payload)
    assert user_response.status_code == 201
    user_data = user_response.json()
    user_id = user_data["id"]

    post_payload = create_post_payload(user_id)
    post_response = requests.post(f"{ENDPOINT}/posts/create", json=post_payload)
    assert post_response.status_code == 201
    post_data = post_response.json()

    assert post_data["author_id"] == user_id
    assert post_data["text"] == post_payload["text"]

    requests.delete(f"{ENDPOINT}/users/{user_id}")


def test_post_reaction():
    user_payload = create_user_payload()
    user_response = requests.post(f"{ENDPOINT}/users/create", json=user_payload)
    assert user_response.status_code == 201
    user_data = user_response.json()
    user_id = user_data["id"]

    post_payload = create_post_payload(user_id)
    post_response = requests.post(f"{ENDPOINT}/posts/create", json=post_payload)
    assert post_response.status_code == 201
    post_data = post_response.json()
    post_id = post_data["id"]

    reaction_payload = {
        "user_id": user_id,
        "reaction": random.choice(["like", "dislike"]),
    }
    reaction_response = requests.post(
        f"{ENDPOINT}/posts/{post_id}/reaction", json=reaction_payload
    )
    assert reaction_response.status_code == 200

    response = requests.get(f"{ENDPOINT}/posts/{post_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["reactions"][0] == "like" or data["reactions"][0] == "dislike"

    requests.delete(f"{ENDPOINT}/users/{user_id}")
