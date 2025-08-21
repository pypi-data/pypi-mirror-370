import os
import tempfile
import pytest
from click.testing import CliRunner
from instagram_api.cli import instagram_api_cli
from instagram_api.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="function")
def temp_db(monkeypatch):
    db_fd, db_path = tempfile.mkstemp()
    db_url = f"sqlite:///{db_path}"
    monkeypatch.setenv('SATURN_DB_URL', db_url)
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    yield db_url
    os.close(db_fd)
    os.remove(db_path)

def test_create_user(temp_db):
    runner = CliRunner()
    result = runner.invoke(instagram_api_cli, ['create-user', 'bob', 'bob@example.com'])
    assert result.exit_code == 0
    assert "User bob created" in result.output

def test_create_post(temp_db):
    runner = CliRunner()
    runner.invoke(instagram_api_cli, ['create-user', 'bob', 'bob@example.com'])
    result = runner.invoke(instagram_api_cli, ['create-post', 'bob', 'Hello world!'])
    assert result.exit_code == 0
    assert "Post created for bob" in result.output

def test_comment(temp_db):
    runner = CliRunner()
    runner.invoke(instagram_api_cli, ['create-user', 'bob', 'bob@example.com'])
    runner.invoke(instagram_api_cli, ['create-user', 'alice', 'alice@example.com'])
    runner.invoke(instagram_api_cli, ['create-post', 'bob', 'Hello world!'])
    result = runner.invoke(instagram_api_cli, ['comment', 'alice', '1', 'Nice post!'])
    assert result.exit_code == 0
    assert "Comment added by alice to post 1" in result.output

def test_like(temp_db):
    runner = CliRunner()
    runner.invoke(instagram_api_cli, ['create-user', 'bob', 'bob@example.com'])
    runner.invoke(instagram_api_cli, ['create-post', 'bob', 'Hello world!'])
    result = runner.invoke(instagram_api_cli, ['like', 'bob', '1'])
    assert result.exit_code == 0
    assert "bob liked post 1" in result.output

def test_follow(temp_db):
    runner = CliRunner()
    runner.invoke(instagram_api_cli, ['create-user', 'bob', 'bob@example.com'])
    runner.invoke(instagram_api_cli, ['create-user', 'alice', 'alice@example.com'])
    result = runner.invoke(instagram_api_cli, ['follow', 'alice', 'bob'])
    assert result.exit_code == 0
    assert "alice now follows bob" in result.output

def test_analytics(temp_db):
    runner = CliRunner()
    runner.invoke(instagram_api_cli, ['create-user', 'bob', 'bob@example.com'])
    runner.invoke(instagram_api_cli, ['create-user', 'alice', 'alice@example.com'])
    runner.invoke(instagram_api_cli, ['follow', 'alice', 'bob'])
    runner.invoke(instagram_api_cli, ['create-post', 'bob', 'Hello world!'])
    runner.invoke(instagram_api_cli, ['like', 'alice', '1'])
    result = runner.invoke(instagram_api_cli, ['analytics'])
    assert result.exit_code == 0
    assert "Top Users by Followers" in result.output 