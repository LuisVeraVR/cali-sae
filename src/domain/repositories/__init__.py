"""
Domain repository interfaces
"""
from .user_repository import UserRepositoryInterface
from .report_repository import ReportRepositoryInterface

__all__ = ['UserRepositoryInterface', 'ReportRepositoryInterface']
