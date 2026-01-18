"""Initial schema

Revision ID: 20260118_1305
Revises: 
Create Date: 2025-01-18 13:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision = '20260118_1305'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_type', sa.Enum('pdf', 'docx', 'txt', name='documentfiletype'), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('file_size', sa.String(50), nullable=True),
        sa.Column('status', sa.Enum('uploading', 'processing', 'indexed', 'failed', name='documentstatus'), default='uploading', nullable=False),
        sa.Column('meta', sa.JSON(), nullable=True),
        sa.Column('vectorized', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_documents_file_type', 'documents', ['file_type'])
    op.create_index('ix_documents_status', 'documents', ['status'])
    op.create_index('ix_documents_vectorized', 'documents', ['vectorized'])
    
    # Create contracts table
    op.create_table(
        'contracts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('contract_type', sa.Enum('sales', 'purchase', 'service', 'nda', 'employment', 'other', name='contracttype'), nullable=False),
        sa.Column('parties', sa.JSON(), nullable=False),
        sa.Column('amount', sa.Numeric(20, 2), nullable=True),
        sa.Column('currency', sa.String(3), default='CNY'),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('status', sa.Enum('draft', 'active', 'expired', 'terminated', name='contractstatus'), default='draft', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_contracts_contract_type', 'contracts', ['contract_type'])
    op.create_index('ix_contracts_status', 'contracts', ['status'])
    op.create_index('ix_contracts_document_id', 'contracts', ['document_id'])
    
    # Create analysis_results table
    op.create_table(
        'analysis_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('contract_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('contracts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tasks.id', ondelete='SET NULL'), nullable=True),
        sa.Column('analysis_data', sa.JSON(), nullable=True),
        sa.Column('review_data', sa.JSON(), nullable=True),
        sa.Column('validation_data', sa.JSON(), nullable=True),
        sa.Column('report_markdown', sa.Text(), nullable=True),
        sa.Column('risk_score', sa.Integer(), nullable=True),
        sa.Column('risk_level', sa.Enum('low', 'medium', 'high', name='risklevel'), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'in_progress', 'completed', 'failed', name='analysisstatus'), default='pending', nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_analysis_results_risk_level', 'analysis_results', ['risk_level'])
    op.create_index('ix_analysis_results_status', 'analysis_results', ['status'])
    op.create_index('ix_analysis_results_contract_id', 'analysis_results', ['contract_id'])
    
    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('task_type', sa.Enum('document_upload', 'contract_analysis', 'rag_search', 'report_generation', name='tasktype'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'running', 'completed', 'failed', 'cancelled', name='taskstatus'), default='pending', nullable=False),
        sa.Column('progress', sa.Integer(), default=0, nullable=False),
        sa.Column('current_stage', sa.String(100), nullable=True),
        sa.Column('input_data', sa.JSON(), nullable=True),
        sa.Column('output_data', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_tasks_task_type', 'tasks', ['task_type'])
    op.create_index('ix_tasks_status', 'tasks', ['status'])
    
    # Create knowledge_chunks table
    op.create_table(
        'knowledge_chunks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('embedding', postgresql.Vector(1024), nullable=True),
        sa.Column('meta', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_knowledge_chunks_document_id', 'knowledge_chunks', ['document_id'])


def downgrade() -> None:
    op.drop_table('knowledge_chunks')
    op.drop_table('tasks')
    op.drop_table('analysis_results')
    op.drop_table('contracts')
    op.drop_table('documents')
    op.execute('DROP EXTENSION IF EXISTS vector')
