import os
import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection

class MongoDBClient:
    """
    MongoDB client handler for safe usage in forking environments.
    Lazily initializes a client to avoid fork-safety warnings.
    Optimized for replica set failover scenarios.
    """

    def __init__(self, user: str = 'SharedData') -> None:
        """
        Initialize MongoDB client handler.
        
        Args:
            user (str): The database user namespace. Defaults to 'SharedData'.
        """
        self._user = user
        if not 'MONGODB_REPLICA_SET' in os.environ:
            self.mongodb_conn_str = (
                f'mongodb://{os.environ["MONGODB_USER"]}:'
                f'{os.environ["MONGODB_PWD"]}@'
                f'{os.environ["MONGODB_HOST"]}:'
                f'{os.environ["MONGODB_PORT"]}/'
            )
        else:
            # Replica set connection string with minimal essential parameters
            self.mongodb_conn_str = (
                f'mongodb://{os.environ["MONGODB_USER"]}:'
                f'{os.environ["MONGODB_PWD"]}@'
                f'{os.environ["MONGODB_HOST"]}/'
                f'?replicaSet={os.environ["MONGODB_REPLICA_SET"]}'
                f'&authSource={os.environ["MONGODB_AUTH_DB"]}'
                f'&readPreference=primaryPreferred'  # Use secondary when primary down
                f'&w=1'  # Explicit write concern 1 for maximum availability
                f'&serverSelectionTimeoutMS=15000'  # Quick failover detection
                f'&socketTimeoutMS=20000'  # Prevent hanging connections
            )
        self._client = None  # Client will be created on first access

    @property
    def client(self) -> MongoClient:
        """
        Lazily initialize the MongoClient for this process.
        """
        if self._client is None:
            self._client = MongoClient(self.mongodb_conn_str)
        return self._client

    @client.setter
    def client(self, value: MongoClient) -> None:
        """
        Manually set the MongoDB client.
        """
        self._client = value

    def __getitem__(self, collection_name: str) -> Collection:
        """
        Allow dictionary-like access to collections in the user's database.
        
        Args:
            collection_name (str): The name of the collection to access.
        
        Returns:
            Collection: The requested MongoDB collection.
        """
        return self.client[self._user][collection_name]
        
    @staticmethod
    def ensure_index(coll, index_fields, **kwargs):
        """
        Ensure a specific index exists on the collection.
        
        Parameters:
            coll (pymongo.collection.Collection): The MongoDB collection.
            index_fields (list of tuples): Index fields and order, e.g., [('status', ASCENDING)].
            kwargs: Any additional options for create_index (e.g., name, unique).
        """
        existing_indexes = coll.index_information()

        # Normalize input index spec for comparison
        target_index = pymongo.helpers._index_list(index_fields)

        for index_name, index_data in existing_indexes.items():
            if pymongo.helpers._index_list(index_data['key']) == target_index:
                return  # Index already exists

        coll.create_index(index_fields, **kwargs)