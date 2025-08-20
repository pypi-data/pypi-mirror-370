import os
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, ForeignKey, UniqueConstraint  
from syntaxmatrix.project_root import detect_project_root

# Location = client_app_root/data/llms.db
_CLIENT_DIR = detect_project_root()
DB_PATH = os.path.join(_CLIENT_DIR, "data", "llms.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()

# Workspace table
# ─────────────────────────────────────────────────────────────
class Workspace(Base):
    __tablename__ = "workspace"
    id           = Column(Integer, primary_key=True)
    name         = Column(String(64), unique=True, nullable=False)
    llm_provider = Column(String(24), default="openai")
    llm_model    = Column(String(48), default="text-embedding-3-small")
    llm_api_key  = Column(LargeBinary)          

    profiles = relationship(
        "LLMProfile",
        back_populates="workspace",
        cascade="all, delete-orphan",
    )


def get_workspace(name: str = "default") -> Workspace:
    """Return the workspace row (creates it if missing)."""
    session = SessionLocal()
    ws = session.query(Workspace).filter_by(name=name).first()
    if not ws:
        ws = Workspace(name=name)
        session.add(ws)
        session.commit()
    return ws


#  LLMProfile table  (one workspace → many profiles)
# ─────────────────────────────────────────────────────────────
class LLMProfile(Base):
    __tablename__ = "llm_profiles"
    id           = Column(Integer, primary_key=True)
    workspace_id = Column(Integer, ForeignKey("workspace.id"), default=1)  # always ties back to default workspace for now
    name         = Column(String(64), nullable=False, unique=True)         # e.g. "chat_main", "analysis_fast"
    purpose_tag  = Column(String(32), default="general")                   # optional hint like "generation" / "embedding"
    provider     = Column(String(24),  nullable=False)                     # "openai", "anthropic", …
    model        = Column(String(48),  nullable=False)                     # "gpt-4o-mini", "claude-3-haiku", …
    api_key      = Column(LargeBinary)                                     # encrypted later

    workspace = relationship("Workspace", back_populates="profiles")

# ─────────────────────────────────────────────────────────────
class LLMModel(Base):
    """
    Catalog row: one provider-model-purpose that an admin can select
    when creating profiles.  Unique on (provider, model).
    """
    __tablename__ = "llm_models"
    id           = Column(Integer, primary_key=True)
    provider     = Column(String(24),  nullable=False)
    model        = Column(String(64),  nullable=False)
    purpose_tag  = Column(String(32),  nullable=False)   
    desc  = Column(String(32),  nullable=False)   

    __table_args__ = (
        UniqueConstraint("provider", "model", name="uq_provider_model"),
    )


# ─────────────────────────────────────────────────────────────

# class LLMService(Base):
#     """
#     Per-workspace LLM “services” (primary, embedding, classification, etc.).
#     One row per (workspace_id, service_type).
#     """
#     __tablename__ = "llm_services"

#     id            = Column(Integer, primary_key=True)
#     workspace_id  = Column(Integer, ForeignKey("workspace.id"), nullable=False)
#     service_type  = Column(String(32),  nullable=False)   # e.g. 'primary', 'embedding'
#     provider      = Column(String(24),  nullable=False)   # e.g. 'openai'
#     model         = Column(String(64),  nullable=False)   # e.g. 'gpt-4', 'text-embedding-ada-002'
#     api_key       = Column(LargeBinary, nullable=False)

#     __table_args__ = (
#         UniqueConstraint("workspace_id", "service_type", name="uq_ws_service"),
#     )

#     # convenience backref to Workspace
#     workspace = relationship("Workspace", back_populates="services")

Base.metadata.create_all(engine)