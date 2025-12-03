"""
Product entity - Represents a product line in an invoice
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class Product:
    """Product line item in an invoice"""

    # Datos principales
    name: str
    underlying_code: str
    unit_of_measure: str        # En JCR siempre la estamos dejando en "Kg"
    quantity: Decimal           # Cantidad CONVERTIDA (kilos)
    unit_price: Decimal
    total_price: Decimal
    iva_percentage: Decimal

    # NUEVO: cantidad original tal como viene en el archivo del cliente
    original_quantity: Optional[Decimal] = None

    # NUEVO: unidad de medida original (UND, P25, CJ, etc.) tal como viene en el XML/archivo
    original_unit_code: Optional[str] = None

    # Meta
    line_number: Optional[int] = None

    def format_decimal(self, value: Decimal, decimals: int = 5) -> str:
        """Format decimal with comma as decimal separator"""
        formatted = f"{value:.{decimals}f}"
        return formatted.replace('.', ',')

    def get_formatted_quantity(self) -> str:
        """Get converted quantity formatted with 5 decimals and comma"""
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

    def get_formatted_original_quantity(self) -> str:
        """
        Get original quantity (from client file) formatted with 5 decimals and comma.
        Si por alguna razón no se llenó, usa la quantity convertida como fallback.
        """
        value = self.original_quantity if self.original_quantity is not None else self.quantity
        return self.format_decimal(value)

    def get_original_unit_code(self) -> str:
        """
        Get original unit code (UND, P25, CJ, etc.) from the source file.
        Returns empty string if not available.
        """
        return self.original_unit_code if self.original_unit_code else ""

    def __repr__(self) -> str:
        return (
            f"Product(name='{self.name}', "
            f"quantity={self.quantity}, "
            f"unit_price={self.unit_price}, "
            f"original_quantity={self.original_quantity})"
        )
