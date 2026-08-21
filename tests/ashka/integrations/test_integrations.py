from types import SimpleNamespace

from ashka.integrations import __all__, get_container, setup_dishka

from aiogram import Router
from aiohttp.web_app import Application
from dishka import AsyncContainer, Container, make_async_container, make_container
from fastapi import FastAPI
from flask import Flask
from litestar import Litestar
from pytest import fixture, raises
from sanic import Config, Sanic
from starlette.applications import Starlette


@fixture
def sanic():
    return Sanic(__name__)


@fixture
def flask():
    return Flask(__name__)


@fixture
def fastapi():
    return FastAPI()


@fixture
def starlette():
    return Starlette()


@fixture
def aiohttp():
    return Application()


@fixture
def litestar():
    return Litestar()


@fixture
def aiogram():
    return Router()


@fixture
def async_container():
    return make_async_container()


@fixture
def container():
    return make_container()


def test_sanic(async_container: AsyncContainer, sanic: Sanic[Config, SimpleNamespace]):
    setup_dishka(async_container, sanic)
    assert get_container(sanic) is async_container


def test_flask(container: Container, flask: Flask):
    setup_dishka(container, flask)
    assert get_container(flask) is container


def test_fastapi(async_container: AsyncContainer, fastapi: FastAPI):
    setup_dishka(async_container, fastapi)
    assert get_container(fastapi) is async_container


def test_starlette(async_container: AsyncContainer, starlette: Starlette):
    setup_dishka(async_container, starlette)
    assert get_container(starlette) is async_container


def test_aiohttp(async_container: AsyncContainer, aiohttp: Application):
    setup_dishka(async_container, aiohttp)
    assert get_container(aiohttp) is async_container


def test_litestar(async_container: AsyncContainer, litestar: Litestar):
    setup_dishka(async_container, litestar)
    assert get_container(litestar) is async_container


def test_aiogram(async_container: AsyncContainer, aiogram: Router):
    setup_dishka(async_container, aiogram)
    assert get_container(aiogram) is async_container


def test_import_error(async_container: AsyncContainer, fake_app: object = object()):
    with raises(ImportError):
        setup_dishka(async_container, fake_app)

    with raises(ImportError):
        get_container(fake_app)


def test_all():
    all = list(__all__)
    all.remove("get_container")
    all.remove("setup_dishka")

    for module in all:
        assert "test_" + module in globals()
