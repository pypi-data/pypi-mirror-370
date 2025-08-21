"""Provides a class for context manager.

Authors:
    Ryan Ignatius Hadiwijaya (ryan.i.hadiwijaya@gdplabs.id)

References:
    NONE
"""

from contextvars import ContextVar


class ContextManager:
    """A Context Manager.

    This class is used to manage the context of the application.
    """

    _tenant: ContextVar[str | None] = ContextVar("tenant_id", default=None)
    _user: ContextVar[str | None] = ContextVar("user_id", default=None)

    @classmethod
    def set_tenant(cls, tenant_id: str) -> None:
        """Set the tenant id in the context.

        Args:
            tenant_id (str): The tenant id.
        """
        cls._tenant.set(tenant_id)

    @classmethod
    def get_tenant(cls) -> str | None:
        """Get the tenant id from the context.

        Returns:
            str | None: The tenant id.
        """
        tenant_id = cls._tenant.get()
        return tenant_id

    @classmethod
    def set_user(cls, user_id: str) -> None:
        """Set the user id in the context.

        Args:
            user_id (str): The user id.
        """
        cls._user.set(user_id)

    @classmethod
    def get_user(cls) -> str | None:
        """Get the user id from the context.

        Returns:
            str | None: The user id.
        """
        return cls._user.get()
