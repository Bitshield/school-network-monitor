"""
Base service class with common database operations.
"""

from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import DeclarativeMeta
from pydantic import BaseModel
import uuid
from datetime import datetime

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base service with CRUD operations for database models.
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        Initialize base service.
        
        Args:
            model: SQLAlchemy model class
            db: Async database session
        """
        self.model = model
        self.db = db

    def _generate_id(self) -> str:
        """Generate unique ID for new records."""
        return str(uuid.uuid4())

    async def get(self, id: str) -> Optional[ModelType]:
        """
        Get single record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            Model instance or None if not found
        """
        result = await self.db.execute(
            select(self.model).where(self.model.id == id) # type: ignore
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and filtering.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field name to order by
            filters: Dictionary of field:value filters
            
        Returns:
            List of model instances
        """
        query = select(self.model)

        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)

        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            query = query.order_by(getattr(self.model, order_by))

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """
        Create new record.
        
        Args:
            obj_in: Pydantic schema with creation data
            
        Returns:
            Created model instance
        """
        obj_data = obj_in.model_dump()
        obj_data["id"] = self._generate_id()
        
        # Add timestamps if model has them
        if hasattr(self.model, "created_at"):
            obj_data["created_at"] = datetime.utcnow()
        if hasattr(self.model, "updated_at"):
            obj_data["updated_at"] = datetime.utcnow()

        db_obj = self.model(**obj_data) # type: ignore
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        id: str,
        obj_in: UpdateSchemaType,
    ) -> Optional[ModelType]:
        """
        Update existing record.
        
        Args:
            id: Record ID
            obj_in: Pydantic schema with update data
            
        Returns:
            Updated model instance or None if not found
        """
        db_obj = await self.get(id)
        if not db_obj:
            return None

        obj_data = obj_in.model_dump(exclude_unset=True)
        
        # Update timestamp if model has it
        if hasattr(self.model, "updated_at"):
            obj_data["updated_at"] = datetime.utcnow()

        for field, value in obj_data.items():
            setattr(db_obj, field, value)

        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: str) -> bool:
        """
        Delete record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            True if deleted, False if not found
        """
        db_obj = await self.get(id)
        if not db_obj:
            return False

        await self.db.delete(db_obj)
        await self.db.commit()
        return True

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filters.
        
        Args:
            filters: Dictionary of field:value filters
            
        Returns:
            Count of matching records
        """
        query = select(func.count()).select_from(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def exists(self, id: str) -> bool:
        """
        Check if record exists by ID.
        
        Args:
            id: Record ID
            
        Returns:
            True if exists, False otherwise
        """
        query = select(func.count()).select_from(self.model).where(self.model.id == id) # type: ignore
        result = await self.db.execute(query)
        return result.scalar_one() > 0

    async def bulk_create(self, objects: List[CreateSchemaType]) -> List[ModelType]:
        """
        Create multiple records at once.
        
        Args:
            objects: List of creation schemas
            
        Returns:
            List of created model instances
        """
        db_objects = []
        for obj_in in objects:
            obj_data = obj_in.model_dump()
            obj_data["id"] = self._generate_id()
            
            if hasattr(self.model, "created_at"):
                obj_data["created_at"] = datetime.utcnow()
            if hasattr(self.model, "updated_at"):
                obj_data["updated_at"] = datetime.utcnow()

            db_obj = self.model(**obj_data) # type: ignore
            db_objects.append(db_obj)

        self.db.add_all(db_objects)
        await self.db.commit()
        
        for db_obj in db_objects:
            await self.db.refresh(db_obj)
        
        return db_objects