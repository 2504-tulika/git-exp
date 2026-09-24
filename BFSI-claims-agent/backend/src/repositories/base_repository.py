"""
Generic CRUD operations, shared by every repository.
"""

from src.utils.logger import get_logger

logger = get_logger(__name__)

class BaseRepository:
    def __init__(self, db, model):
        self.db = db          # the SQLAlchemy session (from get_db())
        self.model = model    # the model class this repository is for, e.g. Customer

    def get_by_id(self, id_value):
        """
        Get one row by its primary key, or None if it doesn't exist.
        For a table with a composite primary key (like policy_customers),
        pass a tuple: get_by_id(("MSI-MOT-1002", "CUST-002")).
        """
        return self.db.get(self.model, id_value)

    def get_all(self):
        """Get every row for this model."""
        return self.db.query(self.model).all()

    def create(self, **fields):
        """Insert a new row. Pass column values as keyword arguments."""
        record = self.model(**fields)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        logger.info(f"Created {self.model.__name__}: {fields}")
        return record

    def update(self, id_value, **fields):
        """Update an existing row. Returns the updated row, or None if it wasn't found."""
        record = self.get_by_id(id_value)
        if record is None:
            return None
        for key, value in fields.items():
            setattr(record, key, value)
        self.db.commit()
        self.db.refresh(record)
        logger.info(f"Updated {self.model.__name__} {id_value}: {fields}")
        return record

    def delete(self, id_value):
        """Delete a row by its primary key. Returns True if something was deleted."""
        record = self.get_by_id(id_value)
        if record is None:
            return False
        self.db.delete(record)
        self.db.commit()
        logger.info(f"Deleted {self.model.__name__} {id_value}")
        return True

