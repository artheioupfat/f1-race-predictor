from sqlalchemy import text
from src.db_setup import get_engine

QUERIES = [
    ("nb courses par saison",
     "SELECT season, COUNT(*) AS n_races FROM races GROUP BY season ORDER BY season"),
    ("nb résultats total",
     "SELECT COUNT(*) FROM results"),
    ("résultats sans position (DNF/DQ/etc.)",
     "SELECT COUNT(*) FROM results WHERE position IS NULL"),
    ("répartition statuts top 10",
     "SELECT status, COUNT(*) c FROM results GROUP BY status ORDER BY c DESC LIMIT 10"),
    ("top 5 pilotes par points cumulés (2018-2024)",
     """
     SELECT d.family_name || ' ' || d.given_name AS driver, SUM(r.points) pts
     FROM results r JOIN drivers d ON r.driver_id=d.driver_id
     GROUP BY driver ORDER BY pts DESC LIMIT 5
     """),
    ("cohérence grid (positions de départ manquantes ou 0)",
     "SELECT COUNT(*) FROM results WHERE grid IS NULL OR grid=0"),
    ("courses sans résultats (devrait être 0)",
     """
     SELECT COUNT(*) FROM races ra
     LEFT JOIN results re ON re.race_id=ra.race_id
     WHERE re.result_id IS NULL
     """),
]

def run_checks():
    e = get_engine()
    with e.connect() as c:
        for name, sql in QUERIES:
            print(f"\n== {name}")
            rs = c.execute(text(sql))
            for row in rs:
                print(tuple(row))

if __name__ == "__main__":
    run_checks()
