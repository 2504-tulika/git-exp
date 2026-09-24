from sqlalchemy import Column, String, Date, Text, Boolean, ForeignKey, Integer, ForeignKeyConstraint
from sqlalchemy.orm import relationship

from src.config.database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    dob = Column(Date, nullable=False)
    gender = Column(String(10))
    contact_number = Column(String(20))

    # One customer can be linked to many policies (via policy_customers).
    policies = relationship("PolicyCustomer", back_populates="customer")


class Policy(Base):
    __tablename__ = "policies"

    policy_id = Column(String(20), primary_key=True)
    policy_type = Column(String(20), nullable=False)      # Motor / Medical / Life
    sub_type = Column(String(100), nullable=False)         # e.g. "Comprehensive Motor Policy"
    status = Column(String(20), nullable=False)             # Active / Lapsed
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    premium = Column(String(50))            # kept as text, e.g. "Rs. 13,200 per annum"
    policy_document = Column(String(200))    # relative path to the policy PDF

    # One policy can be linked to many customers (via policy_customers).
    customers = relationship("PolicyCustomer", back_populates="policy")


class PolicyCustomer(Base):
    """
    The many-to-many link table: which customer(s) are covered under which
    policy. A row here means "this customer is an independent policyholder
    on this policy" -- not that multiple customers on one row are related
    to each other in any way.
    """
    __tablename__ = "policy_customers"

    policy_id = Column(String(20), ForeignKey("policies.policy_id"), primary_key=True)
    customer_id = Column(String(20), ForeignKey("customers.customer_id"), primary_key=True)

    policy = relationship("Policy", back_populates="customers")
    customer = relationship("Customer", back_populates="policies")


class ClaimsHistory(Base):
    __tablename__ = "claims_history"

    claim_id = Column(String(20), primary_key=True)
    
    policy_id = Column(String(20), nullable=False)
    customer_id = Column(String(20), nullable=False)
    claim_type = Column(String(100), nullable=False)
    incident_date = Column(Date, nullable=False)
    incident_description = Column(Text)
    intimation_date = Column(Date, nullable=False)
    claim_amount = Column(String(50))        # kept as text, e.g. "Rs. 45,000"
    status = Column(String(20), nullable=False)   # Approved / Denied / Under Review / Pending
    fraud_flag = Column(Boolean, default=False)

    """A claim always belongs to exactly one specific (policy_id, customer_id)
    pair -- and that pair must actually exist in policy_customers. This
    stops a claim ever being recorded against a customer who doesn't
    actually hold that policy"""
    __table_args__ = (
        ForeignKeyConstraint(
            ["policy_id", "customer_id"],
            ["policy_customers.policy_id", "policy_customers.customer_id"],
        ),
    )


class User(Base):
    """Login accounts for claims handlers and supervisors (Day 6 role-based access)."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="claims_handler")  # or "supervisor"

