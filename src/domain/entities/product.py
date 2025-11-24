"""
Product entity - Represents a product line in an invoice
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class Product:
    """Product line item in an invoice"""

    name: str
    underlying_code: str
    unit_of_measure: str
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal
    iva_percentage: Decimal
    line_number: Optional[int] = None

    def format_decimal(self, value: Decimal, decimals: int = 5) -> str:
        """Format decimal with comma as decimal separator"""
        formatted = f"{value:.{decimals}f}"
        return formatted.replace('.', ',')

    def get_formatted_quantity(self) -> str:
        """Get quantity formatted with 5 decimals and comma"""
        return self.format_decimal(self.quantity)

    def get_formatted_unit_price(self) -> str:
        """Get unit price formatted with 5 decimals and comma"""
        return self.format_decimal(self.unit_price)

    def get_formatted_total_price(self) -> str:
        """Get total price formatted with 5 decimals and comma"""
        return self.format_decimal(self.total_price)

    def get_formatted_iva(self) -> str:
        """Get IVA percentage formatted with 5 decimals and comma"""
        return self.format_decimal(self.iva_percentage)

    def __repr__(self) -> str:
        return f"Product(name='{self.name}', quantity={self.quantity}, unit_price={self.unit_price})"
