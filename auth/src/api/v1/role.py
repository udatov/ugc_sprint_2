from db.basedb import get_session
from db.models.user import User
from fastapi import APIRouter, Depends, HTTPException, Query, status
from services.auth import get_superuser
from services.role import RoleService, get_role_service
from services.user import UserService, get_user_service
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/assign")
async def assign_role(
    user_login: str = Query(..., description="The login of the user"),
    role_name: str = Query(..., description="The role to be assigned"),
    role_service: RoleService = Depends(get_role_service),
    user_service: UserService = Depends(get_user_service),
    session: AsyncSession = Depends(get_session),
    superuser: User = Depends(get_superuser),
) -> dict:
    """
    Assign a role to a user.

    **Requires superuser privileges.**

    **Endpoint**: POST `/assign`

    :param user_login: Login of the user to whom the role will be assigned.
    :param role_name: The name of the role to assign.
    :param role_service: The role service to manage roles.
    :param user_service: The user service to manage users.
    :param session: The database session.
    :param superuser: The current superuser making the request.
    :return: A success message indicating the role assigned to the user.
    :raises HTTPException: If the user or role is not found, or if the user already has the role.
    """
    target_user = await user_service.get_by_login(session, user_login)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found!"
        )

    role = await role_service.get_by_name(session, role_name)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found!"
        )

    user_roles = await role_service.get_user_roles(session, target_user.id)
    if any(user_role.role_id == role.id for user_role in user_roles):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User '{user_login}' already has the role '{role_name}'!",
        )

    await role_service.assign_role(session, target_user.id, role.id)
    return {
        "msg": f"Role '{role_name}' assigned to user '{user_login}'. Please re-signin!"
    }


@router.post("/revoke")
async def revoke_role(
    user_login: str = Query(..., description="The login of the user"),
    role_name: str = Query(..., description="The role to be revoked"),
    role_service: RoleService = Depends(get_role_service),
    user_service: UserService = Depends(get_user_service),
    session: AsyncSession = Depends(get_session),
    superuser: User = Depends(get_superuser),
) -> dict:
    """
    Revoke a role from a user.

    **Requires superuser privileges.**

    **Endpoint**: POST `/revoke`

    :param user_login: Login of the user whose role will be revoked.
    :param role_name: The name of the role to revoke.
    :param role_service: The role service to manage roles.
    :param user_service: The user service to manage users.
    :param session: The database session.
    :param superuser: The current superuser making the request.
    :return: A success message indicating the role revoked from the user.
    :raises HTTPException: If the user or role is not found, or if the user does not have the role.
    """
    target_user = await user_service.get_by_login(session, user_login)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found!"
        )

    role = await role_service.get_by_name(session, role_name)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found!"
        )

    user_roles = await role_service.get_user_roles(session, target_user.id)
    if any(user_role.role_id == role.id for user_role in user_roles):
        await role_service.revoke_role(session, target_user.id, role.id)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User '{user_login}' does not have the role '{role_name}'!",
        )

    return {
        "msg": f"Role '{role_name}' revoked from user '{user_login}'. Please re-signin!"
    }
