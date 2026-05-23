from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.db.base_class import Base

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    filename = Column(String, nullable=False)
    s3_path = Column(String, nullable=False)
    target_column = Column(String)
    protected_attributes = Column(JSON)
    num_rows = Column(Integer)
    num_cols = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="datasets")
    reports = relationship("FairnessReport", back_populates="dataset", cascade="all, delete")

class Model(Base):
    __tablename__ = "models"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    model_type = Column(String)
    s3_path = Column(String)
    hyperparameters = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="models")
    reports = relationship("FairnessReport", back_populates="model", cascade="all, delete")

class FairnessReport(Base):
    __tablename__ = "fairness_reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    model_id = Column(String, ForeignKey("models.id"))
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    metrics = Column(JSON)
    shap_data = Column(JSON)
    ai_consultant_summary = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    model = relationship("Model", back_populates="reports")
    dataset = relationship("Dataset", back_populates="reports")
