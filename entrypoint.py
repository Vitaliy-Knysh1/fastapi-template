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


def main() -> None:
    run_migrations()
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    reload_flag = os.environ.get("UVICORN_RELOAD", "").lower() in {"1", "true", "yes"}

    uvicorn.run("app.main:app", host=host, port=port, reload=reload_flag)


if __name__ == "__main__":
    main()
