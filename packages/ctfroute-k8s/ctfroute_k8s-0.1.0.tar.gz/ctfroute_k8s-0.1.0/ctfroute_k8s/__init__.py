from functools import wraps
from logging import getLogger

from cloudcoil.apimachinery import ObjectMeta
from cloudcoil.errors import ResourceConflict, ResourceNotFound

# cloudcoil generated models from crds.yaml
from .models.v1 import Gate
from .models.v1 import GateSpec as RawGateSpec  # Spec for raw gates
from .models.v1 import GateSpecModel as ConnGateSpec  # Spec for conn gates
from .models.v1 import GateSpecModel1 as GateSpec  # Actual gate spec

LOGGER = getLogger(__name__)


def log_errors(func):
    @wraps(func)
    def with_logging(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except ResourceConflict as e:
            LOGGER.exception("Could not create gate due to resource conflict")
            raise e
        except ResourceNotFound as e:
            LOGGER.exception("Could not find resource")
            raise e


@log_errors
async def add_raw_gate(
    name: str, namespace: str, conn_src: str, conn_dst: str, rule: str
):
    spec = RawGateSpec(
        type="raw",
        conn_src=conn_src,
        conn_dst=conn_dst,
        rule=rule,
    )
    gate = Gate(
        metadata=ObjectMeta(
            name=name,
            namespace=namespace,
        ),
        spec=GateSpec(spec),
    )
    await gate.async_create()


@log_errors
async def add_connection_gate(
    name: str,
    namespace: str,
    conn_src: str,
    conn_dst: str,
    expression: str | None = None,
):
    spec = ConnGateSpec(
        type="connection",
        conn_src=conn_src,
        conn_dst=conn_dst,
        expression=expression,
    )
    gate = Gate(
        metadata=ObjectMeta(
            name=name,
            namespace=namespace,
        ),
        spec=GateSpec(spec),
    )
    await gate.async_create()


@log_errors
async def remove_gate(name: str, namespace: str):
    gate = Gate.get(name=name, namespace=namespace)
    await gate.async_remove()
