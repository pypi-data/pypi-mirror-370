import logging

from fastapi import APIRouter, Depends, HTTPException, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from strats.core.kernel import Kernel

logger = logging.getLogger(__name__)

router = APIRouter()


def get_kernel() -> Kernel:
    raise NotImplementedError("get_kernel is not yet bound")


@router.get("/healthz")
def healthz():
    return "ok"


@router.get("/livez")
def livez():
    return "ok"


@router.get("/readyz")
def readyz():
    return "ok"


@router.get("/metrics")
def metrics(kernel: Kernel = Depends(get_kernel)):
    data = generate_latest(kernel.registry)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@router.get("/strategy", tags=["strategy"])
def get_strategy(kernel: Kernel = Depends(get_kernel)):
    return response_strategy_info(kernel)


@router.post("/strategy/start", tags=["strategy"])
async def start_strategy(kernel: Kernel = Depends(get_kernel)):
    try:
        await kernel.start_strategy()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return response_strategy_info(kernel)


@router.post("/strategy/stop", tags=["strategy"])
async def stop_strategy(kernel: Kernel = Depends(get_kernel)):
    try:
        await kernel.stop_strategy()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return response_strategy_info(kernel)


@router.get("/monitors", tags=["monitors"])
def get_monitors(kernel: Kernel = Depends(get_kernel)):
    return response_monitors_info(kernel)


@router.post("/monitors/start", tags=["monitors"])
async def start_monitors(kernel: Kernel = Depends(get_kernel)):
    try:
        await kernel.start_monitors()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return response_monitors_info(kernel)


@router.post("/monitors/stop", tags=["monitors"])
async def stop_monitors(kernel: Kernel = Depends(get_kernel)):
    try:
        await kernel.stop_monitors()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return response_monitors_info(kernel)


@router.get("/clock", tags=["clock"])
def get_clock(kernel: Kernel = Depends(get_kernel)):
    return response_clock_info(kernel)


@router.post("/clock/start", tags=["clock"])
async def start_clock(kernel: Kernel = Depends(get_kernel)):
    try:
        await kernel.start_clock()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return response_clock_info(kernel)


@router.post("/clock/stop", tags=["clock"])
async def stop_clock(kernel: Kernel = Depends(get_kernel)):
    try:
        await kernel.stop_clock()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return response_clock_info(kernel)


def response_strategy_info(kernel):
    is_running = kernel.strategy_task is not None and not kernel.strategy_task.done()
    resp = {
        "is_configured": kernel.strategy is not None,
        "is_running": is_running,
    }
    if is_running:
        resp["started_at"] = kernel.strategy_started_at
        if "__str__" in type(kernel.strategy).__dict__:
            resp["details"] = str(kernel.strategy)
    return resp


def response_monitors_info(kernel):
    res = {
        "is_configured": kernel.monitors is not None,
    }
    if kernel.monitors is not None:
        res["monitors"] = {}
        for monitor in kernel.monitors:
            is_running = (
                monitor.name in kernel.monitor_tasks
                and not kernel.monitor_tasks[monitor.name].done()
            )
            details = {
                "is_running": is_running,
            }
            if monitor.name in kernel.monitor_started_ats:
                details["started_at"] = kernel.monitor_started_ats[monitor.name]
            res["monitors"][monitor.name] = details
    return res


def response_clock_info(kernel):
    if kernel.clock.is_mock:
        return {
            "is_real": False,
            "is_running": (kernel.clock_task is not None and not kernel.clock_task.done()),
            "datetime": kernel.clock.datetime.isoformat(),
        }
    else:
        return {
            "is_real": True,
            "datetime": kernel.clock.datetime.isoformat(),
        }
