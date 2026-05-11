import os
import subprocess
import sys

import uvicorn


def run_migrations() -> None:
    if os.environ.get("SKIP_MIGRATIONS", "").lower() in {"1", "true", "yes"}:
        return
    root = os.path.dirname(os.path.abspath(__file__))
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        check=True,
        cwd=root,
    )


def run_optional_seed() -> None:
    if os.environ.get("AUTO_SEED", "").lower() not in {"1", "true", "yes"}:
        return
    if os.environ.get("SKIP_SEED", "").lower() in {"1", "true", "yes"}:
        return
    root = os.path.dirname(os.path.abspath(__file__))
    result = subprocess.run(
        [sys.executable, "scripts/seed_db.py"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        msg = (result.stderr or result.stdout or "").strip()
        print(
            "AUTO_SEED failed; home catalog may be empty. Run: poetry run python scripts/seed_db.py",
            file=sys.stderr,
        )
        if msg:
            print(msg, file=sys.stderr)


def main() -> None:
    run_migrations()
    run_optional_seed()
    os.environ.setdefault("HOST", "0.0.0.0")
    host = os.environ["HOST"]
    port = int(os.environ.get("PORT", "8000"))
    reload_flag = os.environ.get("UVICORN_RELOAD", "").lower() in {"1", "true", "yes"}

    publish = os.environ.get("DOCKER_PUBLISH_HOST", "").strip()
    show_host = publish if publish and publish != "0.0.0.0" else "127.0.0.1"
    if host == "0.0.0.0":
        print(
            f"Open in your browser (this machine): http://{show_host}:{port}/",
            file=sys.stderr,
        )
        if publish == "0.0.0.0":
            print(
                "Published on all interfaces; from another device use this computer's LAN IP.",
                file=sys.stderr,
            )

    uvicorn.run("main:app", host=host, port=port, reload=reload_flag)


if __name__ == "__main__":
    main()
