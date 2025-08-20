import os

from mysqllib import execute, fetchall, fetchone


def _init():
    execute("""create table if not exists migrations
            (
                id int unsigned auto_increment primary key,
                timestamp varchar(50) null,
                status varchar(255) null,
                error longtext null,
                date_modify datetime default CURRENT_TIMESTAMP not null,
                date_created datetime default CURRENT_TIMESTAMP not null
            );""")


def _get_migration_list(path) -> list:
    migration_files = []

    for migration_file in sorted(f for f in os.listdir(path) if f.endswith(('.sql', '.py'))):
        migration_files.append(migration_file.replace('.sql', '').replace('.py', ''))

    return migration_files


def _get_finished_migration() -> list:
    migrations_execute = fetchall('select `timestamp` from migrations')

    if migrations_execute:
        return sorted(set((str(row['timestamp'])) for row in migrations_execute))
    else:
        return []


def run_migration(directory_path) -> bool:
    _init()

    if fetchone('select * from migrations where status != "finished"'):
        return False

    migrations_execute = _get_finished_migration()

    lock_result = fetchone("SELECT GET_LOCK('migration_lock', 10) AS lock_acquired")
    lock_acquired = False

    if lock_result and 'lock_acquired' in lock_result:
        lock_acquired = bool(lock_result['lock_acquired'])
    elif lock_result:
        try:
            lock_acquired = bool(list(lock_result.values())[0])
        except Exception:
            lock_acquired = False

    if not lock_acquired:
        return False

    try:
        for filename in _get_migration_list(directory_path):
            if filename in migrations_execute:
                continue

            path = f'{directory_path}{filename}'
            path += '.py' if os.path.isfile(path + '.py') else '.sql'

            try:
                execute('START TRANSACTION')

                if path.endswith('.sql'):
                    with open(path, 'r') as file:
                        execute(file.read())
                else:
                    exec(open(path).read())

                execute('COMMIT')
                execute(
                    'INSERT INTO migrations (timestamp, status) VALUES (%s, %s)',
                    (filename, 'finished')
                )
            except Exception as e:
                try:
                    execute('ROLLBACK')
                except Exception:
                    pass
                execute(
                    'INSERT INTO migrations (timestamp, status, error) VALUES (%s, %s, %s)',
                    (filename, 'failed', str(e))
                )
                return False
        return True
    finally:
        try:
            fetchone("SELECT RELEASE_LOCK('migration_lock')")
        except Exception:
            pass
