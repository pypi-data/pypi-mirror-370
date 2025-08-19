from src.utils.db_config import load_activate_db_config
from src.utils.db_operate import execute_sql
from src.utils.logger_util import logger


async def generate_database_tables():
    try:
        # Get all table names from PostgreSQL information_schema
        tables_result = await execute_sql("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        """)
        tables_info = []

        for table_row in tables_result:
            table_name = table_row['table_name']

            # Get table structure using PostgreSQL information_schema
            describe_result = await execute_sql(f"""
                SELECT 
                    column_name as "Field",
                    data_type as "Type",
                    is_nullable as "Null",
                    column_default as "Default",
                    CASE 
                        WHEN column_name IN (
                            SELECT column_name 
                            FROM information_schema.key_column_usage 
                            WHERE table_name = '{table_name}' 
                            AND table_schema = 'public'
                        ) THEN 'PRI'
                        ELSE ''
                    END as "Key"
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                AND table_schema = 'public'
                ORDER BY ordinal_position
            """)

            # Get table record count
            count_result = await execute_sql(f'SELECT COUNT(*) as count FROM "{table_name}"')
            record_count = count_result[0]['count'] if count_result else 0

            tables_info.append({
                "name": table_name,
                "columns": describe_result,
                "record_count": record_count
            })

        logger.info(f"Successfully obtained information for {len(tables_info)} tables")
        return {
            "uri": "database://tables",
            "mimeType": "application/json",
            "text": str(tables_info)
        }
    except Exception as e:
        logger.error(f"Failed to get database table information: {e}")
        return {
            "uri": "database://tables",
            "mimeType": "application/json",
            "text": f"Error: {str(e)}"
        }

async def generate_database_config():

    active_db, db_config = load_activate_db_config()

    # Hide sensitive information
    safe_config = {
        "dbInstanceId": active_db.db_instance_id,
        "dbHost": active_db.db_host,
        "dbPort": active_db.db_port,
        "dbDatabase": active_db.db_database,
        "dbUsername": active_db.db_username,
        "dbPassword": "***hidden***",
        "dbType": active_db.db_type,  # Get from active_db, not db_config
        "dbVersion": active_db.db_version,  # Get from active_db, not db_config
        "pool_size": db_config.db_pool_size,
        "max_overflow": db_config.db_max_overflow,
        "pool_timeout": db_config.db_pool_timeout,
    }
    logger.info("Successfully obtained database configuration information")
    logger.info(f"Database configuration: {safe_config}")
    return safe_config