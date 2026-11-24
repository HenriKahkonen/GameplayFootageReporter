"""
Module for all of the sqlite related functions and classes.
"""

from collections import defaultdict
from datetime import datetime
from pathlib import Path

from sqlalchemy import JSON, ForeignKey, DateTime, UniqueConstraint, create_engine, select, event, Integer, func
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship, Session
)

from utils.game_footage_data_classes import GameSummary

class Base(DeclarativeBase):
    """Base class. Possibly useless?"""
    pass

class Game(Base):
    """SQLite database class for game summary."""
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_name: Mapped[str] = mapped_column(unique=True)

    release_year: Mapped[int | None]
    total_video_size_in_mb: Mapped[float]
    total_video_length_secs: Mapped[int]
    video_avg_length_secs: Mapped[float]
    video_avg_size_per_min_in_mb: Mapped[float]
    file_ext_list: Mapped[list[str]] = mapped_column(JSON)
    video_files: Mapped[int]
    non_video_files: Mapped[int]
    obsidian_note_found: Mapped[bool]
    md_size: Mapped[float | None]
    platforms: Mapped[list[str]] = mapped_column(JSON)
    categories: Mapped[list[str]] = mapped_column(JSON)
    genres: Mapped[list[str]] = mapped_column(JSON)
    rating: Mapped[float | None]
    playtime_mins: Mapped[int | None]
    game_series: Mapped[str | None]
    developers: Mapped[list[str]] = mapped_column(JSON)
    publishers: Mapped[list[str]] = mapped_column(JSON)

    footage_files: Mapped[list["FootageFile"]] = relationship(
        back_populates="game", cascade="all, delete-orphan"
    )

class FootageFile(Base):
    """SQLite database class for game footage file."""
    __tablename__ = "footage_files"
    __table_args__ = (UniqueConstraint("game_id", "file_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    file_name: Mapped[str]  # path inside the game folder, e.g. "subfolder/file.mp4"
    video_length_in_seconds: Mapped[int]
    file_size_in_mb: Mapped[float]
    file_extension: Mapped[str]
    size_per_min_in_mb: Mapped[float]

    game: Mapped["Game"] = relationship(back_populates="footage_files")

class ReportMetadata(Base):
    """SQLite database class for game footage file."""
    __tablename__ = "report_metadata"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_generated_at: Mapped[datetime] = mapped_column(DateTime)
    games_count: Mapped[int]
    obsidian_notes_count: Mapped[int]
    file_size_total_in_gb: Mapped[float]
    average_total_video_size_in_mb: Mapped[float]
    average_total_video_length_in_secs: Mapped[float]
    average_size_per_min_in_mb: Mapped[float]
    average_rating: Mapped[float | None]
    platforms: Mapped[list[str]] = mapped_column(JSON)
    categories: Mapped[list[str]] = mapped_column(JSON)
    genres: Mapped[list[str]] = mapped_column(JSON)
    file_extensions: Mapped[list[str]] = mapped_column(JSON)



class GameplayFootageDatabase:
    """Creates and manages the sqlite database for game summaries and footage files."""

    def __init__(self, db_path, dummy: bool = False):
        self.dummy = dummy
        if self.dummy:
            return

        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{db_path}")

        @event.listens_for(self.engine, "connect")
        def _enable_fk(dbapi_conn, _record):
            dbapi_conn.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(self.engine)

    def upsert_game(self, summary : GameSummary) -> None:
        """Insert a GameSummary, or update the existing row with the same game_name."""
        if self.dummy:
            return

        data = summary.to_dict()
        with Session(self.engine) as session, session.begin():
            game = session.scalar(select(Game).where(Game.game_name == data["game_name"]))
            if game is None:
                session.add(Game(**data))
            else:
                for key, value in data.items():
                    setattr(game, key, value)

    def replace_footage_files(self, clips: list) -> None:
        """Replace the stored footage files of every game found in `clips`.
        Each game must already exist in the games table."""
        if self.dummy:
            return

        by_game = defaultdict(list)
        for clip in clips:
            by_game[clip.game_name].append(clip)

        with Session(self.engine) as session, session.begin():
            for game_name, game_clips in by_game.items():
                game = session.scalar(select(Game).where(Game.game_name == game_name))
                if game is None:
                    raise ValueError(f"No game '{game_name}' in database; add it first.")

                # delete old files
                game.footage_files.clear()
                session.flush()

                game.footage_files.extend(
                    FootageFile(
                        file_name=c.file_name,
                        video_length_in_seconds=c.video_length_in_seconds,
                        file_size_in_mb=c.file_size_in_mb,
                        file_extension=c.file_extension,
                        size_per_min_in_mb=c.size_per_min_in_mb,
                    )
                    for c in game_clips
                )

    def get_game(self, game_name: str) -> Game | None:
        """Selects the game from the DB with the matching game name."""
        if self.dummy:
            return None
        with Session(self.engine, expire_on_commit=False) as session:
            return session.scalar(select(Game).where(Game.game_name == game_name))

    def list_games(self) -> list[Game]:
        """Lists all of the games in the database."""
        if self.dummy:
            return []
        with Session(self.engine, expire_on_commit=False) as session:
            return list(session.scalars(select(Game).order_by(Game.game_name)))

    def create_report(self) -> ReportMetadata | None:
        """Compute summary stats from the current contents of the games table,
        store them as a new ReportMetadata row and return it.

        Returns None if dummy or if the games table is empty."""
        if self.dummy:
            return None

        with Session(self.engine, expire_on_commit=False) as session, session.begin():
            (
                games_count,
                notes_count,
                total_size_mb,
                total_length_secs,
                avg_rating,
            ) = session.execute(
                select(
                    func.count(Game.id),
                    func.coalesce(func.sum(Game.obsidian_note_found.cast(Integer)), 0),
                    func.coalesce(func.sum(Game.total_video_size_in_mb), 0.0),
                    func.coalesce(func.sum(Game.total_video_length_secs), 0),
                    func.avg(Game.rating),  # ignores NULLs automatically
                )
            ).one()

            if games_count == 0:
                return None

            def merged(column) -> list[str]:
                values: set[str] = set()
                for (items,) in session.execute(select(column)):
                    values.update(items or [])
                return sorted(values)

            # Total size over total minutes, so long games weigh more than short ones
            size_per_min = total_size_mb / (total_length_secs / 60) if total_length_secs else 0.0

            report = ReportMetadata(
                report_generated_at=datetime.now(),
                games_count=games_count,
                obsidian_notes_count=notes_count,
                file_size_total_in_gb=round(total_size_mb / 1024, 2),
                average_total_video_size_in_mb=round(total_size_mb / games_count, 2),
                average_total_video_length_in_secs=round(total_length_secs / games_count, 2),
                average_size_per_min_in_mb=round(size_per_min, 2),
                average_rating=round(avg_rating, 2) if avg_rating is not None else None,
                platforms=merged(Game.platforms),
                categories=merged(Game.categories),
                genres=merged(Game.genres),
                file_extensions=merged(Game.file_ext_list),
            )
            session.add(report)

        return report

    def latest_report(self) -> ReportMetadata | None:
        """Return the most recently generated report, or None."""
        if self.dummy:
            return None
        with Session(self.engine, expire_on_commit=False) as session:
            return session.scalar(
                select(ReportMetadata).order_by(ReportMetadata.report_generated_at.desc())
            )
