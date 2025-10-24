from sqlalchemy import (
    Column, Integer, String, Float, Date, ForeignKey, create_engine
)
from sqlalchemy.orm import declarative_base, relationship, Session
from src.config import DB_PATH
from sqlalchemy import text

Base = declarative_base()

class Driver(Base):
    __tablename__ = "drivers"
    driver_id = Column(String, primary_key=True)  # Ergast uses alphanum ids
    code = Column(String, nullable=True)
    given_name = Column(String)
    family_name = Column(String)
    nationality = Column(String)
    date_of_birth = Column(Date, nullable=True)

class Constructor(Base):
    __tablename__ = "constructors"
    constructor_id = Column(String, primary_key=True)
    name = Column(String)
    nationality = Column(String)

class Circuit(Base):
    __tablename__ = "circuits"
    circuit_id = Column(String, primary_key=True)
    name = Column(String)
    location = Column(String)
    country = Column(String)

class Race(Base):
    __tablename__ = "races"
    race_id = Column(Integer, primary_key=True, autoincrement=False)  # Ergast numeric
    season = Column(Integer, index=True)
    round = Column(Integer)
    circuit_id = Column(String, ForeignKey("circuits.circuit_id"))
    name = Column(String)
    date = Column(Date)

    circuit = relationship("Circuit")

class Result(Base):
    __tablename__ = "results"
    result_id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey("races.race_id"), index=True)
    driver_id = Column(String, ForeignKey("drivers.driver_id"), index=True)
    constructor_id = Column(String, ForeignKey("constructors.constructor_id"))
    grid = Column(Integer)
    position = Column(Integer, nullable=True)  # DNF/DQ -> None
    points = Column(Float)
    status = Column(String)

    race = relationship("Race")
    driver = relationship("Driver")
    constructor = relationship("Constructor")

def get_engine():
    return create_engine(f"sqlite:///{DB_PATH}")

def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)
    
    with engine.connect() as c:
        c.execute(text("CREATE INDEX IF NOT EXISTS idx_results_race ON results(race_id);"))
        c.execute(text("CREATE INDEX IF NOT EXISTS idx_results_driver ON results(driver_id);"))
        c.execute(text("CREATE INDEX IF NOT EXISTS idx_races_season ON races(season);"))
        c.commit()

if __name__ == "__main__":
    init_db()
    print(f"DB initialisée -> {DB_PATH}")
