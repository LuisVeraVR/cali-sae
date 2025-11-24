"""
SQLite implementation of Report Repository
"""
import sqlite3
from typing import List, Optional
from datetime import datetime

from ...domain.entities.report import Report
from ...domain.repositories.report_repository import ReportRepositoryInterface


class SQLiteReportRepository(ReportRepositoryInterface):
    """SQLite implementation of report repository"""

    def __init__(self, db_path: str = "facturas_users.db"):
        """
        Initialize the repository

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    company TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    records_processed INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_size INTEGER DEFAULT 0
                )
            ''')
            conn.commit()

    def create(self, report: Report) -> Report:
        """Create a new report entry"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO reports (username, company, filename, records_processed, created_at, file_size)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (
                    report.username,
                    report.company,
                    report.filename,
                    report.records_processed,
                    report.created_at,
                    report.file_size
                )
            )
            conn.commit()
            report.id = cursor.lastrowid
            return report

    def get_by_id(self, report_id: int) -> Optional[Report]:
        """Get a report by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM reports WHERE id = ?', (report_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_report(row)
            return None

    def get_all(self) -> List[Report]:
        """Get all reports ordered by creation date (newest first)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM reports ORDER BY created_at DESC')
            rows = cursor.fetchall()
            return [self._row_to_report(row) for row in rows]

    def get_by_username(self, username: str) -> List[Report]:
        """Get all reports for a specific user"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM reports WHERE username = ? ORDER BY created_at DESC',
                (username,)
            )
            rows = cursor.fetchall()
            return [self._row_to_report(row) for row in rows]

    def get_by_company(self, company: str) -> List[Report]:
        """Get all reports for a specific company"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM reports WHERE company = ? ORDER BY created_at DESC',
                (company,)
            )
            rows = cursor.fetchall()
            return [self._row_to_report(row) for row in rows]

    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Report]:
        """Get reports within a date range"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT * FROM reports
                   WHERE created_at BETWEEN ? AND ?
                   ORDER BY created_at DESC''',
                (start_date, end_date)
            )
            rows = cursor.fetchall()
            return [self._row_to_report(row) for row in rows]

    def delete(self, report_id: int) -> bool:
        """Delete a report by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM reports WHERE id = ?', (report_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False

    def get_total_records_processed(self) -> int:
        """Get total number of records processed across all reports"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT SUM(records_processed) FROM reports')
            result = cursor.fetchone()[0]
            return result if result else 0

    def get_statistics(self) -> dict:
        """Get statistics about reports"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Total reports
            cursor.execute('SELECT COUNT(*) FROM reports')
            total_reports = cursor.fetchone()[0]

            # Total records processed
            cursor.execute('SELECT SUM(records_processed) FROM reports')
            total_records = cursor.fetchone()[0] or 0

            # Reports by company
            cursor.execute('''
                SELECT company, COUNT(*) as count, SUM(records_processed) as records
                FROM reports
                GROUP BY company
            ''')
            by_company = {row[0]: {'count': row[1], 'records': row[2]} for row in cursor.fetchall()}

            # Reports by user
            cursor.execute('''
                SELECT username, COUNT(*) as count, SUM(records_processed) as records
                FROM reports
                GROUP BY username
            ''')
            by_user = {row[0]: {'count': row[1], 'records': row[2]} for row in cursor.fetchall()}

            return {
                'total_reports': total_reports,
                'total_records': total_records,
                'by_company': by_company,
                'by_user': by_user
            }

    def _row_to_report(self, row) -> Report:
        """Convert a database row to a Report entity"""
        return Report(
            id=row['id'],
            username=row['username'],
            company=row['company'],
            filename=row['filename'],
            records_processed=row['records_processed'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.now(),
            file_size=row['file_size'] if row['file_size'] else 0
        )
