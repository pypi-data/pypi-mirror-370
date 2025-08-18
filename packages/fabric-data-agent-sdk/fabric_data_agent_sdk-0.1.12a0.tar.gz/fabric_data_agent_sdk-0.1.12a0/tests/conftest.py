def pytest_configure(config):
    """Early initialization before imports."""
    import os

    os.environ["REPORT_USAGE_TELEMETRY"] = "false"
    os.environ["fabric_fake_usage_telemetry"] = "true"


from pytest import fixture
import uuid
from .auth import get_fabric_info


@fixture(scope="session")
def fabric_info():
    """Get the authentication context for Fabric"""
    return get_fabric_info()


@fixture(scope="session")
def fabric_named_workspace(fabric_info):
    """Get or creates a workspace (dev name or fixed for CI/CD) and the authentication context for Fabric"""
    from sempy.fabric._client import import_pbix_sample

    workspace_id = uuid.UUID(fabric_info["workspace_id"])

    import_pbix_sample(["AdventureWorksSempy"], workspace_id, skip_report=False)

    return fabric_info
