import aiohttp
from fastapi import HTTPException
from pymongo import UpdateOne, DeleteOne, InsertOne
from pymongo.database import Database
from elasticsearch import Elasticsearch, NotFoundError
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Union, Dict
from sqlalchemy import text


async def post_data(
    payload: dict, url: str, authorization: str, extra_headers: dict = {}
):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": authorization,
                    **extra_headers,
                },
            ) as response:
                if response.status in (200, 201):
                    return await response.json()

                error_detail = await response.text()
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Failed to save data: {error_detail}",
                )
    except aiohttp.ClientError as e:
        raise HTTPException(
            status_code=500, detail=f"Network error occurred on {url}: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error occurred on {url}: {str(e)}"
        )


async def get_data(url: str, authorization: str, extra_headers: dict = {}):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": authorization,
                    **extra_headers,
                },
            ) as response:
                if response.status in (200, 201):
                    return await response.json()

                error_detail = await response.text()
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Failed to retrieve data: {error_detail}",
                )
    except aiohttp.ClientError as e:
        raise HTTPException(
            status_code=500, detail=f"Network error occurred on {url}: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error occurred on {url}: {str(e)}"
        )


async def put_data(
    payload: dict, url: str, authorization: str, extra_headers: dict = {}
):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": authorization,
                    **extra_headers,
                },
            ) as response:
                if response.status in (200, 201):
                    return await response.json()

                error_detail = await response.text()
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Failed to update data: {error_detail}",
                )
    except aiohttp.ClientError as e:
        raise HTTPException(
            status_code=500, detail=f"Network error occurred on {url}: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error occurred on {url}: {str(e)}"
        )


async def delete_data(url: str, authorization: str, extra_headers: dict = {}):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": authorization,
                    **extra_headers,
                },
            ) as response:
                if response.status in (200, 201):
                    return await response.json()

                error_detail = await response.text()
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Failed to delete data: {error_detail}",
                )
    except aiohttp.ClientError as e:
        raise HTTPException(
            status_code=500, detail=f"Network error occurred on {url}: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error occurred on {url}: {str(e)}"
        )


async def patch_data(
    payload: dict, url: str, authorization: str, extra_headers: dict = {}
):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.patch(
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": authorization,
                    **extra_headers,
                },
            ) as response:
                if response.status in (200, 201):
                    return await response.json()

                error_detail = await response.text()
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Failed to patch data: {error_detail}",
                )
    except aiohttp.ClientError as e:
        raise HTTPException(
            status_code=500, detail=f"Network error occurred on {url}: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error occurred on {url}: {str(e)}"
        )


async def mongo_multi_delete(data_list: list, mongo_db: Database, collection_name: str):
    """
    Perform bulk delete operations in MongoDB asynchronously.

    Args:
        data_list (list): List of filter dictionaries for deletion.
        mongodb_connection: MongoDB database or client instance.
        collection_name (str): Target collection name.

    Returns:
        dict: Summary of the bulk delete result.

    Example:
        filters = [
            {"_id": "doc1"},
            {"status": "inactive"},
            {"age": {"$lt": 18}}
        ]
        result = await mongo_multi_delete(filters, mongodb_connection, "users")
        print(result)
    """
    try:
        collection = mongo_db[collection_name]
        operations = [DeleteOne(filter_doc) for filter_doc in data_list]

        result = collection.bulk_write(operations)
        return {
            "deleted_count": result.deleted_count,
            "acknowledged": result.acknowledged,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to perform bulk delete MongoDB: {str(e)}"
        )


async def mongo_multi_update(data_list: list, mongo_db: Database, collection_name: str):
    """
    Perform bulk update operations in MongoDB asynchronously.

    Args:
        data_list (list): List of dictionaries with 'filter' and 'update' keys.
        mongodb_connection: MongoDB database or client instance.
        collection_name (str): Target collection.

    Returns:
        dict: Summary of the bulk update result.

    Example:
    updates = [
        {
            "filter": {"_id": "doc1"},
            "update": {"$set": {"status": "active"}}
        },
        {
            "filter": {"age": {"$lt": 18}},
            "update": {"$set": {"category": "minor"}}
        }
    ]
    result = await mongo_multi_update(updates, mongodb_connection, "users")
    """
    try:
        collection = mongo_db[collection_name]
        operations = [UpdateOne(item["filter"], item["update"]) for item in data_list]

        result = collection.bulk_write(operations)
        return {
            "modified_count": result.modified_count,
            "matched_count": result.matched_count,
            "acknowledged": result.acknowledged,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to perform bulk update MongoDB: {str(e)}"
        )


async def mongo_multi_insert(data_list: list, mongo_db: Database, collection_name: str):
    """
    Perform bulk update operations in MongoDB asynchronously.

    Args:
        data_list (list): List of dictionaries with 'filter' and 'update' keys.
        mongodb_connection: MongoDB database or client instance.
        collection_name (str): Target collection.

    Returns:
        dict: Summary of the bulk insert result.

    Example:
    data_list = [
        {
            "name": "John Doe",
            "age": 30,
            "email": "john.doe@example.com"
        },
        {
            "name": "Jane Smith",
            "age": 25,
            "email": "jane.smith@example.com"
        }
    ]
    result = await mongo_multi_insert(data_list, mongodb_connection, "users")
    """
    try:
        collection = mongo_db[collection_name]
        operations = [InsertOne(item) for item in data_list]

        result = collection.bulk_write(operations)
        return {
            "inserted_count": result.inserted_count,
            "acknowledged": result.acknowledged,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to perform bulk insert MongoDB: {str(e)}"
        )


async def es_multi_delete(data_list: list, es_client: Elasticsearch, index_name: str):
    """
    Perform bulk delete operations in Elasticsearch.

    Supports deletion by document IDs or by query.

    Args:
        data_list (list): List of doc IDs (str) or query dicts.
        es_client: Async Elasticsearch client instance.
        index_name (str): Target index.

    Returns:
        dict: Summary of the delete operations.

    Example:
        # By IDs
        doc_ids = ["doc1", "doc2"]
        await es_multi_delete(doc_ids, es_client, "users")

        # By queries
        queries = [{"term": {"status": "inactive"}}]
        await es_multi_delete(queries, es_client, "users")
    """
    try:
        deleted_count = 0
        errors = []

        for item in data_list:
            try:
                if isinstance(item, str):
                    # Delete by document ID
                    es_client.delete(index=index_name, id=item, ignore=[404])
                    deleted_count += 1
                elif isinstance(item, dict):
                    # Delete by query
                    resp = es_client.delete_by_query(
                        index=index_name, body={"query": item}
                    )
                    deleted_count += resp.get("deleted", 0)
            except NotFoundError:
                continue
            except Exception as ex:
                errors.append(str(ex))

        return {
            "deleted": deleted_count,
            "errors": bool(errors),
            "error_details": errors if errors else None,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform bulk delete in Elasticsearch: {str(e)}",
        )


async def es_multi_update(data_list: list, es_client: Elasticsearch, index_name: str):
    """
    Perform bulk update operations in Elasticsearch.

    Args:
        data_list (list): List of update instructions:
            - By document ID: {'id': 'doc_id', 'doc': {...}}
            - By query: {'query': {...}, 'script': {...}}
        es_client (Elasticsearch): Elasticsearch client instance.
        index_name (str): Target index.

    Returns:
        dict: Summary of the update operations.

    Example:
        updates = [
            {"id": "doc1", "doc": {"status": "active"}},
            {"query": {"term": {"status": "inactive"}}, "script": {"source": "ctx._source.status = 'active'"}}
        ]
        result = await es_multi_update(updates, es_client, "users")
        print(result)
    """
    try:
        doc_updates = []
        query_updates = []
        updated_count = 0
        errors = []

        for item in data_list:
            if "id" in item and "doc" in item:
                # Bulk update by document ID
                doc_updates.extend(
                    [
                        {"update": {"_index": index_name, "_id": item["id"]}},
                        {"doc": item["doc"]},
                    ]
                )
            elif "query" in item and "script" in item:
                # Update by query
                query_updates.append(item)

        # Execute bulk doc updates
        if doc_updates:
            result = es_client.bulk(operations=doc_updates)
            if result.get("errors"):
                errors.append("Some document updates failed.")
            updated_count += len(doc_updates) // 2  # each update has 2 parts

        # Execute query updates
        for update in query_updates:
            try:
                result = es_client.update_by_query(
                    index=index_name,
                    body={"query": update["query"], "script": update["script"]},
                )
                updated_count += result.get("updated", 0)
            except Exception as ex:
                errors.append(str(ex))

        return {
            "updated": updated_count,
            "errors": bool(errors),
            "error_details": errors if errors else None,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform bulk update in Elasticsearch: {str(e)}",
        )


async def es_multi_insert(data_list: list, es_client: Elasticsearch, index_name: str):
    """
    Perform bulk insert operations in Elasticsearch.

    Args:
        data_list (list): List of documents to insert. Can be:
            - List of document dictionaries (auto-generated IDs)
            - List of dictionaries with 'id' and 'doc' keys (custom IDs)
        es_client (Elasticsearch): Elasticsearch client instance.
        index_name (str): Target index.

    Returns:
        dict: Summary of the insert operations.

    Example:
        # Auto-generated IDs
        data_list = [
            {"name": "John Doe", "age": 30},
            {"name": "Jane Smith", "age": 25}
        ]
        result = await es_multi_insert(data_list, es_client, "users")

        # Custom IDs
        data_list = [
            {"id": "doc1", "doc": {"name": "John Doe", "age": 30}},
            {"id": "doc2", "doc": {"name": "Jane Smith", "age": 25}}
        ]
        result = await es_multi_insert(data_list, es_client, "users")
    """
    try:
        bulk_operations = []
        inserted_count = 0
        errors = []

        for item in data_list:
            if "id" in item and "doc" in item:
                # Custom ID provided
                bulk_operations.extend(
                    [{"index": {"_index": index_name, "_id": item["id"]}}, item["doc"]]
                )
            else:
                # Auto-generated ID
                bulk_operations.extend([{"index": {"_index": index_name}}, item])

        if bulk_operations:
            result = es_client.bulk(operations=bulk_operations)

            if result.get("errors"):
                errors.append("Some document inserts failed.")
                # Add detailed error information if available
                if "items" in result:
                    for item in result["items"]:
                        if "index" in item and "error" in item["index"]:
                            errors.append(f"Error: {item['index']['error']}")

            inserted_count = (
                len(bulk_operations) // 2
            )  # each document has 2 parts in bulk

        return {
            "inserted": inserted_count,
            "errors": bool(errors),
            "error_details": errors if errors else None,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform bulk insert in Elasticsearch: {str(e)}",
        )


async def pg_multi_delete(
    data_list: List[Union[int, str]],
    pg_db: Session,
    table_name: str,
    id_column: str = "id",
):
    """
    Perform bulk delete operations in PostgreSQL using SQLAlchemy ORM.

    Args:
        data_list (list): List of values to match against the id_column for deletion.
        pg_db (Session): SQLAlchemy ORM database session.
        table_name (str): Name of the table to perform operations on.
        id_column (str): Name of the column to match against (default: "id").

    Returns:
        dict: Result of the bulk operation.

    Example:
        ids = [1, 2, 3]
        result = pg_multi_delete(ids, pg_db, "users")

        usernames = ["user1", "user2"]
        result = pg_multi_delete(usernames, pg_db, "users", "username")
    """
    try:
        if not data_list:
            return {"deleted": 0, "errors": False}

        # Create a parameterized query safely using SQLAlchemy's text()
        query = text(
            f"""
            DELETE FROM {table_name}
            WHERE {id_column} = ANY(:data_list)
            RETURNING {id_column}
        """
        )

        result = pg_db.execute(query, {"data_list": data_list})
        deleted_ids = [row[0] for row in result.fetchall()]
        pg_db.commit()

        return {
            "deleted": len(deleted_ids),
            "errors": False,
            "deleted_ids": deleted_ids,
        }

    except Exception as e:
        pg_db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform bulk delete operation in PostgreSQL: {str(e)}",
        )


async def pg_multi_update(
    data_list: List[Dict[str, Union[int, Dict]]],
    pg_db: Session,
    table_name: str,
    id_column: str = "id",
):
    """
    Perform bulk update operations in PostgreSQL using SQLAlchemy ORM.

    Args:
        data_list (list): List of dictionaries containing 'id' and 'data' keys.
                          Each 'data' is a dict of column-value pairs to be updated.
        pg_db (Session): SQLAlchemy ORM database session.
        table_name (str): Name of the table to perform operations on.
        id_column (str): Name of the column to match against (default: "id").

    Returns:
        dict: Result of the bulk operation.
    """
    try:
        if not data_list:
            return {"updated": 0, "errors": False}

        updated_ids = []

        for item in data_list:
            record_id = item.get("id")
            update_data = item.get("data")

            if not record_id or not update_data:
                continue

            set_clause = ", ".join([f"{key} = :{key}" for key in update_data])
            query = text(
                f"""
                UPDATE {table_name}
                SET {set_clause}
                WHERE {id_column} = :record_id
                RETURNING {id_column}
            """
            )

            # Add the ID to the values dict
            values = {**update_data, "record_id": record_id}
            result = pg_db.execute(query, values).fetchone()
            if result:
                updated_ids.append(result[0])

        pg_db.commit()

        return {
            "updated": len(updated_ids),
            "errors": False,
            "updated_ids": updated_ids,
        }

    except Exception as e:
        pg_db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform bulk update operation in PostgreSQL: {str(e)}",
        )
