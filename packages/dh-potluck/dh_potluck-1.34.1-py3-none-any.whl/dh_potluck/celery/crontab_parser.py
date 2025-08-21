from typing import Dict


def parse_crontab_str(crontab_str: str) -> Dict[str, str]:
    """
    Parse a crontab expression and convert to dict that can be passed as kwargs to crontab from
    celery.schedules

    See https://crontab.guru/ for help with generating crontab strings
    """
    try:
        m, h, dw, dm, my = crontab_str.split()
    except ValueError:
        raise ValueError(
            f'Crontab string: {crontab_str} does not contain 5 values, '
            'enter a valid crontab input in the form of "* * * * *"'
        )
    return {'minute': m, 'hour': h, 'day_of_week': dw, 'day_of_month': dm, 'month_of_year': my}
