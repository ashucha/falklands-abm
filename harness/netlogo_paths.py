from __future__ import annotations

import os
from pathlib import Path

# Repository root (parent of harness/).
_REPO_ROOT = Path(__file__).resolve().parent.parent


def _has_netlogo_app(home: Path) -> bool:
    app = home / "app"
    return app.is_dir() and any(app.glob("*.jar"))


def netlogo_java_cwd(install_root: Path) -> Path:
    """Directory that contains app/*.jar (for java -cp app/* ...)."""
    if (install_root / "app").is_dir():
        return install_root
    nested = install_root / "Contents" / "Java"
    if (nested / "app").is_dir():
        return nested
    return install_root


def resolve_netlogo_home(cli_path: Path | None) -> Path:
    """
    Resolve NetLogo install root for pyNetLogo.

    Order: --netlogo-home, NETLOGO_HOME, then a sibling folder next to the
    course directory whose name contains 'netlogo' and contains app/*.jar
    (matches a portable tree like ../NetLogo 7.0.3/).
    """
    if cli_path is not None:
        p = cli_path.expanduser().resolve()
        if _has_netlogo_app(p):
            return p
        raise RuntimeError(
            f"--netlogo-home must be a NetLogo install directory containing app/*.jar: {p}"
        )

    env = os.environ.get("NETLOGO_HOME", "").strip()
    if env:
        p = Path(env).expanduser().resolve()
        if _has_netlogo_app(p):
            return p
        raise RuntimeError(
            f"NETLOGO_HOME must point to a NetLogo install directory containing app/*.jar: {p}"
        )

    base = _REPO_ROOT.parent.parent
    if base.is_dir():
        candidates = sorted(
            (p for p in base.iterdir() if p.is_dir() and "netlogo" in p.name.lower()),
            key=lambda p: p.name.lower(),
            reverse=True,
        )
        for p in candidates:
            if _has_netlogo_app(p):
                return p.resolve()

    raise RuntimeError(
        "Could not find NetLogo (expected app/*.jar). Set NETLOGO_HOME, pass "
        "--netlogo-home, or keep a portable NetLogo folder next to your course directory."
    )
