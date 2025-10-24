from datetime import datetime
from sqlalchemy.orm import Session
from src.db_setup import get_engine, init_db, Driver, Constructor, Circuit, Race, Result
from src.api_fetch import fetch_constructors, fetch_circuits, fetch_drivers, fetch_results

def to_date(s: str | None):
    if not s:
        return None
    return datetime.fromisoformat(s).date()

def ingest_season(season: int):
    engine = get_engine()
    with Session(engine) as ses:
        # Drivers
        djson = fetch_drivers(season)
        for d in djson["MRData"]["DriverTable"]["Drivers"]:
            ses.merge(Driver(
                driver_id=d["driverId"],
                code=d.get("code"),
                given_name=d["givenName"],
                family_name=d["familyName"],
                nationality=d.get("nationality"),
                date_of_birth=to_date(d.get("dateOfBirth"))
            ))

        # Constructors
        cjson = fetch_constructors(season)
        for c in cjson["MRData"]["ConstructorTable"]["Constructors"]:
            ses.merge(Constructor(
                constructor_id=c["constructorId"],
                name=c["name"],
                nationality=c.get("nationality")
            ))

        # Circuits + Races + Results
        rjson = fetch_results(season)
        for race in rjson["MRData"]["RaceTable"]["Races"]:
            cir = race["Circuit"]
            ses.merge(Circuit(
                circuit_id=cir["circuitId"],
                name=cir["circuitName"],
                location=cir["Location"]["locality"],
                country=cir["Location"]["country"]
            ))
            race_id = int(race["round"]) + int(race["season"]) * 100  # id déterministe simple
            ses.merge(Race(
                race_id=race_id,
                season=int(race["season"]),
                round=int(race["round"]),
                circuit_id=cir["circuitId"],
                name=race["raceName"],
                date=to_date(race.get("date"))
            ))
            for res in race["Results"]:
                pos = res.get("position")
                ses.add(Result(
                    race_id=race_id,
                    driver_id=res["Driver"]["driverId"],
                    constructor_id=res["Constructor"]["constructorId"],
                    grid=int(res.get("grid") or 0),
                    position=int(pos) if (pos and pos.isdigit()) else None,
                    points=float(res.get("points") or 0.0),
                    status=res.get("status", "")
                ))
        ses.commit()

def ingest_range(start_season: int, end_season: int):
    init_db()
    for s in range(start_season, end_season + 1):
        print(f"Ingestion saison {s} …")
        ingest_season(s)
    print("Ingestion terminée.")
