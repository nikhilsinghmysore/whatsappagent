"""Initial schema setup

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create patients table
    op.create_table(
        'patients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('wa_id', sa.String(20), unique=True, nullable=False),
        sa.Column('name', sa.String(255)),
        sa.Column('age', sa.Integer()),
        sa.Column('language', sa.String(10), default='en', nullable=False),
        sa.Column('default_address', sa.Text()),
        sa.Column('pin', sa.String(10)),
        sa.Column('consent_opt_in_at', sa.DateTime()),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_patients_wa_id'), 'patients', ['wa_id'], unique=True)

    # Create providers table
    op.create_table(
        'providers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('wa_id', sa.String(20), unique=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('registration_no', sa.String(100), unique=True, nullable=False),
        sa.Column('verification_status', sa.String(20), default='pending', nullable=False),
        sa.Column('fee', sa.Numeric(10, 2)),
        sa.Column('service_area', sa.JSON()),
        sa.Column('is_online', sa.Boolean(), default=False, nullable=False),
        sa.Column('availability', sa.JSON()),
        sa.Column('rating_avg', sa.Numeric(3, 2), default=0, nullable=False),
        sa.Column('total_bookings', sa.Integer(), default=0, nullable=False),
        sa.Column('bio', sa.Text()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_providers_wa_id'), 'providers', ['wa_id'], unique=True)
    op.create_index(op.f('ix_providers_category'), 'providers', ['category'])
    op.create_index(op.f('ix_providers_verification_status'), 'providers', ['verification_status'])

    # Create services table
    op.create_table(
        'services',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('category', sa.String(50), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_services_name'), 'services', ['name'], unique=True)

    # Create bookings table
    op.create_table(
        'bookings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('patient_wa_id', sa.String(20), nullable=False),
        sa.Column('provider_id', sa.Integer()),
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), default='requested', nullable=False),
        sa.Column('symptoms', sa.Text()),
        sa.Column('address', sa.Text()),
        sa.Column('pin', sa.String(10)),
        sa.Column('scheduled_at', sa.DateTime()),
        sa.Column('provider_response_at', sa.DateTime()),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('meta_message_id', sa.String(100), unique=True),
        sa.Column('notes', sa.Text()),
        sa.ForeignKeyConstraint(['patient_wa_id'], ['patients.wa_id']),
        sa.ForeignKeyConstraint(['provider_id'], ['providers.id']),
        sa.ForeignKeyConstraint(['service_id'], ['services.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bookings_patient_wa_id'), 'bookings', ['patient_wa_id'])
    op.create_index(op.f('ix_bookings_provider_id'), 'bookings', ['provider_id'])
    op.create_index(op.f('ix_bookings_status'), 'bookings', ['status'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('wa_id', sa.String(20), nullable=False),
        sa.Column('direction', sa.String(10), nullable=False),
        sa.Column('message_type', sa.String(20), nullable=False),
        sa.Column('body', sa.Text()),
        sa.Column('meta_message_id', sa.String(100), unique=True),
        sa.Column('is_duplicate', sa.Boolean(), default=False, nullable=False),
        sa.Column('error', sa.Text()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_wa_id'), 'messages', ['wa_id'])

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('wa_id', sa.String(20), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('state', sa.String(50), default='awaiting_name', nullable=False),
        sa.Column('language', sa.String(10), default='en', nullable=False),
        sa.Column('current_booking_id', sa.Integer()),
        sa.Column('turn_count', sa.Integer(), default=0, nullable=False),
        sa.Column('escalated_to_human_at', sa.DateTime()),
        sa.Column('last_message_at', sa.DateTime()),
        sa.Column('is_escalated', sa.Boolean(), default=False, nullable=False),
        sa.Column('summary', sa.Text()),
        sa.Column('reminder_preference', sa.JSON()),
        sa.PrimaryKeyConstraint('wa_id')
    )
    op.create_index(op.f('ix_conversations_wa_id'), 'conversations', ['wa_id'], unique=True)

    # Create ratings table
    op.create_table(
        'ratings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('patient_wa_id', sa.String(20), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('feedback_text', sa.Text()),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id']),
        sa.ForeignKeyConstraint(['patient_wa_id'], ['patients.wa_id']),
        sa.ForeignKeyConstraint(['provider_id'], ['providers.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('booking_id')
    )

    # Create consents table
    op.create_table(
        'consents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('wa_id', sa.String(20), nullable=False),
        sa.Column('template_name', sa.String(100), nullable=False),
        sa.Column('opted_in', sa.Boolean(), default=True, nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_consents_wa_id'), 'consents', ['wa_id'])

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=False),
        sa.Column('document_type', sa.String(50), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('mime_type', sa.String(50), nullable=False),
        sa.Column('data', sa.LargeBinary(), nullable=False),
        sa.Column('verified', sa.String(20), default='pending', nullable=False),
        sa.ForeignKeyConstraint(['provider_id'], ['providers.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_provider_id'), 'documents', ['provider_id'])


def downgrade() -> None:
    op.drop_table('documents')
    op.drop_table('consents')
    op.drop_table('ratings')
    op.drop_table('conversations')
    op.drop_table('messages')
    op.drop_table('bookings')
    op.drop_table('services')
    op.drop_table('providers')
    op.drop_table('patients')
