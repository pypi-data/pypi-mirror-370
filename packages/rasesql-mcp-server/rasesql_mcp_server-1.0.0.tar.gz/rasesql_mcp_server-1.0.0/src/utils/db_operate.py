from src.utils.db_pool import get_db_pool
from src.utils.logger_util import logger
import asyncpg

async def get_pooled_connection():
    """Get database connection from connection pool"""
    try:
        pool = await get_db_pool()
        conn = await pool.get_connection()
        return conn
    except Exception as e:
        logger.error(f"Failed to get connection from PostgreSQL connection pool: {e}")
        raise
async def execute_sql(sql, params=None):
    """Execute SQL statement (asynchronous version, using connection pool)"""
    conn = None
    logger.debug(f"Preparing to execute async SQL: {sql}")
    try:
        logger.debug("Getting PostgreSQL connection pool connection...")
        conn = await get_pooled_connection()

        # Execute SQL
        logger.debug("Executing async SQL query...")

        # Handle different types of SQL statements
        sql_lower = sql.strip().lower()
        if sql_lower.startswith(("select", "show", "describe", "desc")):
            # For query statements, return result set
            if params:
                result = await conn.fetch(sql, *params)
            else:
                result = await conn.fetch(sql)
            # Convert asyncpg.Record to dict list for compatibility
            result = [dict(row) for row in result]
            logger.debug(f"Async query returned {len(result)} rows of data")
        elif sql_lower.startswith(("insert", "update", "delete")):
            # For modification statements, return affected rows count
            if params:
                result = await conn.execute(sql, *params)
            else:
                result = await conn.execute(sql)
            # Extract row count from returned status string (e.g. "UPDATE 5")
            if isinstance(result, str) and ' ' in result:
                try:
                    result = int(result.split()[-1])
                except (ValueError, IndexError):
                    result = 0
            logger.debug(f"Async query affected {result} rows of data")
        else:
            # For other statements (like CREATE, DROP, etc.)
            if params:
                await conn.execute(sql, *params)
            else:
                await conn.execute(sql)
            result = "Query executed successfully"
            logger.debug("Async DDL query executed successfully")

        logger.info(f"Async SQL executed successfully: {sql[:200]}{'...' if len(sql) > 50 else ''}")
        return result

    except Exception as e:
        logger.error(f"Async SQL execution failed: {e}")
        logger.debug(f"Failed async SQL: {sql}")
        raise
    finally:
        if conn:
            pool = await get_db_pool()
            await pool.release_connection(conn)
            logger.debug("Async connection has been released back to connection pool")