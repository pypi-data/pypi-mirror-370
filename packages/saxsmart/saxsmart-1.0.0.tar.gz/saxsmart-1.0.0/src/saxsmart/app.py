from __future__ import annotations
import os
import pathlib
import dash
import dash_bootstrap_components as dbc
from dash.long_callback import DiskcacheManager
import diskcache

from .layout import layout
from .callbacks import register_callbacks

_ASSETS = pathlib.Path(__file__).parent / "assets"


def _resolve_cache_dir() -> pathlib.Path:
    env = os.environ.get("SAXSMART_CACHE_DIR")
    if env:
        return pathlib.Path(env)
    try:
        from platformdirs import user_cache_dir  # optional dependency

        base = pathlib.Path(user_cache_dir(appname="saxsmart", appauthor="ESRF"))
    except Exception:
        base = pathlib.Path.home() / ".cache" / "saxsmart"

    return base / "long-callbacks"


def create_app():
    cache_dir = _resolve_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)

    cache = diskcache.Cache(str(cache_dir))
    long_callback_manager = DiskcacheManager(cache)

    app = dash.Dash(
        __name__,
        assets_folder=str(_ASSETS),
        external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
        long_callback_manager=long_callback_manager,
        suppress_callback_exceptions=True,
        title="SAXSMART",
    )
    app.layout = layout
    register_callbacks(app)
    return app


app = create_app()
server = app.server


def main():
    # Optional: print where the cache lives when debugging
    if os.environ.get("SAXSMART_DEBUG"):
        print("Diskcache dir:", _resolve_cache_dir())
    app.run_server(debug=False)


if __name__ == "__main__":
    main()
