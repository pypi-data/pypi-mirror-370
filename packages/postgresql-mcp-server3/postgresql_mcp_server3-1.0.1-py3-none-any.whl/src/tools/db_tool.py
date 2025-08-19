"""
Database Utility Functions

Provides database utility functions related to SQL execution.
"""
from src.utils.db_operate import execute_sql
from src.utils.logger_util import logger
import random, string


async def sql_exec(sql: str):
    """
    Execute any SQL statement (SELECT/INSERT/UPDATE/DELETE)
    """
    logger.info(f"Executing SQL: {sql}")
    try:
        result = await execute_sql(sql)
        logger.info(f"SQL executed successfully, returned {len(result) if isinstance(result, list) else result} rows/affected rows")
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"SQL execution failed: {e}")
        return {"success": False, "error": str(e)}


async def generate_test_data(table, columns, num):
    logger.info(f"Starting to generate {num} test records for table '{table}'")
    logger.debug(f"Target table {table} columns: {columns}")

    try:
        for i in range(num):
            values = []
            for _ in columns:
                # Simple example: all use 8-character random strings
                random_value = ''.join(random.choices(string.ascii_letters, k=8))
                values.append(random_value)

            # PostgreSQL uses $1, $2, $3... for placeholders
            placeholders = ','.join([f'${j+1}' for j in range(len(columns))])
            sql = f'INSERT INTO "{table}" ({",".join([f'"{col}"' for col in columns])}) VALUES ({placeholders})'

            logger.debug(f"Inserting row {i + 1}/{num}: {dict(zip(columns, values))}")
            await execute_sql(sql, values)

        logger.info(f"Successfully generated {num} test records for table '{table}'")
        return {
            "success": True,
            "result": f"Successfully generated {num} test records for table '{table}'",
            "message": "Test data generation completed"
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to generate test data for table '{table}': {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "message": "Test data generation failed"
        }