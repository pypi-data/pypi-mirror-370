import datetime as dt
import uuid
from functools import partial
from typing import Annotated

from sqlalchemy import JSON, CheckConstraint, ForeignKey, MetaData, String, UniqueConstraint, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from billing_shared.types import OrderStatus, PaymentMethodName, PaymentProviderName, PaymentStatus, RefundStatus

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


class ValueEnum(SAEnum):
    def __init__(self, enum_class, **kwargs):
        super().__init__(enum_class, values_callable=lambda x: [e.value for e in x], **kwargs)


class Base(DeclarativeBase):
    metadata = metadata

    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True, unique=True, nullable=False)
    created_at = Annotated[dt.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
    updated_at = Annotated[
        dt.datetime,
        mapped_column(
            server_default=text("TIMEZONE('utc', now())"), onupdate=partial(dt.datetime.now, dt.timezone.utc)
        ),
    ]


class Order(Base):
    __tablename__ = "orders"

    # TODO for MVP not necessary to create relation to product like subscription or one-time purchase via unique pairs of id and type columns
    title: Mapped[str] = mapped_column(String(512))
    status: Mapped[OrderStatus] = mapped_column(ValueEnum(OrderStatus), default=OrderStatus.NEW)
    user_id: Mapped[uuid.UUID] = mapped_column(index=True)  # fk-like, users stored in separate db


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    user_id: Mapped[uuid.UUID] = mapped_column(index=True)  # fk-like, users stored in separate db
    name: Mapped[PaymentMethodName] = mapped_column(ValueEnum(PaymentMethodName))
    provider_name: Mapped[PaymentProviderName] = mapped_column(ValueEnum(PaymentProviderName))
    id_at_provider: Mapped[str | None] = mapped_column(index=True)
    details: Mapped[dict | None] = mapped_column(JSON)
    active: Mapped[bool] = mapped_column(default=True)

    __table_args__ = (
        UniqueConstraint("user_id", "name", "provider_name", name="uq_payment_methods_user_id_name_provider"),
    )


class Payment(Base):
    __tablename__ = "payments"

    currency: Mapped[str] = mapped_column(default="RUB")
    amount: Mapped[float]
    status: Mapped[PaymentStatus] = mapped_column(ValueEnum(PaymentStatus), default=PaymentStatus.CREATED)
    provider_name: Mapped[PaymentProviderName] = mapped_column(ValueEnum(PaymentProviderName))
    user_id: Mapped[uuid.UUID] = mapped_column(index=True)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"))
    external_id: Mapped[str | None]
    is_refundable: Mapped[bool | None]
    result_data: Mapped[dict | None] = mapped_column(JSON)

    payment_method_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("payment_methods.id"))
    payment_method: Mapped[PaymentMethod] = relationship()

    __table_args__ = (CheckConstraint("amount > 0", name="amount_positive"),)


class Refund(Base):
    __tablename__ = "refunds"

    status: Mapped[RefundStatus] = mapped_column(ValueEnum(RefundStatus), default=RefundStatus.CREATED)
    provider_name: Mapped[PaymentProviderName] = mapped_column(ValueEnum(PaymentProviderName))
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"), index=True)
    payment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("payments.id"), index=True)
    external_id: Mapped[str | None] = mapped_column(index=True)
    result_data: Mapped[dict | None] = mapped_column(JSON)
