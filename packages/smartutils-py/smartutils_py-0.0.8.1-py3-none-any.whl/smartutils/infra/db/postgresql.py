from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional

from smartutils.config.const import ConfKey
from smartutils.config.schema.postgresql import PostgreSQLConf
from smartutils.ctx import CTXKey, CTXVarManager
from smartutils.design import singleton
from smartutils.error.sys import DatabaseError
from smartutils.infra.db.sqlalchemy_cli import AsyncDBCli, db_commit, db_rollback
from smartutils.infra.resource.manager.manager import CTXResourceManager
from smartutils.init.factory import InitByConfFactory
from smartutils.init.mixin import LibraryCheckMixin

try:
    from sqlalchemy.ext.asyncio import AsyncSession
except ImportError:
    ...
if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ["PostgresqlManager"]


@singleton
@CTXVarManager.register(CTXKey.DB_POSTGRESQL)
class PostgresqlManager(LibraryCheckMixin, CTXResourceManager[AsyncDBCli]):
    def __init__(self, confs: Optional[Dict[str, PostgreSQLConf]] = None):
        self.check(conf=confs)
        assert confs

        resources = {
            k: AsyncDBCli(conf, f"postgresql_{k}") for k, conf in confs.items()
        }
        super().__init__(
            resources=resources,
            ctx_key=CTXKey.DB_POSTGRESQL,
            success=db_commit,
            fail=db_rollback,
            error=DatabaseError,
        )

    @property
    def curr(self) -> AsyncSession:
        return super().curr[0]


@InitByConfFactory.register(ConfKey.POSTGRESQL)
def _(conf):
    PostgresqlManager(conf)
