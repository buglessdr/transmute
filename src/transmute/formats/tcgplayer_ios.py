"""
Minimal TCGPlayer iOS paste-import format.
"""

from typing import ClassVar

from transmute.core.models import CardEntry
from transmute.formats.base import FormatHandler

class TCGPlayerIOSHandler(FormatHandler):
    """
    Minimal CSV format compatible with TCGPlayer iOS paste importer.
    """

    name: ClassVar[str] = "tcgplayer_ios"
    display_name: ClassVar[str] = "TCGPlayer (iOS Import)"
    required_columns: ClassVar[set[str]] = set()

    HEADERS = [
        "Quantity",
        "Name",
        "Set Code",
        "Printing",
        "Condition",
        "Language",
    ]

    def parse_row(self, row: dict[str, str]):
        raise NotImplementedError("tcgplayer_ios is export-only")

    def format_row(self, entry: CardEntry) -> dict[str, str]:
        return {
            "Quantity": str(entry.quantity),
            "Name": entry.card.name,
            "Set Code": entry.card.set_code or "",
            "Printing": entry.finish.value,  # Normal / Foil
            "Condition": "Near Mint",
            "Language": "English",
        }

    def get_headers(self) -> list[str]:
        return self.HEADERS