from sqlalchemy import Integer, String, DateTime, ForeignKey, Float, BIGINT, Text, JSON, Boolean
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Table
from datetime import datetime

from novatrace.connect import *

Base = declarative_base()

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)

    created_at = Column(DateTime, default=lambda: datetime.now(hora))
    projects = relationship("Project", back_populates="session")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    session_id = Column(Integer, ForeignKey("sessions.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(hora))

    session = relationship("Session", back_populates="projects")
    traces = relationship("Trace", back_populates="project")

class TraceTypes(Base):
    __tablename__ = "trace_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)

    traces = relationship("Trace", back_populates="trace_types")

class Trace(Base):
    __tablename__ = "traces"
    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey("trace_types.id"))
    input_data = Column(Text, nullable=False)
    output_data = Column(Text, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(hora))
    request_time = Column(DateTime, nullable=False)    # cuando se recibe el input
    response_time = Column(DateTime, nullable=False)   # cuando se genera output
    duration_ms = Column(Float, nullable=False)      

    user_external_id = Column(String(255), nullable=True)  # ID del usuario de el proyecto
    user_external_name = Column(String(255), nullable=True)  # nombre del usuario de el proyecto
    model_provider = Column(String(255), nullable=True)  # proveedor del modelo (ej. "anthropic", "openai")
    model_name = Column(String(255), nullable=True)  # nombre del modelo utilizado (ej. "claude-3-haiku-20240307", "gpt-4-turbo")
    model_input_cost = Column(Float, nullable=True)  # costo por token de entrada del modelo
    model_output_cost = Column(Float, nullable=True)  # costo por token de salida del
    call_cost = Column(Float, nullable=True)  # costo total de la llamada (input + output)

    input_tokens = Column(BIGINT, nullable=True)  # tokens de entrada
    output_tokens = Column(BIGINT, nullable=True)  # tokens de salida 

    project = relationship("Project", back_populates="traces")
    trace_types = relationship("TraceTypes", back_populates="traces")

