import io
import logging
import sys
import typing as t
from collections import OrderedDict

import pymongo
import pymongo.database
from bson.raw_bson import RawBSONDocument
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from .export import collection_to_json
from .extract import extract_schema_from_collection
from .transform import TransformationManager
from .translate import translate as translate_schema
from .util import parse_input_numbers

logger = logging.getLogger(__name__)

console = Console(stderr=True)
rich = console


def gather_collections(database) -> t.List[str]:
    """
    Gather a list of collections to use from a MongoDB database, based on user input.
    """

    collections = database.list_collection_names()

    tbl = Table(show_header=True, header_style="bold blue")
    tbl.add_column("Id", width=3)
    tbl.add_column("Collection Name")
    tbl.add_column("Estimated Size")

    for i, c in enumerate(collections):
        tbl.add_row(str(i), c, str(database[c].estimated_document_count()))

    rich.print(tbl)

    rich.print("\nCollections to exclude: (eg: '0 1 2', '0, 1, 2', '0-2'). Leave empty to use all collections.")

    sys.stderr.write("> ")
    collections_to_ignore = parse_input_numbers(input())
    filtered_collections = []
    for i, c in enumerate(collections):
        if i not in collections_to_ignore:
            filtered_collections.append(c)

    # MongoDB 2 does not understand `include_system_collections=False`.
    filtered_collections = [item for item in filtered_collections if not item.startswith("system.")]

    return filtered_collections


def get_mongodb_client_database(args, **kwargs) -> t.Tuple[pymongo.MongoClient, pymongo.database.Database]:
    client: pymongo.MongoClient
    client = pymongo.MongoClient(args.url, datetime_conversion="DATETIME_AUTO", **kwargs)
    db: pymongo.database.Database = client.get_database(args.database)
    return client, db


def extract(args) -> t.Dict[str, t.Any]:
    """
    Extract schemas from MongoDB collections.

    This asks the user for which collections they would like to extract,
    iterates over these collections and returns a dictionary of schemas for
    each of the selected collections.
    """
    client, db = get_mongodb_client_database(args)
    if args.collection:
        filtered_collections = [args.collection]
    else:
        filtered_collections = gather_collections(db)

    if not filtered_collections:
        rich.print("\nExcluding all collections. Nothing to do.")
        exit(0)

    if args.scan:
        partial = args.scan == "partial"
    else:
        rich.print("\nDo a [red bold]full[/red bold] collection scan?")
        rich.print("A full scan will iterate over all documents in the collection, a partial only one document. (Y/n)")
        sys.stderr.write("> ")
        full = input().strip().lower()

        partial = full != "y"

        rich.print(f"\nExecuting a [red bold]{'partial' if partial else 'full'}[/red bold] scan")

    tm = TransformationManager.from_path(path=args.transformation)
    schemas = OrderedDict()
    for collection_name in filtered_collections:
        collection_schema = extract_schema_from_collection(db[collection_name], partial, limit=args.limit)
        tm.apply_type_overrides(db.name, collection_name, collection_schema)
        schemas[collection_name] = collection_schema
    return schemas


def translate(schemas, schemaname: str = None) -> t.Dict[str, str]:
    """
    Translate a given schema into SQL DDL statements compatible with CrateDB.
    """
    result: t.Dict[str, str] = {}
    sql_queries = translate_schema(schemas=schemas, schemaname=schemaname)
    for collection, query in sql_queries.items():
        result[collection] = query
        syntax = Syntax(query, "sql")
        rich.print(f"Collection [blue bold]'{collection}'[/blue bold]:")
        rich.print(syntax)
    return result


def export(args) -> t.IO[bytes]:
    """
    Export MongoDB collection into JSON format.

    TODO: Run on multiple collections, like `extract`.
    """
    tm = TransformationManager.from_path(path=args.transformation)
    buffer = io.BytesIO()
    client, db = get_mongodb_client_database(args, document_class=RawBSONDocument)
    collection_to_json(db[args.collection], fp=buffer, tm=tm, limit=args.limit)
    buffer.seek(0)
    return buffer
