from fastapi import FastAPI

from strats.core.kernel import Kernel

from .middleware import AccessLogMiddleware
from .router import get_kernel, router

BANNER = r"""
 _______ _______  ______ _______ _______ _______
 |______    |    |_____/ |_____|    |    |______
 ______|    |    |     \ |     |    |    ______|
"""


def kernel_getter_factory(kernel):
    def kernel_getter():
        return kernel

    return kernel_getter


class Strats(Kernel):
    def create_app(self) -> FastAPI:
        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_kernel] = kernel_getter_factory(self)

        if self.config.install_access_log:
            app.add_middleware(
                AccessLogMiddleware,
                drop_paths=self.config.drop_access_log_paths,
            )
        return app
