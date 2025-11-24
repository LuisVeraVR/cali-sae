"""
Report Repository Interface - Defines the contract for report persistence
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from ..entities.report import Report


class ReportRepositoryInterface(ABC):
    """Abstract interface for report repository"""

    @abstractmethod
    def create(self, report: Report) -> Report:
        """Create a new report entry"""
        pass

    @abstractmethod
    def get_by_id(self, report_id: int) -> Optional[Report]:
        """Get a report by ID"""
        pass

    @abstractmethod
    def get_all(self) -> List[Report]:
        """Get all reports"""
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> List[Report]:
        """Get all reports for a specific user"""
        pass

    @abstractmethod
    def get_by_company(self, company: str) -> List[Report]:
        """Get all reports for a specific company"""
        pass

    @abstractmethod
    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Report]:
        """Get reports within a date range"""
        pass

    @abstractmethod
    def delete(self, report_id: int) -> bool:
        """Delete a report by ID"""
        pass

    @abstractmethod
    def get_total_records_processed(self) -> int:
        """Get total number of records processed across all reports"""
        pass

    @abstractmethod
    def get_statistics(self) -> dict:
        """Get statistics about reports"""
        pass
