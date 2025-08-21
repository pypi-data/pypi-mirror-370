from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Column, DateTime, ForeignKey, Text  # type: ignore[import-untyped]
from sqlalchemy.dialects.postgresql import JSONB  # type: ignore[import-untyped]
from sqlalchemy.orm import backref, relationship  # type: ignore[import-untyped]

from ckan import model, types
from ckan.model import Resource
from ckan.model.types import make_uuid
from ckan.plugins import toolkit as tk


class ResourceDocs(tk.BaseModel):  # type: ignore[call-arg]
    """Model for storing resource documentation.

    Attributes:
        id: Unique identifier for the resource docs
        resource_id: Reference to the resource this documentation belongs to
        docs: JSON field containing the documentation data
        validation_schema: Optional JSON schema for validating the docs
        modified_at: Timestamp when the documentation was last modified
    """

    __tablename__ = "resource_docs"

    id = Column(Text, primary_key=True, default=make_uuid)  # type: ignore[assignment]
    resource_id = Column(Text, ForeignKey("resource.id", ondelete="CASCADE"), nullable=False, unique=True)  # type: ignore[assignment]
    docs = Column(JSONB, nullable=False, default=dict)  # type: ignore[assignment]
    validation_schema: dict[str, Any] = Column(JSONB, nullable=True, default=dict)  # type: ignore[assignment]
    modified_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))  # type: ignore[assignment]

    resource = relationship(  # type: ignore
        Resource,
        backref=backref("resource_docs", uselist=False),
    )

    def __repr__(self):
        """Return a string representation of the resource docs."""
        return f"[ResourceDocs id: {self.id}, resource_id: {self.resource_id}]"

    @classmethod
    def get_by_resource_id(cls, resource_id: str) -> ResourceDocs | None:
        """Get resource docs by resource ID."""
        return model.Session.query(cls).filter(cls.resource_id == resource_id).first()  # type: ignore[return-value]

    @classmethod
    def get_by_resources_ids(cls, resources_ids: list[str]) -> dict[str, ResourceDocs]:
        """Get multiple resource docs by resource IDs."""
        return {
            res_doc.resource_id: res_doc
            for res_doc in model.Session.query(cls).filter(cls.resource_id.in_(resources_ids))
        }

    @classmethod
    def create(
        cls, resource_id: str, docs: dict[str, Any], validation_schema: dict[str, Any] | None = None
    ) -> ResourceDocs:
        """Create new resource docs."""
        resource_docs = cls(
            resource_id=resource_id,
            docs=docs,
            validation_schema=validation_schema,
            modified_at=datetime.now(tz=timezone.utc),
        )
        model.Session.add(resource_docs)
        model.Session.commit()
        return resource_docs

    def update(self, docs: dict[str, Any], validation_schema: dict[str, Any] | None = None) -> ResourceDocs:
        """Update the docs and modified_at timestamp."""
        self.docs = docs
        self.modified_at = datetime.now(tz=timezone.utc)

        if validation_schema is not None:
            self.validation_schema = validation_schema

        model.Session.commit()

        return self

    def delete(self) -> None:
        """Delete resource docs."""
        model.Session.delete(self)
        model.Session.commit()

    def dictize(self, context: types.Context) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "id": self.id,
            "resource_id": self.resource_id,
            "docs": self.docs,
            "validation_schema": self.validation_schema,
            "modified_at": self.modified_at.isoformat(),
        }
