from urllib.parse import urlencode

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from pymongo import InsertOne, UpdateOne
from pymongo.errors import BulkWriteError

from reach_commons.app_logging.logger import get_reach_logger


class MongoCustomerCRUDAsync:
    def __init__(self, connection_info: dict, logger=get_reach_logger()):
        self.logger = logger
        self.mongo_client = AsyncIOMotorClient(
            "{}://{}:{}@{}/?{}".format(
                connection_info["schema"],
                connection_info["username"],
                connection_info["password"],
                connection_info["host"],
                urlencode(connection_info["extra_args"]),
            )
        )
        self.db = self.mongo_client.get_database(connection_info["database"])
        self.collection: AsyncIOMotorCollection = self.db.get_collection("customers")

    def validate_and_prepare_operations(self, records: list, operation: str):
        operations = []
        for record in records:
            customer_id = record.get("customer_id")
            business_id = record.get("business_id")

            if not customer_id or not business_id:
                self.logger.error(
                    f"Missing customer_id or business_id in record.  record={str(record)}"
                )
                raise ValueError(
                    f"Both customer_id and business_id are required in the record.  record={str(record)}"
                )

            query = {"customer_id": customer_id, "business_id": business_id}

            if operation == "upsert":
                update_fields = {"$set": record}
                if "updated_at" not in record:
                    update_fields["$currentDate"] = {"updated_at": True}

                operations.append(UpdateOne(query, update_fields, upsert=True))
            elif operation == "insert":
                operations.append(InsertOne(record))
            elif operation == "update":
                update_fields = {"$set": record, "$currentDate": {"updated_at": True}}
                operations.append(UpdateOne(query, update_fields, upsert=False))
            elif operation == "delete":
                operations.append(UpdateOne(query, {"$set": {"deleted": True}}))
            else:
                raise ValueError(
                    f"Invalid operation: {operation}  record={str(record)}"
                )

        return operations

    async def execute_bulk_operations(self, operations: list):
        try:
            if operations:
                result = await self.collection.bulk_write(operations)
                self.logger.info(f"Bulk operation completed: {result.bulk_api_result}")
        except BulkWriteError as bwe:
            self.logger.error(f"Bulk write error: {bwe.details}")

    async def process_records(self, records: list, operation: str):
        operations = self.validate_and_prepare_operations(records, operation)
        await self.execute_bulk_operations(operations)


"""
# Exemplo de uso:
connection_info = {
    "database": "db0",
    "schema": "mongodb+srv",
    "username": "databricks_rw",
    "password": "Lh4GsNx7cQUPtDmONqVGI9Dy7Jy6TbAxmq",
    "host": "cluster0.rwha2.mongodb.net",
    "extra_args": {
        "retryWrites": "true",
        "w": "majority",
        "appName": "Cluster0",
    },
}

mongo_crud = MongoCustomerCRUDAsync(connection_info)

message = {
    "metadata": {"operation": "upsert"},
    "records": [
        {"customer_id": "123", "business_id": "456", "name": "John Doe"},
        {"customer_id": "124", "business_id": "456", "name": "Jane Doe"}
    ],
}

# Rodar a função assíncrona:
import asyncio
asyncio.run(mongo_crud.process_records(message["records"], message["metadata"]["operation"]))
"""
