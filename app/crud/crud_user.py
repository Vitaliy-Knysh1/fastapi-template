from __future__ import annotations

from threading import Lock

from app.crud.base import CRUDBase
from app.schemas.user import UserCreate, UserPublic

_lock = Lock()
_users: dict[int, dict[str, int | str]] = {}
_next_id: int = 1


class CRUDUser(CRUDBase):
    def create(self, obj: UserCreate) -> UserPublic:
        global _next_id
        with _lock:
            uid = _next_id
            _next_id += 1
            row: dict[str, int | str] = {"id": uid, "email": obj.email, "name": obj.name}
            _users[uid] = row
        return UserPublic.model_validate(row)

    def get(self, user_id: int) -> UserPublic | None:
        row = _users.get(user_id)
        return UserPublic.model_validate(row) if row else None

    def get_multi(self) -> list[UserPublic]:
        return [UserPublic.model_validate(r) for r in _users.values()]

    def replace(self, user_id: int, obj: UserCreate) -> UserPublic | None:
        """Full replace (used for PUT)."""
        with _lock:
            if user_id not in _users:
                return None
            _users[user_id] = {"id": user_id, "email": obj.email, "name": obj.name}
            row = _users[user_id]
        return UserPublic.model_validate(row)

    def delete(self, user_id: int) -> bool:
        with _lock:
            return _users.pop(user_id, None) is not None


crud_user = CRUDUser()
