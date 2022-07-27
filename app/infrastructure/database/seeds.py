import logging
from typing import Any, Dict, Iterable

from sqlmodel import SQLModel, Session

from app.domain.models.movie import Movie, MovieCreate

logger = logging.getLogger(__name__)

# TODO implement your own data seeding or remove this code. Also update app/api/app.py:register_events function

def _populate_table(
    db: Session, table: SQLModel, values: Iterable[Dict[str, Any]],
):
    name = table.__tablename__
    logger.info(f"Seeding table {name}")
    for v in values:
        db.add(table.from_orm(v))
    db.commit()
    logger.info(f"Seeded table {name} successfully")

def _populate_movies(db: Session) -> None:
    values = [
        MovieCreate(title="2001: A Space Odyssey", description="An imposing black structure provides a connection between the past and the future in this enigmatic adaptation of a short story by revered sci-fi author Arthur C. Clarke. When Dr. Dave Bowman (Keir Dullea) and other astronauts are sent on a mysterious mission, their ship's computer system, HAL, begins to display increasingly strange behavior, leading up to a tense showdown between man and machine that results in a mind-bending trek through space and time.", movieYear=1968),
        MovieCreate(title="Star Wars: The Last Jedi", description="Rey develops her newly discovered abilities with the guidance of Luke Skywalker, who is unsettled by the strength of her powers. Meanwhile, the Resistance prepares for battle with the First Order.", movieYear=2017),
        MovieCreate(title="The Fly", description="When scientist Seth Brundle (Jeff Goldblum) completes his teleportation device, he decides to test its abilities on himself. Unbeknownst to him, a housefly slips in during the process, leading to a merger of man and insect. Initially, Brundle appears to have undergone a successful teleportation, but the fly's cells begin to take over his body. As he becomes increasingly fly-like, Brundle's girlfriend (Geena Davis) is horrified as the person she once loved deteriorates into a monster.", movieYear=1986)
    ]
    _populate_table(db, Movie, values)


def run(db: Session) -> None:
    logger.info("Initializing databases")
    logger.info("Populating database")
    for fn in [_populate_movies]:
        fn(db)
    logger.info("Finished populating database")