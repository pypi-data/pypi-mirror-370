from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, AsyncGenerator, Dict, Optional, Tuple

from smartutils.config.const import ConfKey
from smartutils.config.schema.mysql import MySQLConf
from smartutils.ctx import CTXKey, CTXVarManager
from smartutils.design import singleton
from smartutils.error.sys import DatabaseError
from smartutils.infra.db.sqlalchemy_cli import AsyncDBCli, db_commit, db_rollback
from smartutils.infra.resource.manager.manager import CTXResourceManager
from smartutils.init.factory import InitByConfFactory
from smartutils.init.mixin import LibraryCheckMixin

try:
    from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction
except ImportError:
    ...

if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction

__all__ = ["MySQLManager"]


@singleton
@CTXVarManager.register(CTXKey.DB_MYSQL)
class MySQLManager(LibraryCheckMixin, CTXResourceManager[AsyncDBCli]):
    def __init__(self, confs: Optional[Dict[str, MySQLConf]] = None):
        self.check(conf=confs)
        assert confs

        resources = {k: AsyncDBCli(conf, f"mysql_{k}") for k, conf in confs.items()}
        super().__init__(
            resources=resources,
            ctx_key=CTXKey.DB_MYSQL,
            success=db_commit,
            fail=db_rollback,
            error=DatabaseError,
        )

    @property
    def curr(self) -> AsyncSession:
        return super().curr[0]

    # @asynccontextmanager
    # async def session(
    #     self, key: ConfKey = ConfKey.GROUP_DEFAULT, use_transaction: bool = False
    # ) -> AsyncGenerator[Tuple[AsyncSession, Optional[AsyncSessionTransaction]], None]:
    #     async with self._resources[key].db(use_transaction) as session:
    #         yield session


@InitByConfFactory.register(ConfKey.MYSQL)
def _(conf):
    MySQLManager(conf)
