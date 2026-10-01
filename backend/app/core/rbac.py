from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.core.auth import get_current_user


def require_role(
    required_role: str,
) -> Callable:

    async def role_checker(
        current_user: dict = Depends(get_current_user),
    ) -> dict:

        current_role = current_user.get("role")

        if current_role != required_role:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Role '{required_role}' is required "
                    "to access this resource."
                ),
            )

        return current_user

    return role_checker


async def require_admin(
    current_user: dict = Depends(
        require_role("admin")
    ),
) -> dict:

    return current_user