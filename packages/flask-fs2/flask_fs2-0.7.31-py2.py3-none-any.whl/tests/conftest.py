import io
import os

from flask import Flask
from werkzeug.datastructures import FileStorage
from flask_fs.crypto import AES256FileEncryptor


import pytest

PNG_FILE = os.path.join(os.path.dirname(__file__), "flask.png")
JPG_FILE = os.path.join(os.path.dirname(__file__), "flask.jpg")


class TestConfig:
    DEBUG = True
    TESTING = True
    MONGODB_DB = "flask-fs-test"
    MONGODB_HOST = "localhost"
    MONGODB_PORT = 27017


class TestConfigEncrypted:
    TESTING = True
    MONGODB_DB = "flask-fs-test"
    MONGODB_HOST = "localhost"
    MONGODB_PORT = 27017


class TestFlask(Flask):
    def configure(self, *storages, **configs):
        import flask_fs as fs

        for key, value in configs.items():
            self.config[key] = value
        fs.init_app(self, *storages)


@pytest.fixture
def app():
    app = TestFlask("flaskfs-tests")
    app.config.from_object(TestConfig)
    yield app


@pytest.fixture
def binfile():
    return PNG_FILE


@pytest.fixture
def pngfile():
    return PNG_FILE


@pytest.fixture
def jpgfile():
    return JPG_FILE


class Utils(object):
    def filestorage(self, filename, content, content_type=None):
        return FileStorage(
            self.file(content), filename, content_type=content_type
        )

    def file(self, content):
        if isinstance(content, bytes):
            return io.BytesIO(content)
        elif isinstance(content, str):
            return io.BytesIO(content.encode("utf-8"))
        else:
            return content


@pytest.fixture
def utils(faker):
    return Utils()


@pytest.fixture
def mock_backend(app, mocker):
    app.config["FS_BACKEND"] = "mock"
    mock = mocker.patch("flask_fs.backends.mock.MockBackend")
    mock.return_value.encryptor = None
    yield mock


@pytest.fixture
def mock_encrypted_backend(app, mocker):
    app.config["FS_BACKEND"] = "mock"
    mock = mocker.patch("flask_fs.backends.mock.MockBackend")
    mock.return_value.encryptor = AES256FileEncryptor(
        "jHEyo0GjTZDCUEnCkMcaF-LIxmnOix8b3JH633I7dls="
    )
    yield mock
