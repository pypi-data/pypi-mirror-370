from typing import Dict

import mysqllib
from mysqllib import JoinType
from mysqllib.generator import ConditionsType


class Database:
    def __init__(self):
        self.table = None

    def find(
            self,
            conditions: ConditionsType = None,
            columns='*',
            joins: JoinType = None,
            order_by=None
    ) -> dict:
        return mysqllib.find(
            table=self.table,
            conditions=conditions,
            columns=columns,
            joins=joins,
            order_by=order_by
        )

    def findall(
            self,
            conditions: ConditionsType = None,
            columns='*',
            joins: JoinType = None,
            group_by=None,
            order_by=None,
            limit=None
    ) -> list:
        return mysqllib.findall(
            table=self.table,
            conditions=conditions,
            columns=columns,
            joins=joins,
            group_by=group_by,
            order_by=order_by,
            limit=limit
        )

    def update(
            self,
            data: Dict[str, any],
            conditions: ConditionsType = None
    ) -> bool:
        return mysqllib.update(table=self.table, data=data, conditions=conditions)

    def delete(
            self,
            conditions: ConditionsType = None
    ) -> bool:
        return mysqllib.delete(table=self.table, conditions=conditions)

    def create(
            self,
            data: Dict[str, any]
    ) -> bool:
        return mysqllib.create(table=self.table, data=data)

    def exists(
            self,
            conditions: ConditionsType = None,
            columns='*',
            joins: JoinType = None
    ) -> bool:
        """
        Exists in database
        """
        find = self.find(conditions=conditions, columns=columns, joins=joins)

        if not find:
            return False

        return True
