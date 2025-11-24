"""
Report entity - Represents an audit report
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Report:
    """Audit report entity for tracking processing activities"""

    id: Optional[int]
    username: str
    company: str  # Company name (e.g., 'AGROBUITRON', 'JUAN CAMILO ROSAS', 'EL PAISANO')
    filename: str  # Name of the processed file
    records_processed: int  # Number of records/invoices processed
    created_at: datetime
    file_size: int  # Size in bytes

    def get_file_size_mb(self) -> float:
        """Get file size in megabytes"""
        return self.file_size / (1024 * 1024)

    def format_date(self, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format the creation date"""
        return self.created_at.strftime(format_str)

    def get_short_date(self) -> str:
        """Get creation date in short format (YYYY-MM-DD)"""
        return self.format_date("%Y-%m-%d")

    def get_datetime(self) -> str:
        """Get creation date with time"""
        return self.format_date("%Y-%m-%d %H:%M:%S")

    def __repr__(self) -> str:
        return (
            f"Report(id={self.id}, user='{self.username}', "
            f"company='{self.company}', records={self.records_processed})"
        )
