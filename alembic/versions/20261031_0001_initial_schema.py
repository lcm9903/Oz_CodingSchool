"""initial schema: users, patients, medical_records, predictions

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-31 00:00:00
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

department_enum = sa.Enum("developer", "medical team", "researcher", name="department")
gender_enum = sa.Enum("male", "female", name="gender")
patient_gender_enum = sa.Enum("male", "female", name="patient_gender")
role_enum = sa.Enum("pending", "staff", "admin", name="user_role")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("department", department_enum, nullable=False),
        sa.Column("gender", gender_enum, nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=False),
        sa.Column("role", role_enum, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_name", "users", ["name"], unique=False)

    op.create_table(
        "patients",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("gender", patient_gender_enum, nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_patients_name", "patients", ["name"], unique=False)

    op.create_table(
        "medical_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("chart_number", sa.String(length=50), nullable=False),
        sa.Column("symptoms", sa.Text(), nullable=False),
        sa.Column("xray_image_path", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_medical_records_patient_id", "medical_records", ["patient_id"], unique=False
    )

    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("medical_record_id", sa.Integer(), nullable=False),
        sa.Column("is_pneumonia", sa.Boolean(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("heatmap_image_url", sa.String(length=255), nullable=True),
        sa.Column("ai_model", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["medical_record_id"], ["medical_records.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("medical_record_id", "ai_model", name="uq_record_model"),
    )
    op.create_index(
        "ix_predictions_medical_record_id",
        "predictions",
        ["medical_record_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_predictions_medical_record_id", table_name="predictions")
    op.drop_table("predictions")
    op.drop_index("ix_medical_records_patient_id", table_name="medical_records")
    op.drop_table("medical_records")
    op.drop_index("ix_patients_name", table_name="patients")
    op.drop_table("patients")
    op.drop_index("ix_users_name", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
