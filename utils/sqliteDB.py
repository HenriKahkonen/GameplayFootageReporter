import pysqlite3 as sqlite3
import settings
from typing import Optional
from datetime import datetime
from pathlib import Path
from sqlalchemy import foreignkey, create_engine, select, event
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship, Session
)
import os





class Base(DeclarativeBase):
    pass

class Game(Base):
    """
    Data class for every game
    """
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    folder_path: Mapped[str]

    files: Mapped[list["VideoFile"]] = relationship(
        back_populates="game", cascade="all, delete-orphan"
    )

class GameplayfootageSQLiteDB:
    """
    SQLite database that stores data about the footage files and folders.
    """

    def __init__(
        self,
        db_path: str,
        report_date: str = datetime.now().isoformat(),
        debug: bool = False,
        ):

        """
        Initialize database connection, create .db file if it doesn't exist yet.
        
        Args:
            db_path: Path to SQLite database file. Created if doesn't exist.
        """

        self.db_path = Path(db_path)
        self.conn: Optional[sqlite3.Connection] = None

    def set_debug(self, debug_status: bool):
        """Set self-debug status."""
        self.debug = debug_status

    def connect(self) -> sqlite3.Connection:
        """Open Db connection, creates the Db file if needed."""
        if self.conn is None:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def destroy_db_file(self) -> None:
        """Removes db file. If debug is not set to True, throws permission error."""
        if self.debug != True:
            raise PermissionError("Program tried to delete the footage database. If deletion was intentional, set the database class state to debug = True with db.set_debug(True) first.")
        else:
            try:
                ## TODO: guardrails to make sure this doesn't delete anything not intended
                os.remove(self.db_path)
            except FileNotFoundError:
                print(f"Error: Tried to remove database file at {self.db_path}, but db file was not found.")
                raise

    def initialize_tables(self) -> None:
        """Initializes the tables needed for the database"""

        conn = self.connect()
        cursor = conn.cursor()

        ### Games folders
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id  INTEGER PRIMARY KEY AUTOINCREMENT
                
            )
        """) 


# where i realized i don't want to write all this manually