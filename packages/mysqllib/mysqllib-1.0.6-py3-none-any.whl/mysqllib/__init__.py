import time
from typing import Optional, Any, Dict, List, Tuple

import pymysql

from mysqllib.err import DatabaseError
from mysqllib.generator import condition_generator, ConditionsType

JoinType = Optional[List[Tuple[str, str, str]]]

_connection_attempts = 10
_connection_attempts_sleep = 1
_connection = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': '',
    'password': '',
    'database': ''
}


def connect(
        user: str,
        password: str,
        database: str,
        host: str = '127.0.0.1',
        port: int = 3306
):
    global _connection

    _connection = {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'database': database
    }


def get_connection(attempts: Any = 'auto') -> pymysql.Connection:
    global _connection_attempts, _connection_attempts_sleep, _connection

    if attempts == 'auto':
        attempts = _connection_attempts

    if attempts is not None:
        for attempt in range(attempts):
            try:
                return get_connection(attempts=None)
            except DatabaseError:
                time.sleep(_connection_attempts_sleep)

    try:
        return pymysql.connect(
            host=_connection['host'],
            user=_connection['user'],
            password=_connection['password'],
            database=_connection['database'],
            port=_connection['port']
        )
    except pymysql.MySQLError as e:
        raise DatabaseError(str(e))


def fetchone(query, args=None) -> Optional[dict]:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, args)
            row = cursor.fetchone()

            if not row:
                return None

            column_names = [desc[0] for desc in cursor.description]
            return dict(zip(column_names, row))
    except pymysql.MySQLError as e:
        raise DatabaseError(str(e))
    finally:
        connection.close()


def fetchall(query, args=None) -> Optional[list]:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, args)
            rows = cursor.fetchall()

            if not rows:
                return None

            column_names = [desc[0] for desc in cursor.description]
            return [dict(zip(column_names, row)) for row in rows]
    except pymysql.MySQLError as e:
        raise DatabaseError(str(e))
    finally:
        connection.close()


def execute(query, args=None) -> bool:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, args)
        connection.commit()

        return True
    except pymysql.MySQLError as e:
        raise DatabaseError(str(e))
    finally:
        connection.close()


def find(
        table: str,
        conditions: ConditionsType = None,
        columns='*',
        joins: JoinType = None,
        order_by=None
) -> dict:
    """
    Find one
    """
    join_clauses = ""
    where_clause = ""
    order_by_clause = ""
    values = ()

    if joins:
        join_clauses = " ".join(
            [f"{join_type} JOIN {join_table} ON {on_condition}" for join_type, join_table, on_condition in joins]
        )
    if conditions:
        condition_str, values = condition_generator(conditions)
        where_clause = f"WHERE {condition_str}"
    if order_by:
        order_by_clause = f"ORDER BY {order_by}"

    sql = f"SELECT {columns} FROM {table} {join_clauses} {where_clause} {order_by_clause} LIMIT 1"

    fetch = fetchone(sql, values)

    if not fetch:
        return {}

    return fetch


def findall(
        table: str,
        conditions: ConditionsType = None,
        columns='*',
        joins: JoinType = None,
        group_by=None,
        order_by=None,
        limit=None
) -> list:
    """
    Find all
    """
    join_clauses = ""
    where_clause = ""
    order_by_clause = ""
    group_by_clause = ""
    limit_clause = ""
    values = ()

    if joins:
        join_clauses = " ".join(
            [f"{join_type} JOIN {join_table} ON {on_condition}" for join_type, join_table, on_condition in joins]
        )
    if conditions:
        condition_str, values = condition_generator(conditions)
        where_clause = f"WHERE {condition_str}"
    if group_by:
        group_by_clause = f"GROUP BY {group_by}"
    if order_by:
        order_by_clause = f"ORDER BY {order_by}"
    if limit:
        limit_clause = f"LIMIT {limit}"

    sql = f"SELECT {columns} FROM {table} {join_clauses} {where_clause} {group_by_clause} {order_by_clause} {limit_clause}"

    fetch = fetchall(sql, values)

    if not fetch:
        return []

    return fetch


def update(
        table: str,
        data: Dict[str, any],
        conditions: ConditionsType = None
) -> bool:
    where_clause = ""
    set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
    values = list(data.values())

    if conditions:
        condition_str, condition_values = condition_generator(conditions)
        where_clause = f"WHERE {condition_str}"
        values.extend(condition_values)

    sql = f"UPDATE {table} SET {set_clause} {where_clause}"

    return execute(sql, values)


def delete(
        table: str,
        conditions: ConditionsType = None
):
    where_clause = ""
    values = ()

    if conditions:
        condition_str, values = condition_generator(conditions)
        where_clause = f"WHERE {condition_str}"

    sql = f"DELETE FROM {table} {where_clause}"

    return execute(sql, values)


def create(
        table: str,
        data: Dict[str, any]
) -> bool:
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["%s"] * len(data))
    values = list(data.values())

    sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

    return execute(sql, values)
