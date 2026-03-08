import datetime
import uuid
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, DateTime, ForeignKey, Uuid

from archilog.config import config
engine = create_engine(config.DATABASE_URL, echo=config.DEBUG)
metadata = MetaData()

table_cagnotte = Table(
    "cagnotte",
    metadata,
    Column("name", String, primary_key=True),
    Column("date", DateTime, default=datetime.datetime.now),
    Column("montant", Integer)
)

membres_table = Table(
    "membres",
    metadata,
    Column("nom", String, primary_key=True),
    Column("cagnotte", String, ForeignKey("cagnotte.name"), primary_key=True)
)

depenses_table = Table(
    "depenses",
    metadata,
    Column("id", Uuid, primary_key=True, default=uuid.uuid4),
    Column("cagnotte", String, ForeignKey("cagnotte.name"), primary_key=True),
    Column("nom", String, ForeignKey("membres.nom"), primary_key=True),
    Column("depense", String),
    Column("date", DateTime, default=datetime.datetime.now),
    Column("montant", Integer)
)

def init_db():
    metadata.create_all(engine)