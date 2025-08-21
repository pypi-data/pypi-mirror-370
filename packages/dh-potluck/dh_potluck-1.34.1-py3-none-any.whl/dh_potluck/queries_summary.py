try:
    from flask_sqlalchemy.record_queries import get_recorded_queries
except ImportError:
    from flask_sqlalchemy import get_debug_queries as get_recorded_queries  # type: ignore[no-redef]

from .utils.term import Bell, TextColors


def get_database_queries_summary(app):
    """
    Prepare a summary of the SQL queries executed during a request. Useful finding slow queries.
    """
    queries = get_recorded_queries()
    message = f'\n{TextColors.LIGHTYELLOW}Database Queries Summary'
    slow_query_time = app.config.get('DH_SLOW_DB_QUERY_TIME', 0.5)
    too_many_queries = app.config.get('DH_TOO_MANY_SQL_QUERIES', 10)
    total_query_time = 0
    select_queries_count = 0
    slow_queries = []
    for query in queries:
        total_query_time += query.duration
        if query.statement.startswith('SELECT'):
            select_queries_count += 1
        if query.duration > slow_query_time:
            slow_queries.append(query)
    message += f'\n\t{TextColors.BLUE}Select queries: {TextColors.RESET}{select_queries_count}'

    if len(queries) - select_queries_count > 0:
        message += (
            f'\n\t{TextColors.BLUE}Other queries: '
            f'{TextColors.RESET}{len(queries) - select_queries_count}'
        )
    message += f'\n\t{TextColors.BLUE}Total queries: {TextColors.RESET}{len(queries)}'
    message += f'\n\t{TextColors.BLUE}Total query time: {TextColors.RESET}{total_query_time:.2f}s'

    if slow_queries:
        message += (
            f'\n\t{TextColors.LIGHTRED}{Bell.BELL}[⚠️  WARNING] Slow queries '
            f'(>{slow_query_time}s): {len(slow_queries)}'
        )

    if len(queries) > too_many_queries:
        message += (
            f'\n\t{TextColors.LIGHTRED}{Bell.BELL}[⚠️  WARNING] Too many queries '
            f'(max {too_many_queries} queries)'
        )

    return message
