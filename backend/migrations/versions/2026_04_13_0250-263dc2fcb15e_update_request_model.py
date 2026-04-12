"""update request model

Revision ID: 263dc2fcb15e
Revises: 0cef71ab930a
Create Date: 2026-04-13 02:50:33.575131
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "263dc2fcb15e"
down_revision: Union[str, Sequence[str], None] = "0cef71ab930a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("requests") as batch_op:
        batch_op.alter_column("executor_id", existing_type=sa.INTEGER(), nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("requests") as batch_op:
        batch_op.alter_column("executor_id", existing_type=sa.INTEGER(), nullable=False)
