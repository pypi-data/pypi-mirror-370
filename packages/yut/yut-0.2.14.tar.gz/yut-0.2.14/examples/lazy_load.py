from contextlib import contextmanager
from typing import Generator

from loguru import logger
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.engine import Engine

import yus_demo
from ndw import get_db, get_qm


@contextmanager
def db_session(engine: Engine) -> Generator:
    """上下文管理器用于自动处理数据库会话"""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def lazy_query(session, query, batch_size=100) -> Generator:
    """
    使用 SQLAlchemy 的生成器懒加载数据库结果

    :param session: SQLAlchemy 会话对象
    :param query: SQLAlchemy 查询对象 (Select 或 ORM 查询)
    :param batch_size: 每次从数据库获取的批处理大小
    """
    # 创建可滚动的服务器端游标
    result = session.execute(query.execution_options(yield_per=batch_size))

    # 逐批获取结果
    while True:
        # 获取下一批结果
        batch = result.fetchmany(batch_size)
        if not batch:
            break  # 没有更多数据时退出循环

        # 逐行生成结果
        for row in batch:
            # 如果是 ORM 查询，返回实体对象；如果是核心查询，返回行对象
            yield row[0] if isinstance(row, tuple) and hasattr(row[0], '__table__') else row


# 示例使用
if __name__ == "__main__":
    yus_demo.init_env()
    engine = get_db().engine

    # 使用Lazy Load
    with db_session(engine) as session:
        qs = get_qm().get_selection('DW_AR')
        # 创建查询
        core_query = qs._create_query()

        # 获取懒加载生成器
        core_generator = lazy_query(session, core_query, batch_size=100)

        logger.info("Processing using SQL Core expressions:")
        for idx, row in enumerate(core_generator, 1):
            logger.info(f"{idx:>6d}: [#{row.AR_ID:06d}] {row.AR_NUM:<30s} - {row.SCT_ID:<10d} {row.AMOUNT:>20,.2f}")

            # 模拟提前退出
            if idx == 500:
                print("Stopped after 150 records")
                break

    # 使用普通查询
    qs = get_qm().get_selection('DW_AR')
    # 创建查询
    q = qs._create_query()
    logger.info("使用普通查询:")
    for idx, row in enumerate(q.all()):
        logger.info(f"{idx:>6d}: [#{row.AR_ID:06d}] {row.AR_NUM:<30s} - {row.SCT_ID:<10d} {row.AMOUNT:>20,.2f}")

        # 模拟提前退出
        if idx == 500:
            print("Stopped after 150 records")
            break
