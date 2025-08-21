import glob
import os
import re
import shutil
import subprocess
import tempfile

import click
from flask import current_app
from flask.cli import with_appcontext
from sqlalchemy.dialects.mysql.base import MySQLDialect
from sqlalchemy.schema import CreateTable

from dh_potluck.utils import get_db


@click.group(help='Commands for using Skeema with SQLAlchemy')
def skeema():
    pass


@skeema.command(help='Dump the current SQLAlchemy schema to Skeema-compatible SQL files')
@click.option(
    '--output-dir',
    default=None,
    help='Output directory for the dump files. Defaults to `{current_app.root_path}/database`.',
)
@with_appcontext
def dump(output_dir):
    metadata = get_db().Model.metadata
    dialect = MySQLDialect()
    db_dir = output_dir if output_dir else os.path.join(current_app.root_path, 'database')
    os.makedirs(db_dir, exist_ok=True)

    # Clear all existing Skeema files
    files = glob.glob(os.path.join(db_dir, '*.sql'))
    for file in files:
        os.remove(file)

    # Iterate through all the tables in the metadata and print their CREATE TABLE statements
    for table in metadata.sorted_tables:
        create_table = str(CreateTable(table).compile(dialect=dialect)).strip()

        # Skeema expects indexes to be defined as part of the CREATE TABLE statements, but
        # SQLAlchemy outputs them as separate CREATE INDEX statements. Adjust for this by
        # iterating through all the indexes in the table and manually add them to the CREATE TABLE
        # statement.
        if table.indexes:
            index_definitions = []
            for index in table.indexes:
                columns = ', '.join([f'`{column.name}`' for column in index.columns])
                index_type = 'UNIQUE' if index.unique else 'INDEX'
                index_definitions.append(f'{index_type} `{index.name}` ({columns})')

            index_definitions = ',\n\t'.join(index_definitions)
            create_table = re.sub(r'\n\)', f',\n\t{index_definitions}\n)', create_table)

        # Write the CREATE TABLE statement to a file named after the table
        table_file = os.path.join(db_dir, f'{table.name}.sql')
        with open(table_file, 'w') as file:
            file.write(f'{create_table};\n')


def call_skeema(command, args, ctx):
    with tempfile.TemporaryDirectory() as tmp_dir:
        ctx.invoke(dump, output_dir=tmp_dir)
        shutil.copy(os.path.join(current_app.root_path, '.skeema'), tmp_dir)
        subprocess.run(['skeema', command, *args], cwd=tmp_dir)


@skeema.command(
    'diff',
    context_settings={'ignore_unknown_options': True},
    help='Compare a DB’s schema to the current app’s SQLAlchemy schema',
)
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
@with_appcontext
def diff(ctx, args):
    call_skeema('diff', args, ctx)


@skeema.command(
    'push',
    context_settings={'ignore_unknown_options': True},
    help='Alter a DB to reflect the current app’s SQLAlchemy schema',
)
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
@with_appcontext
def push(ctx, args):
    call_skeema('push', args, ctx)
