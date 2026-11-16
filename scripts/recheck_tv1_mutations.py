"""Recheck 19 documented TV1 mutants in a temporary copy, never in the live tree.

Run with the project test dependencies installed:
    python -m scripts.recheck_tv1_mutations
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ("tests/test_key_manager.py", "tests/test_crypto.py",
         "tests/test_auth.py", "tests/test_init_env.py")
CRYPTO = "app/crypto_service.py"
KEY = "app/key_manager.py"
AUTH = "app/auth.py"
ENV = "scripts/init_env.py"

# Each tuple is (file, exact old text, replacement). M4 intentionally has two edits.
MUTANTS = {
    "M1": [(CRYPTO, "nonce = os.urandom(NONCE_SIZE)", "nonce = bytes(NONCE_SIZE)")],
    "M2": [(CRYPTO, "self._aad(student_id, field, self.key_version))",
            "None)")],
    "M3": [(CRYPTO, 'f"student:{student_id}|field:{field}|key:{key_version}"',
            'f"record:{student_id}|field:{field}|key:{key_version}"')],
    "M4": [(CRYPTO, "if ev.key_version != self.key_version:", "if False:"),
           (CRYPTO, "self._aad(student_id, field, ev.key_version))",
            "self._aad(student_id, field, self.key_version))")],
    "M5": [(CRYPTO, "if len(ev.nonce) != NONCE_SIZE:", "if False:")],
    "M6": [(CRYPTO, 'raise IntegrityFailure("Authentication failed") from exc',
            "raise exc")],
    "M7": [(CRYPTO, "self._aes = AESGCM(key)", "self._aes = AESGCM(bytes(32))")],
    "M8": [(CRYPTO, "if len(key) != KEY_SIZE:", "if False:")],
    "M9": [(KEY, "base64.b64decode(encoded_key, validate=True)",
            "base64.b64decode(encoded_key, validate=False)")],
    "M10": [(KEY, "if len(key) != KEY_SIZE:", "if len(key) < KEY_SIZE:")],
    "M11": [(KEY, 'raise ValueError(f"Key phải đúng {KEY_SIZE} byte, nhận được {len(key)} byte")',
             'raise ValueError(f"Key sai độ dài: {encoded_key}")')],
    "M12": [(AUTH, 'secrets.compare_digest(a.encode("utf-8"), b.encode("utf-8"))',
             "secrets.compare_digest(a, b)")],
    "M13": [(AUTH, 'secrets.compare_digest(a.encode("utf-8"), b.encode("utf-8"))',
             "a == b")],
    "M14": [(AUTH, 'if role != "admin":', "if False:")],
    "M15": [(AUTH, 'headers={"WWW-Authenticate": "Bearer"},', "headers={ },")],
    "M16": [(AUTH, 'if creds is None:\n        raise _unauthorized()',
             'if creds is None:\n        return "viewer"')],
    "M17": [(ENV, "if env_path.exists():", "if False:")],
    "M18": [(ENV, 'f"DATABASE_URL=postgresql+psycopg://demo:{pg_password}@127.0.0.1:{DB_PORT}/encryption_demo"',
             'f"DATABASE_URL=postgresql+psycopg://demo:wrong@127.0.0.1:{DB_PORT}/encryption_demo"')],
    "M19": [(CRYPTO, 'raise IntegrityFailure("Plaintext không phải UTF-8") from exc',
             "raise exc")],
}


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="database-encryption-mutation-") as temporary:
        scratch = Path(temporary)
        for directory in ("app", "scripts", "tests"):
            shutil.copytree(ROOT / directory, scratch / directory,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        shutil.copy2(ROOT / ".env.example", scratch / ".env.example")
        results = {}
        for name, edits in MUTANTS.items():
            originals = {}
            try:
                for relative, old, new in edits:
                    path = scratch / relative
                    source = path.read_text(encoding="utf-8")
                    originals.setdefault(path, source)
                    if source.count(old) != 1:
                        raise RuntimeError(f"{name}: expected exactly one matching source fragment")
                    path.write_text(source.replace(old, new, 1), encoding="utf-8")
                process = subprocess.run(
                    [sys.executable, "-m", "pytest", *TESTS, "-q"],
                    cwd=scratch, capture_output=True, text=True,
                    encoding="utf-8", errors="replace", timeout=90,
                )
                output = process.stdout + process.stderr
                failures = re.findall(r"(?m)^FAILED (tests/\S+)", output)
                killed = bool(failures)
                results[name] = {"killed_by_test": killed,
                                 "first_failed_test": failures[0] if failures else None,
                                 "pytest_exit_code": process.returncode}
                print(name, "killed" if killed else "survived", process.returncode)
            finally:
                for path, source in originals.items():
                    path.write_text(source, encoding="utf-8")

    report = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "method": "temporary source copy; all 48 TV1 tests run for each mutant",
        "note": "M13 equality comparison is expected to survive functional tests; inspect code for compare_digest.",
        "results": results,
    }
    path = ROOT / "docs/evidence/tv1_mutation_recheck.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if len(results) == 19 and all(
        result["killed_by_test"] == (name != "M13")
        for name, result in results.items()
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
