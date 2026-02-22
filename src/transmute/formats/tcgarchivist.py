"""
Handler for TCG Archivist CSV export format.
"""

from typing import ClassVar
from collections import defaultdict
from pathlib import Path
import csv

from transmute.core.enums import Condition, Finish, Language
from transmute.core.models import Card, CardEntry, Collection
from transmute.formats.base import FormatHandler


class TCGArchivistHandler(FormatHandler):
    """
    Handler for TCG Archivist CSV format.

    Expected columns:
    Location,Name,Set code,Collector number,Finish,
    Quantity,Scryfall ID,Colors,CMC,Type
    """

    name: ClassVar[str] = "tcgarchivist"
    display_name: ClassVar[str] = "TCG Archivist"
    required_columns: ClassVar[set[str]] = {
        "Name",
        "Set code",
        "Finish",
        "Quantity",
        "Scryfall ID",
    }

    def parse_row(self, row: dict[str, str]) -> CardEntry:
        """
        Not used — we override read() to handle merging.
        """
        raise NotImplementedError("TCGArchivistHandler uses custom read()")

    def read(self, file_path: Path) -> Collection:
        """
        Custom read implementation to merge duplicates by:
        (scryfall_id, finish)
        """

        merged: dict[tuple[str, str], dict] = defaultdict(
            lambda: {
                "name": None,
                "set_code": None,
                "collector_number": None,
                "quantity": 0,
            }
        )

        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=self.delimiter)

            for row in reader:
                scryfall_id = row["Scryfall ID"].strip()
                finish_raw = row["Finish"].strip().lower()

                key = (scryfall_id, finish_raw)

                merged[key]["name"] = row["Name"].strip()
                merged[key]["set_code"] = row["Set code"].strip().upper()
                merged[key]["collector_number"] = (
                    row.get("Collector number", "").strip() or None
                )
                merged[key]["quantity"] += int(row["Quantity"])

        collection = Collection(source_format=self.name)

        for (scryfall_id, finish_raw), data in merged.items():

            finish = (
                Finish.FOIL if finish_raw == "foil" else Finish.NONFOIL
            )

            card = Card(
                name=data["name"],
                scryfall_id=scryfall_id,
                set_code=data["set_code"],
                collector_number=data["collector_number"],
            )

            entry = CardEntry(
                card=card,
                quantity=data["quantity"],
                finish=finish,
                condition=Condition.NEAR_MINT,
                language=Language.ENGLISH,
            )

            collection.add(entry)

        return collection

    def format_row(self, entry: CardEntry) -> dict[str, str]:
        """
        Not used for export.
        """
        raise NotImplementedError("TCGArchivistHandler is import-only")

    def get_headers(self) -> list[str]:
        """
        Not used for export.
        """
        return []