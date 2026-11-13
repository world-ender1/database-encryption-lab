# tests/test_init_env.py
from pathlib import Path

import pytest
from dotenv import dotenv_values

from app.key_manager import decode_key
from scripts import init_env

H4 = {"DATABASE_URL", "POSTGRES_PASSWORD", "ENCRYPTION_KEY_B64", "KEY_VERSION",
      "ADMIN_TOKEN", "VIEWER_TOKEN", "API_PORT", "DB_PORT"}
SECRETS = ("ENCRYPTION_KEY_B64", "ADMIN_TOKEN", "VIEWER_TOKEN", "POSTGRES_PASSWORD")
ENV_EXAMPLE = Path(__file__).resolve().parent.parent / ".env.example"


@pytest.fixture
def env_file(tmp_path):
    path = tmp_path / ".env"
    assert init_env.main(path) == 0
    return path


def test_env_has_exactly_h4_vars(env_file):
    assert set(dotenv_values(env_file)) == H4


def test_env_values_are_usable(env_file):
    e = dotenv_values(env_file)
    assert len(decode_key(e["ENCRYPTION_KEY_B64"])) == 32
    assert (e["KEY_VERSION"], e["API_PORT"], e["DB_PORT"]) == ("v1", "8000", "55432")
    assert e["DATABASE_URL"] == (
        f"postgresql+psycopg://demo:{e['POSTGRES_PASSWORD']}@127.0.0.1:55432/encryption_demo")
    assert e["ADMIN_TOKEN"] != e["VIEWER_TOKEN"]
    assert all(len(e[k]) >= 32 for k in ("ADMIN_TOKEN", "VIEWER_TOKEN", "POSTGRES_PASSWORD"))


def test_existing_env_is_not_overwritten(env_file, capsys):
    before = env_file.read_bytes()
    assert init_env.main(env_file) == 0
    assert env_file.read_bytes() == before
    assert "already exists" in capsys.readouterr().out


def test_each_run_generates_new_secrets(tmp_path):
    a, b = tmp_path / "a.env", tmp_path / "b.env"
    init_env.main(a)
    init_env.main(b)
    ea, eb = dotenv_values(a), dotenv_values(b)
    assert all(ea[k] != eb[k] for k in SECRETS)


def test_output_is_ascii_and_has_no_secret(tmp_path, capsys):
    path = tmp_path / ".env"
    init_env.main(path)
    out = capsys.readouterr().out
    assert out.isascii()
    e = dotenv_values(path)
    assert not any(e[k] in out for k in SECRETS)


def test_env_example_has_h4_vars_without_real_values():
    example = dotenv_values(ENV_EXAMPLE)
    assert set(example) == H4
    assert all(example[k].startswith("<") for k in SECRETS)
