"""auto_generated

Revision ID: fdd959a2cfda
Revises: 
Create Date: 2025-06-01 02:19:26.646342

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import Text

# revision identifiers, used by Alembic.
revision: str = 'fdd959a2cfda'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def create_tab_addresses():
    op.create_table('addresses',
                    sa.Column('user_id', sa.String(length=36), nullable=False),
                    sa.Column('street_number', sa.String(length=10), nullable=False),
                    sa.Column('street_name', sa.String(length=40), nullable=False),
                    sa.Column('neighborhood', sa.String(length=20), nullable=False),
                    sa.Column('locality', sa.String(length=20), nullable=False),
                    sa.Column('lga', sa.String(length=36), nullable=False),
                    sa.Column('state', sa.String(length=36), nullable=False),
                    sa.Column('country_id', sa.String(length=36), nullable=False),
                    sa.Column('gps_location', sa.JSON(), nullable=False),
                    sa.Column('verified', sa.Boolean(), nullable=False),
                    sa.Column('id', sa.String(length=36), nullable=False),
                    sa.Column('date_created', sa.TIMESTAMP(timezone=True), nullable=False),
                    sa.Column('created_by', sa.String(length=36), nullable=True),
                    sa.Column('date_updated', sa.TIMESTAMP(timezone=True), nullable=True),
                    sa.Column('updated_by', sa.String(length=36), nullable=True),
                    sa.Column('deleted', sa.Boolean(), nullable=False),
                    sa.Column('date_deleted', sa.TIMESTAMP(timezone=True), nullable=True),
                    sa.Column('deleted_by', sa.String(length=36), nullable=True),
                    sa.Column('version', sa.Integer(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_addresses_deleted'), 'addresses', ['deleted'], unique=False)
    op.create_index(op.f('ix_addresses_id'), 'addresses', ['id'], unique=True)
    op.create_index(op.f('ix_addresses_user_id'), 'addresses', ['user_id'], unique=False)
def drop_tab_addresses():
    op.drop_index(op.f('ix_addresses_user_id'), table_name='addresses')
    op.drop_index(op.f('ix_addresses_id'), table_name='addresses')
    op.drop_index(op.f('ix_addresses_deleted'), table_name='addresses')
    op.drop_table('addresses')

def create_tab_key_values():
    op.create_table('key_values',
                    sa.Column('key', sa.String(length=128), nullable=False),
                    sa.Column('value', sa.LargeBinary(), nullable=False),
                    sa.Column('expires_at', sa.DateTime(), nullable=False),
                    sa.PrimaryKeyConstraint('key')
                    )
    op.create_index(op.f('ix_key_values_key'), 'key_values', ['key'], unique=True)
def drop_tab_key_values():
    op.drop_index(op.f('ix_key_values_key'), table_name='key_values')
    op.drop_table('key_values')


def create_tab_users():
    op.create_table('users',
                    sa.Column('email', sa.String(length=60), nullable=False),
                    sa.Column('phone', sa.String(length=25), nullable=True),
                    sa.Column('phone_ext', sa.String(length=6), nullable=True),
                    sa.Column('password', sa.String(length=512), nullable=True),
                    sa.Column('password_last_updated', sa.DateTime(), nullable=True),
                    sa.Column('firstname', sa.String(length=30), nullable=False),
                    sa.Column('middle_name', sa.String(length=30), nullable=True),
                    sa.Column('lastname', sa.String(length=30), nullable=False),
                    sa.Column('user_type', sa.String(length=2), nullable=False),
                    sa.Column('status', sa.String(length=12), nullable=False),
                    sa.Column('dob', sa.Date(), nullable=True),
                    sa.Column('gender', sa.String(length=2), nullable=True),
                    sa.Column('last_active_date', sa.DateTime(), nullable=True),
                    sa.Column('notes', sa.Text(), nullable=True),
                    sa.Column('profile_picture_doc_id', sa.String(length=36), nullable=True),
                    sa.Column('selfie_picture_doc_id', sa.String(length=36), nullable=True),
                    sa.Column('bvn', sa.String(length=40), nullable=True),
                    sa.Column('bvn_validated', sa.Boolean(), nullable=False),
                    sa.Column('phone_validated', sa.Boolean(), nullable=False),
                    sa.Column('email_validated', sa.Boolean(), nullable=False),
                    sa.Column('identity_validated', sa.Boolean(), nullable=False),
                    sa.Column('address_id', sa.String(length=36), nullable=True),
                    sa.Column('address_validated', sa.Boolean(), nullable=False),
                    sa.Column('selfie_validated', sa.Boolean(), nullable=False),
                    sa.Column('id', sa.String(length=36), nullable=False),
                    sa.Column('date_created', sa.TIMESTAMP(timezone=True), nullable=False),
                    sa.Column('created_by', sa.String(length=36), nullable=True),
                    sa.Column('date_updated', sa.TIMESTAMP(timezone=True), nullable=True),
                    sa.Column('updated_by', sa.String(length=36), nullable=True),
                    sa.Column('deleted', sa.Boolean(), nullable=False),
                    sa.Column('date_deleted', sa.TIMESTAMP(timezone=True), nullable=True),
                    sa.Column('deleted_by', sa.String(length=36), nullable=True),
                    sa.Column('version', sa.Integer(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_users_deleted'), 'users', ['deleted'], unique=False)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=True)
def drop_tab_users():
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_deleted'), table_name='users')
    op.drop_table('users')

def create_tab_devices():
    op.create_table('devices',
                    sa.Column('user_id', sa.String(length=36), nullable=False),
                    sa.Column('device_id', sa.String(length=36), nullable=False),
                    sa.Column('push_provider_type', sa.String(length=20), nullable=False),
                    sa.Column('push_token', sa.JSON(), nullable=False),
                    sa.Column('last_active', sa.DateTime(), nullable=False),
                    sa.Column('id', sa.String(length=36), nullable=False),
                    sa.Column('date_created', sa.TIMESTAMP(timezone=True), nullable=False),
                    sa.Column('created_by', sa.String(length=36), nullable=True),
                    sa.Column('date_updated', sa.TIMESTAMP(timezone=True), nullable=True),
                    sa.Column('updated_by', sa.String(length=36), nullable=True),
                    sa.Column('deleted', sa.Boolean(), nullable=False),
                    sa.Column('date_deleted', sa.TIMESTAMP(timezone=True), nullable=True),
                    sa.Column('deleted_by', sa.String(length=36), nullable=True),
                    sa.Column('version', sa.Integer(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_devices_deleted'), 'devices', ['deleted'], unique=False)
    op.create_index(op.f('ix_devices_id'), 'devices', ['id'], unique=True)
def drop_tab_devices():
    op.drop_index(op.f('ix_devices_id'), table_name='devices')
    op.drop_index(op.f('ix_devices_deleted'), table_name='devices')
    op.drop_table('devices')

def upgrade() -> None:
    create_tab_addresses()
    create_tab_key_values()
    create_tab_users()
    create_tab_devices()


def downgrade() -> None:
    drop_tab_addresses()
    drop_tab_key_values()
    drop_tab_users()
    drop_tab_devices()
