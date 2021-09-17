from app.core.dependencies import PermissionChecker
from app.utils.permissions import permissions
from fastapi import APIRouter

router = APIRouter()


allow_add_permission = PermissionChecker("add_permission")
allow_change_permission = PermissionChecker("change_permission")
allow_delete_permission = PermissionChecker("delete_permission")


@router.get(
    "/", response_description="List all permissions"
)
async def list_permissions():
    return permissions
