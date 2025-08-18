import enum
from decimal import Decimal

from pydantic import Field, ConfigDict

from appodus_utils import Object


class TransactionCurrency(str, enum.Enum):
    USD = 'USD'
    EUR = 'EUR'
    GBP = 'GBP'
    NGN = 'NGN'


class Money(Object):
    value: Decimal = Field(0.0)
    currency: TransactionCurrency = Field(None)

    def get_value(self) -> Decimal:
        return self.value

    def get_currency(self) -> TransactionCurrency:
        return self.currency

    def plus(self, money: 'Money') -> 'Money':
        self._validate_currency(money.get_currency())
        self._validate_negative_credit(money.get_value())
        self.value += money.get_value()

        return self

    def minus(self, money: 'Money') -> 'Money':
        self._validate_debit_balance(money.get_value())
        self._validate_currency(money.get_currency())
        self._validate_negative_debit(money.get_value())
        self.value -= money.get_value()

        return self

    def compare(self, other: 'Money') -> Decimal:
        """
        Compare self to other.  Return a decimal value:

            a or b is a NaN ==> Decimal('NaN')
            a < b           ==> Decimal('-1')
            a == b          ==> Decimal('0')
            a > b           ==> Decimal('1')

        :param other:
        :return:
        """
        self._validate_currency(other.get_currency())
        return self.value.compare(other.get_value())

    def is_less_than(self, other: 'Money') -> bool:
        return self.value.compare(other.get_value()) < 0

    def is_greater_than(self, other: 'Money') -> bool:
        return self.value.compare(other.get_value()) > 0

    def is_equal_to(self, other: 'Money') -> bool:
        return self.value.compare(other.get_value()) == 0

    def _validate_currency(self, currency: TransactionCurrency):
        if self.currency != currency:
            raise ValueError("Money exception: currency mismatch")

    @staticmethod
    def _validate_negative_credit(amount: Decimal):
        if amount.compare(Decimal(0)) == Decimal(-1):
            raise ValueError("Money exception: negative credit amount")

    @staticmethod
    def _validate_negative_debit(amount: Decimal):
        if amount.compare(Decimal(0)) == Decimal(-1):
            raise ValueError("Money exception: negative debit amount")

    def _validate_debit_balance(self, amount: Decimal):
        if self.value.compare(Decimal(0)) == Decimal(-1) or self.value.compare(amount) == Decimal(-1):
            raise ValueError("Money exception: insufficient balance")

    model_config = ConfigDict(
        # strict=True,
        populate_by_name=True,  # allows using the alias when parsing
        # extra="forbid"          # disallow any extra fields not defined here
    )
