import json
import logging
from typing import List, Optional

from pydantic import BaseModel

try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    raise ImportError("The 'psycopg2' library is required. Please install it using 'pip install psycopg2'.")

from memory.vector_stores.base import VectorStoreBase

logger = logging.getLogger(__name__)


class OutputData(BaseModel):
    id: Optional[str]
    score: Optional[float]
    payload: Optional[dict]


class PGVector(VectorStoreBase):
    def __init__(
        self,
        dbname,
        collection_name,
        user,
        password,
        host,
        port,
        diskann,
        hnsw,
        embedding_model_dims=None,
    ):
        """
        Initialize the PGVector database.

        Args:
            dbname (str): Database name
            collection_name (str): Collection name
            user (str): Database user
            password (str): Database password
            host (str, optional): Database host
            port (int, optional): Database port
            diskann (bool, optional): Use DiskANN for faster search
            hnsw (bool, optional): Use HNSW for faster search
            embedding_model_dims (int, optional): Dimension of the embedding vector. If not provided, will be inferred from first vector.
        """
        self.collection_name = collection_name
        self.use_diskann = diskann
        self.use_hnsw = hnsw
        self.embedding_model_dims = embedding_model_dims

        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        self.cur = self.conn.cursor()

        collections = self.list_cols()
        if collection_name not in collections and embedding_model_dims is not None:
            self.create_col(embedding_model_dims)

    def create_col(self, embedding_model_dims):
        """
        Create a new collection (table in PostgreSQL).
        Will also initialize vector search index if specified.

        Args:
            embedding_model_dims (int): Dimension of the embedding vector.
        """
        self.cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        self.cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.collection_name} (
                id UUID PRIMARY KEY,
                vector vector({embedding_model_dims}),
                payload JSONB
            );
        """
        )

        if self.use_diskann and embedding_model_dims < 2000:
            # Check if vectorscale extension is installed
            self.cur.execute("SELECT * FROM pg_extension WHERE extname = 'vectorscale'")
            if self.cur.fetchone():
                # Create DiskANN index if extension is installed for faster search
                self.cur.execute(
                    f"""
                    CREATE INDEX IF NOT EXISTS {self.collection_name}_diskann_idx
                    ON {self.collection_name}
                    USING diskann (vector);
                """
                )
        elif self.use_hnsw:
            self.cur.execute(
                f"""
                CREATE INDEX IF NOT EXISTS {self.collection_name}_hnsw_idx
                ON {self.collection_name}
                USING hnsw (vector vector_cosine_ops)
            """
            )

        self.conn.commit()

    def insert(self, vectors, payloads=None, ids=None):
        """
        Insert vectors into a collection.

        Args:
            vectors (List[List[float]]): List of vectors to insert.
            payloads (List[Dict], optional): List of payloads corresponding to vectors.
            ids (List[str], optional): List of IDs corresponding to vectors.
        """
        logger.info(f"Inserting {len(vectors)} vectors into collection {self.collection_name}")
        
        # Auto-detect dimensions if not set
        if self.embedding_model_dims is None and vectors:
            self.embedding_model_dims = len(vectors[0])
            logger.info(f"Auto-detected embedding dimensions: {self.embedding_model_dims}")
        
        # Check if collection exists and handle dimension changes
        collections = self.list_cols()
        if self.collection_name not in collections:
            if self.embedding_model_dims is None:
                raise ValueError("Cannot create collection: embedding dimensions not specified and no vectors provided")
            self.create_col(self.embedding_model_dims)
        else:
            # Check if existing table has different dimensions
            existing_dims = self._get_table_dimensions()
            if existing_dims and existing_dims != self.embedding_model_dims:
                logger.warning(f"Dimension mismatch: Table has {existing_dims} dimensions, vectors have {self.embedding_model_dims}")
                logger.info(f"Recreating table {self.collection_name} with new dimensions: {self.embedding_model_dims}")
                self._migrate_table_dimensions(existing_dims, self.embedding_model_dims)
        
        json_payloads = [json.dumps(payload) for payload in payloads]

        data = [(id, vector, payload) for id, vector, payload in zip(ids, vectors, json_payloads)]
        execute_values(
            self.cur,
            f"INSERT INTO {self.collection_name} (id, vector, payload) VALUES %s",
            data,
        )
        self.conn.commit()

    def search(self, query, vectors, limit=5, filters=None):
        """
        Search for similar vectors.

        Args:
            query (str): Query.
            vectors (List[float]): Query vector.
            limit (int, optional): Number of results to return. Defaults to 5.
            filters (Dict, optional): Filters to apply to the search. Defaults to None.

        Returns:
            list: Search results.
        """
        # Check if collection exists before searching
        collections = self.list_cols()
        if self.collection_name not in collections:
            return []  # Return empty results if table doesn't exist yet
            
        filter_conditions = []
        filter_params = []

        if filters:
            for k, v in filters.items():
                filter_conditions.append("payload->>%s = %s")
                filter_params.extend([k, str(v)])

        filter_clause = "WHERE " + " AND ".join(filter_conditions) if filter_conditions else ""

        self.cur.execute(
            f"""
            SELECT id, vector <=> %s::vector AS distance, payload
            FROM {self.collection_name}
            {filter_clause}
            ORDER BY distance
            LIMIT %s
        """,
            (vectors, *filter_params, limit),
        )

        results = self.cur.fetchall()
        return [OutputData(id=str(r[0]), score=float(r[1]), payload=r[2]) for r in results]

    def delete(self, vector_id):
        """
        Delete a vector by ID.

        Args:
            vector_id (str): ID of the vector to delete.
        """
        self.cur.execute(f"DELETE FROM {self.collection_name} WHERE id = %s", (vector_id,))
        self.conn.commit()

    def update(self, vector_id, vector=None, payload=None):
        """
        Update a vector and its payload.

        Args:
            vector_id (str): ID of the vector to update.
            vector (List[float], optional): Updated vector.
            payload (Dict, optional): Updated payload.
        """
        if vector:
            self.cur.execute(
                f"UPDATE {self.collection_name} SET vector = %s WHERE id = %s",
                (vector, vector_id),
            )
        if payload:
            self.cur.execute(
                f"UPDATE {self.collection_name} SET payload = %s WHERE id = %s",
                (psycopg2.extras.Json(payload), vector_id),
            )
        self.conn.commit()

    def get(self, vector_id) -> OutputData:
        """
        Retrieve a vector by ID.

        Args:
            vector_id (str): ID of the vector to retrieve.

        Returns:
            OutputData: Retrieved vector.
        """
        self.cur.execute(
            f"SELECT id, vector, payload FROM {self.collection_name} WHERE id = %s",
            (vector_id,),
        )
        result = self.cur.fetchone()
        if not result:
            return None
        return OutputData(id=str(result[0]), score=None, payload=result[2])

    def list_cols(self) -> List[str]:
        """
        List all collections.

        Returns:
            List[str]: List of collection names.
        """
        self.cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        return [row[0] for row in self.cur.fetchall()]

    def delete_col(self):
        """Delete a collection."""
        self.cur.execute(f"DROP TABLE IF EXISTS {self.collection_name}")
        self.conn.commit()

    def col_info(self):
        """
        Get information about a collection.

        Returns:
            Dict[str, Any]: Collection information.
        """
        self.cur.execute(
            f"""
            SELECT 
                table_name, 
                (SELECT COUNT(*) FROM {self.collection_name}) as row_count,
                (SELECT pg_size_pretty(pg_total_relation_size('{self.collection_name}'))) as total_size
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = %s
        """,
            (self.collection_name,),
        )
        result = self.cur.fetchone()
        return {"name": result[0], "count": result[1], "size": result[2]}

    def list(self, filters=None, limit=100):
        """
        List all vectors in a collection.

        Args:
            filters (Dict, optional): Filters to apply to the list.
            limit (int, optional): Number of vectors to return. Defaults to 100.

        Returns:
            List[OutputData]: List of vectors.
        """
        # Check if collection exists before listing
        collections = self.list_cols()
        if self.collection_name not in collections:
            return [[]]  # Return empty list if table doesn't exist yet
            
        filter_conditions = []
        filter_params = []

        if filters:
            for k, v in filters.items():
                filter_conditions.append("payload->>%s = %s")
                filter_params.extend([k, str(v)])

        filter_clause = "WHERE " + " AND ".join(filter_conditions) if filter_conditions else ""

        query = f"""
            SELECT id, vector, payload
            FROM {self.collection_name}
            {filter_clause}
            LIMIT %s
        """

        self.cur.execute(query, (*filter_params, limit))

        results = self.cur.fetchall()
        return [[OutputData(id=str(r[0]), score=None, payload=r[2]) for r in results]]

    def _get_table_dimensions(self):
        """
        Get the dimensions of the vector column in the existing table.
        
        Returns:
            int: Number of dimensions, or None if table doesn't exist or no vector column
        """
        try:
            self.cur.execute(f"""
                SELECT a.atttypmod as dimensions
                FROM pg_attribute a
                JOIN pg_class c ON a.attrelid = c.oid
                JOIN pg_type t ON a.atttypid = t.oid
                WHERE c.relname = '{self.collection_name}' 
                    AND a.attname = 'vector'
                    AND t.typname = 'vector'
                    AND NOT a.attisdropped
            """)
            result = self.cur.fetchone()
            if result and result[0] and result[0] > 0:
                return int(result[0])
            return None
        except Exception as e:
            logger.warning(f"Could not determine table dimensions: {e}")
            return None

    def _migrate_table_dimensions(self, old_dims, new_dims):
        """
        Migrate table to new dimensions by backing up data and recreating table.
        
        Args:
            old_dims (int): Old dimension count
            new_dims (int): New dimension count
        """
        try:
            # Backup existing data
            backup_table = f"{self.collection_name}_backup_{old_dims}d"
            logger.info(f"Creating backup table: {backup_table}")
            
            self.cur.execute(f"""
                CREATE TABLE {backup_table} AS 
                SELECT id, payload, NOW() as backup_date 
                FROM {self.collection_name}
            """)
            
            # Count backed up records
            self.cur.execute(f"SELECT COUNT(*) FROM {backup_table}")
            backup_count = self.cur.fetchone()[0]
            logger.info(f"Backed up {backup_count} records to {backup_table}")
            
            # Drop existing table
            self.cur.execute(f"DROP TABLE {self.collection_name} CASCADE")
            logger.info(f"Dropped table {self.collection_name}")
            
            # Create new table with new dimensions
            self.create_col(new_dims)
            logger.info(f"Created new table {self.collection_name} with {new_dims} dimensions")
            
            self.conn.commit()
            
        except Exception as e:
            logger.error(f"Error during table migration: {e}")
            self.conn.rollback()
            raise

    def __del__(self):
        """
        Close the database connection when the object is deleted.
        """
        if hasattr(self, "cur"):
            self.cur.close()
        if hasattr(self, "conn"):
            self.conn.close()

    def reset(self):
        """Reset the index by deleting and recreating it."""
        logger.warning(f"Resetting index {self.collection_name}...")
        self.delete_col()
        if self.embedding_model_dims is not None:
            self.create_col(self.embedding_model_dims)
