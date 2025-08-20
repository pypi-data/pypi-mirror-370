from strats import Strats, StratsConfig


def create_app():
    config = StratsConfig(
        install_access_log=True,
        drop_access_log_paths=("/healthz", "/livez", "/readyz"),
    )
    return Strats(config=config).create_app()
