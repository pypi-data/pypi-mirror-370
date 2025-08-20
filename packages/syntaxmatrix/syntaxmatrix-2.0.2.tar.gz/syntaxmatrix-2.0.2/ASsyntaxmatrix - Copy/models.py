# syntaxmatrix/models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Workspace(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(64), unique=True, nullable=False)
    llm_provider  = db.Column(db.String(24), default="openai")
    llm_model     = db.Column(db.String(48), default="gpt-3.5-turbo")
    llm_api_key   = db.Column(db.LargeBinary)      # we'll encrypt later

    def __repr__(self):
        return f"<Workspace {self.name}>"
