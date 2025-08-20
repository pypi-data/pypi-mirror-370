from contextlib import _GeneratorContextManager, contextmanager
from typing import Callable, Generator

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

DBSessionMaker = Callable[[], _GeneratorContextManager[Session]]


def get_session_maker(engine: Engine) -> DBSessionMaker:
    session_maker = sessionmaker(bind=engine)

    @contextmanager
    def session_manager() -> Generator[Session, None, None]:
        session = session_maker()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    return session_manager
