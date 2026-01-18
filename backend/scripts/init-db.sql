-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create additional schemas if needed
CREATE SCHEMA IF NOT EXISTS legal;
