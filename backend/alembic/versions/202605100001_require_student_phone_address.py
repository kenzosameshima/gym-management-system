"""require student phone and address

Revision ID: 202605100001
Revises: 202605080005
Create Date: 2026-05-10 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "202605100001"
down_revision: str | None = "202605080005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("UPDATE students SET phone = 'Not informed' WHERE phone IS NULL OR phone = ''")
    op.execute(
        "UPDATE students SET address = 'Not informed' WHERE address IS NULL OR address = ''",
    )
    op.alter_column("students", "phone", existing_type=sa.String(length=32), nullable=False)
    op.alter_column("students", "address", existing_type=sa.Text(), nullable=False)


def downgrade() -> None:
    op.alter_column("students", "address", existing_type=sa.Text(), nullable=True)
    op.alter_column("students", "phone", existing_type=sa.String(length=32), nullable=True)
