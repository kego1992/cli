# -*- coding: utf-8 -*-

from cli.main import cli

from click.testing import CliRunner

from pytest import fixture


@fixture
def runner():
    return CliRunner()


def test_choose_template(runner):
    res = runner.invoke(cli, ['bootstrap'])
    assert res.exit_code == 0
    assert 'Choose a template' in res.output
