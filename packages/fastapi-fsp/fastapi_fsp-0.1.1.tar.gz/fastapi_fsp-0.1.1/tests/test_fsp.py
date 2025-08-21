from fastapi.testclient import TestClient
from sqlmodel import Session

from tests.main import Hero


def test_paginate_heroes(session: Session, client: TestClient):
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
    hero_2 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)
    session.add(hero_1)
    session.add(hero_2)
    session.commit()

    response = client.get("/heroes/?page=1&per_page=1")

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1


def test_filter_heroes(session: Session, client: TestClient):
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
    hero_2 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)
    session.add(hero_1)
    session.add(hero_2)
    session.commit()

    response = client.get("/heroes/?field=name&operator=eq&value=Deadpond")

    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["name"] == hero_1.name
    assert data[0]["secret_name"] == hero_1.secret_name
    assert data[0]["age"] == hero_1.age
    assert data[0]["id"] == hero_1.id


def test_sort_heroes(session: Session, client: TestClient):
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
    hero_2 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)
    session.add(hero_1)
    session.add(hero_2)
    session.commit()

    response = client.get("/heroes/?sort_by=name&order=asc")
    data = response.json()["data"]
    assert data[0]["name"] == hero_1.name
    assert data[1]["name"] == hero_2.name

    response = client.get("/heroes/?sort_by=name&order=desc")
    data = response.json()["data"]
    assert data[0]["name"] == hero_2.name
    assert data[1]["name"] == hero_1.name
