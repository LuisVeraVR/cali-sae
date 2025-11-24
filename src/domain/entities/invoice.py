"""
Invoice entity - Represents an electronic invoice
"""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from .product import Product


@dataclass
class Invoice:
    """Electronic invoice entity following UBL 2.0 DIAN Colombia standard"""

    # Invoice identification
    invoice_number: str
    issue_date: datetime
    due_date: Optional[datetime]
    currency: str  # COP, USD, EUR, etc.

    # Seller information
    seller_nit: str
    seller_name: str
    seller_municipality: str

    # Buyer information
    buyer_nit: str
    buyer_name: str

    # Products
    products: List[Product] = field(default_factory=list)

    # Optional fields
    xml_filename: Optional[str] = None
    zip_filename: Optional[str] = None

    # Metadata
    processed_at: Optional[datetime] = None

    def add_product(self, product: Product) -> None:
        """Add a product to the invoice"""
        product.line_number = len(self.products) + 1
        self.products.append(product)

    def get_total_amount(self) -> Decimal:
        """Calculate total amount of the invoice"""
        return sum(product.total_price for product in self.products)

    def get_total_iva(self) -> Decimal:
        """Calculate total IVA of the invoice"""
        return sum(
            product.total_price * product.iva_percentage / Decimal(100)
            for product in self.products
        )

    def get_product_count(self) -> int:
        """Get the number of products in the invoice"""
        return len(self.products)

    def format_currency_code(self) -> str:
        """Format currency code to numeric representation"""
        currency_map = {
            'COP': '1',
            'USD': '2',
            'EUR': '3'
        }
        return currency_map.get(self.currency.upper(), '1')

    def format_date(self, date: Optional[datetime], format_str: str = "%Y-%m-%d") -> str:
        """Format date to string"""
        if date is None:
            return ""
        return date.strftime(format_str)

    def get_issue_date_formatted(self) -> str:
        """Get issue date formatted as YYYY-MM-DD"""
        return self.format_date(self.issue_date)

    def get_due_date_formatted(self) -> str:
        """Get due date formatted as YYYY-MM-DD"""
        return self.format_date(self.due_date)

    def __repr__(self) -> str:
        return (
            f"Invoice(number='{self.invoice_number}', "
            f"seller='{self.seller_name}', "
            f"products={len(self.products)})"
        )
