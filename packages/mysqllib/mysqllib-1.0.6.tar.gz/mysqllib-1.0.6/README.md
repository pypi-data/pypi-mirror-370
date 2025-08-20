# Mysqllib
Simple mysql database

## Connect
```text
connect(
        user: str,
        password: str,
        database: str,
        host: str='127.0.0.1',
        port: int=3306
)
```

## Fetch one
```text
fetchone(query, args=None) -> Optional[dict]
```

## Fetch all
```text
fetchall(query, args=None) -> Optional[list]:
```

## Execute
```text
execute(query, args=None) -> bool:
```

## find
```text
def find(
        table: str,
        conditions: Dict[str, Union[str, List]] = None,
        columns='*',
        joins: Optional[List[Tuple[str, str, str]]] = None,
        order_by=None
) -> dict
```

## findall
```text
def findall(
        table: str,
        conditions: Dict[str, Union[str, List]] = None,
        columns='*',
        joins: Optional[List[Tuple[str, str, str]]] = None,
        group_by=None,
        order_by=None,
        limit=None
) -> list
```

## update
```text
def update(
        table: str,
        data: Dict[str, any],
        conditions: Optional[Dict[str, any]] = None
) -> bool
```

## delete
```text
def delete(
        table: str,
        conditions: Optional[Dict[str, any]] = None
)
```

## insert
```text
def create(
        table: str,
        data: Dict[str, any]
) -> bool
```

# Mirations
## Run
```python
import mysqllib.migration

mysqllib.migration.run_migration('./path/to/migration/directory/')
```