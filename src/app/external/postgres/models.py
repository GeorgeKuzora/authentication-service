from datetime import datetime
from typing import List

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

username_max_len = 200
hash_max_len = 1000


class Base(DeclarativeBase):
    """Базовый класс для создания ORM моделей."""


class User(Base):
    """Пользователь."""

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(username_max_len), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(hash_max_len))
    balance: Mapped[int] = mapped_column(default=0)
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_deleted: Mapped[bool] = mapped_column(default=False)
    transactions: Mapped[List['Transaction']] = relationship(
        back_populates='user',
    )
    reports: Mapped[List['Report']] = relationship(back_populates='user')
    vector: Mapped[bytes] = mapped_column(nullable=True)


class Transaction(Base):
    """Транзакция."""

    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_type: Mapped[bool]
    amount: Mapped[int]
    created_at: Mapped[datetime]
    is_deleted: Mapped[bool] = mapped_column(default=False)
    id_user: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='transactions')


class Report(Base):
    """Отчет."""

    __tablename__ = 'reports'

    id: Mapped[int] = mapped_column(primary_key=True)
    start_date: Mapped[datetime]
    end_date: Mapped[datetime]
    is_deleted: Mapped[bool] = mapped_column(default=False)
    id_user: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='reports')
    transactions = relationship(
        'Transaction',
        secondary=Table(
            'report_transaction',
            Base.metadata,
            Column('id', Integer, primary_key=True),
            Column('id_transaction', Integer, ForeignKey('transactions.id')),
            Column('id_report', Integer, ForeignKey('reports.id')),
        ),
        backref='reports',
    )
