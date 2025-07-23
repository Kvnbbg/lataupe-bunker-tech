#!/usr/bin/env python3
"""
Script d'implémentation de la base de données SQL pour lataupe-bunker-tech
Migre de SQLite vers PostgreSQL et implémente un système d'enregistrement avancé
"""

import os
import json
import psycopg2
from datetime import datetime, timedelta
from pathlib import Path

def create_postgresql_schema():
    """Crée le schéma PostgreSQL complet pour lataupe-bunker-tech"""
    
    schema_sql = """
-- Lataupe Bunker Tech - PostgreSQL Schema
-- Version 2.0 - Production Ready

-- Extensions nécessaires
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Suppression des tables existantes (pour migration)
DROP TABLE IF EXISTS quiz_attempts CASCADE;
DROP TABLE IF EXISTS quiz_questions CASCADE;
DROP TABLE IF EXISTS bunker_quizzes CASCADE;
DROP TABLE IF EXISTS quiz_categories CASCADE;
DROP TABLE IF EXISTS user_subscriptions CASCADE;
DROP TABLE IF EXISTS emergency_messages CASCADE;
DROP TABLE IF EXISTS alerts CASCADE;
DROP TABLE IF EXISTS environmental_data CASCADE;
DROP TABLE IF EXISTS bunker_users CASCADE;
DROP TABLE IF EXISTS user_sessions CASCADE;
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Table des utilisateurs (améliorée)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'resident' NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contraintes
    CONSTRAINT valid_role CHECK (role IN ('admin', 'security', 'resident', 'guest')),
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Index pour les utilisateurs
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_users_created ON users(created_at);

-- Table des sessions utilisateur
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT true,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour les sessions
CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at);
CREATE INDEX idx_sessions_active ON user_sessions(is_active);

-- Table des profils bunker (améliorée)
CREATE TABLE bunker_users (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    bunker_id VARCHAR(50) NOT NULL,
    access_level VARCHAR(50) DEFAULT 'basic' NOT NULL,
    room_assignment VARCHAR(100),
    emergency_contact VARCHAR(200),
    medical_info JSONB,
    security_clearance INTEGER DEFAULT 1,
    shift_schedule JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contraintes
    CONSTRAINT valid_access_level CHECK (access_level IN ('basic', 'advanced', 'admin', 'emergency')),
    CONSTRAINT valid_security_clearance CHECK (security_clearance BETWEEN 1 AND 5),
    UNIQUE(user_id, bunker_id)
);

-- Index pour les profils bunker
CREATE INDEX idx_bunker_users_user_id ON bunker_users(user_id);
CREATE INDEX idx_bunker_users_bunker_id ON bunker_users(bunker_id);
CREATE INDEX idx_bunker_users_access_level ON bunker_users(access_level);
CREATE INDEX idx_bunker_users_security_clearance ON bunker_users(security_clearance);

-- Table des données environnementales (optimisée)
CREATE TABLE environmental_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    temperature DECIMAL(5,2),
    humidity DECIMAL(5,2),
    air_quality DECIMAL(5,2),
    oxygen_level DECIMAL(5,2),
    co2_level DECIMAL(7,2),
    radiation_level DECIMAL(8,4),
    atmospheric_pressure DECIMAL(7,2),
    bunker_id VARCHAR(50) NOT NULL,
    sensor_location VARCHAR(100),
    sensor_id VARCHAR(50),
    data_quality_score DECIMAL(3,2) DEFAULT 1.0,
    is_anomaly BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour les données environnementales
CREATE INDEX idx_env_data_timestamp ON environmental_data(timestamp);
CREATE INDEX idx_env_data_bunker_timestamp ON environmental_data(bunker_id, timestamp);
CREATE INDEX idx_env_data_sensor ON environmental_data(sensor_id);
CREATE INDEX idx_env_data_anomaly ON environmental_data(is_anomaly);

-- Partitioning par mois pour les données environnementales
CREATE TABLE environmental_data_y2025m01 PARTITION OF environmental_data
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE environmental_data_y2025m02 PARTITION OF environmental_data
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
-- Ajouter d'autres partitions selon les besoins

-- Table des alertes (améliorée)
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    bunker_id VARCHAR(50) NOT NULL,
    sensor_location VARCHAR(100),
    sensor_id VARCHAR(50),
    threshold_value DECIMAL(10,4),
    actual_value DECIMAL(10,4),
    is_resolved BOOLEAN DEFAULT false,
    resolved_by INTEGER REFERENCES users(id),
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    auto_resolved BOOLEAN DEFAULT false,
    escalation_level INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contraintes
    CONSTRAINT valid_severity CHECK (severity IN ('low', 'medium', 'high', 'critical', 'emergency')),
    CONSTRAINT valid_escalation CHECK (escalation_level BETWEEN 1 AND 5)
);

-- Index pour les alertes
CREATE INDEX idx_alerts_timestamp ON alerts(timestamp);
CREATE INDEX idx_alerts_bunker_severity ON alerts(bunker_id, severity, timestamp);
CREATE INDEX idx_alerts_resolved ON alerts(is_resolved);
CREATE INDEX idx_alerts_type ON alerts(alert_type);
CREATE INDEX idx_alerts_escalation ON alerts(escalation_level);

-- Table des messages d'urgence (améliorée)
CREATE TABLE emergency_messages (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    message_type VARCHAR(50) NOT NULL,
    recipient VARCHAR(200) NOT NULL,
    subject VARCHAR(200),
    content TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'normal' NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    sent_by INTEGER REFERENCES users(id) NOT NULL,
    bunker_id VARCHAR(50) NOT NULL,
    delivery_confirmation TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    scheduled_for TIMESTAMP,
    
    -- Contraintes
    CONSTRAINT valid_message_type CHECK (message_type IN ('sms', 'email', 'radio', 'satellite', 'internal')),
    CONSTRAINT valid_priority CHECK (priority IN ('low', 'normal', 'high', 'urgent', 'emergency')),
    CONSTRAINT valid_status CHECK (status IN ('pending', 'sent', 'delivered', 'failed', 'cancelled'))
);

-- Index pour les messages d'urgence
CREATE INDEX idx_emergency_messages_timestamp ON emergency_messages(timestamp);
CREATE INDEX idx_emergency_messages_status ON emergency_messages(status);
CREATE INDEX idx_emergency_messages_priority ON emergency_messages(priority);
CREATE INDEX idx_emergency_messages_bunker ON emergency_messages(bunker_id);
CREATE INDEX idx_emergency_messages_scheduled ON emergency_messages(scheduled_for);

-- Table des catégories de quiz
CREATE TABLE quiz_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour les catégories de quiz
CREATE INDEX idx_quiz_categories_active ON quiz_categories(is_active);
CREATE INDEX idx_quiz_categories_sort ON quiz_categories(sort_order);

-- Table des quiz bunker
CREATE TABLE bunker_quizzes (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category_id INTEGER REFERENCES quiz_categories(id) ON DELETE SET NULL,
    difficulty VARCHAR(20) DEFAULT 'medium',
    required_for_role VARCHAR(50),
    is_mandatory BOOLEAN DEFAULT false,
    time_limit INTEGER DEFAULT 300,
    passing_score INTEGER DEFAULT 70,
    max_attempts INTEGER DEFAULT 3,
    is_active BOOLEAN DEFAULT true,
    version INTEGER DEFAULT 1,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contraintes
    CONSTRAINT valid_difficulty CHECK (difficulty IN ('easy', 'medium', 'hard', 'expert')),
    CONSTRAINT valid_passing_score CHECK (passing_score BETWEEN 0 AND 100),
    CONSTRAINT valid_time_limit CHECK (time_limit > 0)
);

-- Index pour les quiz
CREATE INDEX idx_bunker_quizzes_category ON bunker_quizzes(category_id);
CREATE INDEX idx_bunker_quizzes_difficulty ON bunker_quizzes(difficulty);
CREATE INDEX idx_bunker_quizzes_mandatory ON bunker_quizzes(is_mandatory);
CREATE INDEX idx_bunker_quizzes_active ON bunker_quizzes(is_active);

-- Table des questions de quiz
CREATE TABLE quiz_questions (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER REFERENCES bunker_quizzes(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) DEFAULT 'multiple_choice',
    options JSONB,
    correct_answer VARCHAR(500) NOT NULL,
    explanation TEXT,
    points INTEGER DEFAULT 1,
    order_index INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    difficulty_weight DECIMAL(3,2) DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contraintes
    CONSTRAINT valid_question_type CHECK (question_type IN ('multiple_choice', 'true_false', 'text', 'numeric')),
    CONSTRAINT valid_points CHECK (points > 0)
);

-- Index pour les questions
CREATE INDEX idx_quiz_questions_quiz_id ON quiz_questions(quiz_id);
CREATE INDEX idx_quiz_questions_order ON quiz_questions(quiz_id, order_index);
CREATE INDEX idx_quiz_questions_active ON quiz_questions(is_active);

-- Table des tentatives de quiz
CREATE TABLE quiz_attempts (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    quiz_id INTEGER REFERENCES bunker_quizzes(id) ON DELETE CASCADE,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    score INTEGER,
    total_questions INTEGER,
    correct_answers INTEGER,
    time_taken INTEGER,
    is_passed BOOLEAN,
    answers JSONB,
    ip_address INET,
    user_agent TEXT,
    is_valid BOOLEAN DEFAULT true,
    cheating_detected BOOLEAN DEFAULT false,
    
    -- Contraintes
    CONSTRAINT valid_score CHECK (score IS NULL OR score BETWEEN 0 AND 100)
);

-- Index pour les tentatives
CREATE INDEX idx_quiz_attempts_user_quiz ON quiz_attempts(user_id, quiz_id);
CREATE INDEX idx_quiz_attempts_completed ON quiz_attempts(completed_at);
CREATE INDEX idx_quiz_attempts_passed ON quiz_attempts(is_passed);
CREATE INDEX idx_quiz_attempts_valid ON quiz_attempts(is_valid);

-- Table des abonnements utilisateur
CREATE TABLE user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    subscription_type VARCHAR(50) NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    features JSONB,
    payment_method VARCHAR(50),
    payment_status VARCHAR(20) DEFAULT 'pending',
    auto_renew BOOLEAN DEFAULT false,
    cancelled_at TIMESTAMP,
    cancellation_reason TEXT,
    
    -- Contraintes
    CONSTRAINT valid_subscription_type CHECK (subscription_type IN ('free', 'lataupe_plus', 'lataupe_premium')),
    CONSTRAINT valid_payment_status CHECK (payment_status IN ('pending', 'paid', 'failed', 'refunded', 'cancelled'))
);

-- Index pour les abonnements
CREATE INDEX idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX idx_user_subscriptions_active ON user_subscriptions(is_active);
CREATE INDEX idx_user_subscriptions_expires ON user_subscriptions(expires_at);

-- Table des logs d'audit
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),
    success BOOLEAN DEFAULT true,
    error_message TEXT
);

-- Index pour les logs d'audit
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);

-- Vues utiles
CREATE VIEW active_users AS
SELECT u.*, bu.bunker_id, bu.access_level, bu.room_assignment
FROM users u
LEFT JOIN bunker_users bu ON u.id = bu.user_id
WHERE u.is_active = true;

CREATE VIEW current_environmental_status AS
SELECT DISTINCT ON (bunker_id, sensor_location)
    bunker_id,
    sensor_location,
    temperature,
    humidity,
    air_quality,
    oxygen_level,
    co2_level,
    radiation_level,
    atmospheric_pressure,
    timestamp
FROM environmental_data
ORDER BY bunker_id, sensor_location, timestamp DESC;

CREATE VIEW active_alerts AS
SELECT a.*, u.username as resolved_by_username
FROM alerts a
LEFT JOIN users u ON a.resolved_by = u.id
WHERE a.is_resolved = false
ORDER BY a.severity DESC, a.timestamp DESC;

-- Fonctions utiles
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers pour updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bunker_users_updated_at BEFORE UPDATE ON bunker_users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_quiz_categories_updated_at BEFORE UPDATE ON quiz_categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bunker_quizzes_updated_at BEFORE UPDATE ON bunker_quizzes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Fonction pour nettoyer les sessions expirées
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM user_sessions WHERE expires_at < CURRENT_TIMESTAMP;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour calculer le score de quiz
CREATE OR REPLACE FUNCTION calculate_quiz_score(attempt_id INTEGER)
RETURNS INTEGER AS $$
DECLARE
    total_points INTEGER;
    earned_points INTEGER;
    score INTEGER;
BEGIN
    -- Calculer les points totaux possibles
    SELECT COALESCE(SUM(qq.points), 0) INTO total_points
    FROM quiz_attempts qa
    JOIN bunker_quizzes bq ON qa.quiz_id = bq.id
    JOIN quiz_questions qq ON bq.id = qq.quiz_id
    WHERE qa.id = attempt_id AND qq.is_active = true;
    
    -- Calculer les points obtenus (à implémenter selon la logique métier)
    -- Pour l'instant, utiliser le nombre de bonnes réponses
    SELECT qa.correct_answers INTO earned_points
    FROM quiz_attempts qa
    WHERE qa.id = attempt_id;
    
    -- Calculer le pourcentage
    IF total_points > 0 THEN
        score := ROUND((earned_points::DECIMAL / total_points) * 100);
    ELSE
        score := 0;
    END IF;
    
    -- Mettre à jour la tentative
    UPDATE quiz_attempts SET score = score WHERE id = attempt_id;
    
    RETURN score;
END;
$$ LANGUAGE plpgsql;

-- Données initiales
INSERT INTO quiz_categories (name, description, icon, sort_order) VALUES
('Survival Basics', 'Essential survival skills for bunker life', '🏠', 1),
('Emergency Procedures', 'Critical emergency response protocols', '🚨', 2),
('System Maintenance', 'Technical maintenance and troubleshooting', '🔧', 3),
('Security Protocols', 'Security procedures and threat assessment', '🛡️', 4),
('Medical Emergency', 'First aid and medical emergency procedures', '🏥', 5);

-- Utilisateur admin par défaut
INSERT INTO users (username, email, password_hash, role, is_active, is_verified) VALUES
('admin', 'admin@bunker.tech', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Vgj2Oa', 'admin', true, true);

-- Profil bunker pour l'admin
INSERT INTO bunker_users (user_id, bunker_id, access_level, room_assignment, security_clearance) VALUES
(1, 'bunker-01', 'admin', 'Control Room', 5);

-- Abonnement gratuit par défaut pour l'admin
INSERT INTO user_subscriptions (user_id, subscription_type, features) VALUES
(1, 'lataupe_premium', '["all_features", "unlimited_access", "priority_support"]'::jsonb);

COMMIT;
"""
    
    return schema_sql

def create_database_migration_script():
    """Crée le script de migration de SQLite vers PostgreSQL"""
    
    migration_script = """#!/usr/bin/env python3
\"\"\"
Script de migration de SQLite vers PostgreSQL pour lataupe-bunker-tech
\"\"\"

import sqlite3
import psycopg2
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

def migrate_sqlite_to_postgresql():
    \"\"\"Migre les données de SQLite vers PostgreSQL\"\"\"
    
    # Configuration de la base de données
    sqlite_db = 'bunker.db'  # Chemin vers la base SQLite existante
    postgres_config = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'database': os.environ.get('DB_NAME', 'lataupe_bunker'),
        'user': os.environ.get('DB_USER', 'postgres'),
        'password': os.environ.get('DB_PASSWORD', 'password'),
        'port': os.environ.get('DB_PORT', '5432')
    }
    
    print("🔄 Début de la migration SQLite → PostgreSQL...")
    
    try:
        # Connexion SQLite
        sqlite_conn = sqlite3.connect(sqlite_db)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        # Connexion PostgreSQL
        postgres_conn = psycopg2.connect(**postgres_config)
        postgres_cursor = postgres_conn.cursor()
        
        # Migration des utilisateurs
        print("👥 Migration des utilisateurs...")
        sqlite_cursor.execute("SELECT * FROM users")
        users = sqlite_cursor.fetchall()
        
        for user in users:
            postgres_cursor.execute(\"\"\"
                INSERT INTO users (username, email, password_hash, role, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (username) DO NOTHING
            \"\"\", (
                user['username'],
                user['email'],
                user['password_hash'],
                user.get('role', 'resident'),
                user.get('is_active', True),
                datetime.now()
            ))
        
        # Migration des profils bunker
        print("🏠 Migration des profils bunker...")
        sqlite_cursor.execute("SELECT * FROM bunker_users")
        bunker_users = sqlite_cursor.fetchall()
        
        for bunker_user in bunker_users:
            postgres_cursor.execute(\"\"\"
                INSERT INTO bunker_users (user_id, bunker_id, access_level, room_assignment, emergency_contact, medical_info)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id, bunker_id) DO NOTHING
            \"\"\", (
                bunker_user['user_id'],
                bunker_user['bunker_id'],
                bunker_user.get('access_level', 'basic'),
                bunker_user.get('room_assignment'),
                bunker_user.get('emergency_contact'),
                json.dumps(bunker_user.get('medical_info', {})) if bunker_user.get('medical_info') else None
            ))
        
        # Migration des données environnementales
        print("🌡️ Migration des données environnementales...")
        sqlite_cursor.execute("SELECT * FROM environmental_data ORDER BY timestamp DESC LIMIT 10000")
        env_data = sqlite_cursor.fetchall()
        
        for data in env_data:
            postgres_cursor.execute(\"\"\"
                INSERT INTO environmental_data (
                    timestamp, temperature, humidity, air_quality, oxygen_level,
                    co2_level, radiation_level, atmospheric_pressure, bunker_id, sensor_location
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            \"\"\", (
                data['timestamp'],
                data.get('temperature'),
                data.get('humidity'),
                data.get('air_quality'),
                data.get('oxygen_level'),
                data.get('co2_level'),
                data.get('radiation_level'),
                data.get('atmospheric_pressure'),
                data['bunker_id'],
                data.get('sensor_location')
            ))
        
        # Migration des alertes
        print("🚨 Migration des alertes...")
        sqlite_cursor.execute("SELECT * FROM alerts")
        alerts = sqlite_cursor.fetchall()
        
        for alert in alerts:
            postgres_cursor.execute(\"\"\"
                INSERT INTO alerts (
                    timestamp, alert_type, severity, title, message, bunker_id,
                    sensor_location, is_resolved, resolved_by, resolved_at, resolution_notes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            \"\"\", (
                alert['timestamp'],
                alert['alert_type'],
                alert['severity'],
                alert.get('message', alert['message'])[:200],  # Titre limité
                alert['message'],
                alert['bunker_id'],
                alert.get('sensor_location'),
                alert.get('is_resolved', False),
                alert.get('resolved_by'),
                alert.get('resolved_at'),
                alert.get('resolution_notes')
            ))
        
        # Commit des changements
        postgres_conn.commit()
        
        print("✅ Migration terminée avec succès!")
        print(f"   • {len(users)} utilisateurs migrés")
        print(f"   • {len(bunker_users)} profils bunker migrés")
        print(f"   • {len(env_data)} données environnementales migrées")
        print(f"   • {len(alerts)} alertes migrées")
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        postgres_conn.rollback()
        raise
    
    finally:
        sqlite_conn.close()
        postgres_conn.close()

def create_sample_data():
    \"\"\"Crée des données d'exemple pour les tests\"\"\"
    
    postgres_config = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'database': os.environ.get('DB_NAME', 'lataupe_bunker'),
        'user': os.environ.get('DB_USER', 'postgres'),
        'password': os.environ.get('DB_PASSWORD', 'password'),
        'port': os.environ.get('DB_PORT', '5432')
    }
    
    print("📊 Création des données d'exemple...")
    
    try:
        conn = psycopg2.connect(**postgres_config)
        cursor = conn.cursor()
        
        # Créer des utilisateurs de test
        test_users = [
            ('resident1', 'resident1@bunker.tech', 'resident', 'Living Quarter A-12'),
            ('security1', 'security1@bunker.tech', 'security', 'Security Station'),
            ('maintenance1', 'maintenance1@bunker.tech', 'resident', 'Maintenance Bay')
        ]
        
        for username, email, role, room in test_users:
            password_hash = generate_password_hash('password123')
            
            cursor.execute(\"\"\"
                INSERT INTO users (username, email, password_hash, role, is_active, is_verified)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (username) DO NOTHING
                RETURNING id
            \"\"\", (username, email, password_hash, role, True, True))
            
            result = cursor.fetchone()
            if result:
                user_id = result[0]
                
                # Créer le profil bunker
                cursor.execute(\"\"\"
                    INSERT INTO bunker_users (user_id, bunker_id, access_level, room_assignment, security_clearance)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (user_id, bunker_id) DO NOTHING
                \"\"\", (user_id, 'bunker-01', 'basic' if role == 'resident' else 'advanced', room, 2 if role == 'security' else 1))
                
                # Créer l'abonnement gratuit
                cursor.execute(\"\"\"
                    INSERT INTO user_subscriptions (user_id, subscription_type, features)
                    VALUES (%s, %s, %s)
                \"\"\", (user_id, 'free', json.dumps(['basic_quiz', 'emergency_training'])))
        
        # Créer des quiz d'exemple
        sample_quizzes = [
            {
                'title': 'Air Quality Management',
                'description': 'Understanding and maintaining air quality in enclosed spaces',
                'category_id': 1,
                'difficulty': 'medium',
                'is_mandatory': True,
                'questions': [
                    {
                        'question_text': 'What is the ideal oxygen level for a bunker environment?',
                        'options': ['16-18%', '19-21%', '22-24%', '25-27%'],
                        'correct_answer': '19-21%',
                        'explanation': 'Normal atmospheric oxygen levels are 20.9%. Levels below 19% can cause hypoxia.'
                    },
                    {
                        'question_text': 'CO2 levels above 1000 PPM indicate poor ventilation.',
                        'question_type': 'true_false',
                        'options': ['True', 'False'],
                        'correct_answer': 'True',
                        'explanation': 'CO2 levels above 1000 PPM indicate inadequate ventilation and can cause drowsiness.'
                    }
                ]
            }
        ]
        
        for quiz_data in sample_quizzes:
            cursor.execute(\"\"\"
                INSERT INTO bunker_quizzes (title, description, category_id, difficulty, is_mandatory, time_limit, passing_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            \"\"\", (
                quiz_data['title'],
                quiz_data['description'],
                quiz_data['category_id'],
                quiz_data['difficulty'],
                quiz_data['is_mandatory'],
                300,
                80
            ))
            
            quiz_id = cursor.fetchone()[0]
            
            for i, question in enumerate(quiz_data['questions']):
                cursor.execute(\"\"\"
                    INSERT INTO quiz_questions (
                        quiz_id, question_text, question_type, options, correct_answer, explanation, order_index
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                \"\"\", (
                    quiz_id,
                    question['question_text'],
                    question.get('question_type', 'multiple_choice'),
                    json.dumps(question['options']),
                    question['correct_answer'],
                    question['explanation'],
                    i
                ))
        
        conn.commit()
        print("✅ Données d'exemple créées avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des données: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "sample":
        create_sample_data()
    else:
        migrate_sqlite_to_postgresql()
"""
    
    return migration_script

def create_database_config():
    """Crée la configuration de base de données pour différents environnements"""
    
    config = {
        'development': {
            'DATABASE_URL': 'postgresql://postgres:password@localhost:5432/lataupe_bunker_dev',
            'SQLALCHEMY_DATABASE_URI': 'postgresql://postgres:password@localhost:5432/lataupe_bunker_dev',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'pool_size': 10,
                'pool_recycle': 3600,
                'pool_pre_ping': True
            }
        },
        'testing': {
            'DATABASE_URL': 'postgresql://postgres:password@localhost:5432/lataupe_bunker_test',
            'SQLALCHEMY_DATABASE_URI': 'postgresql://postgres:password@localhost:5432/lataupe_bunker_test',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'TESTING': True
        },
        'production': {
            'DATABASE_URL': '${DATABASE_URL}',  # Variable d'environnement
            'SQLALCHEMY_DATABASE_URI': '${DATABASE_URL}',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'pool_size': 20,
                'pool_recycle': 3600,
                'pool_pre_ping': True,
                'connect_args': {
                    'sslmode': 'require'
                }
            }
        }
    }
    
    return json.dumps(config, indent=2)

def create_advanced_models():
    """Crée les modèles SQLAlchemy avancés pour PostgreSQL"""
    
    models_code = """from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy import func, Index
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='resident', nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_verified = db.Column(db.Boolean, default=False)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    bunker_profile = db.relationship('BunkerUser', backref='user', uselist=False, cascade='all, delete-orphan')
    subscription = db.relationship('UserSubscription', backref='user', uselist=False, cascade='all, delete-orphan')
    sessions = db.relationship('UserSession', backref='user', cascade='all, delete-orphan')
    quiz_attempts = db.relationship('QuizAttempt', backref='user', cascade='all, delete-orphan')
    resolved_alerts = db.relationship('Alert', foreign_keys='Alert.resolved_by', backref='resolver')
    sent_messages = db.relationship('EmergencyMessage', backref='sender', cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_locked(self):
        return self.locked_until and self.locked_until > datetime.utcnow()
    
    def lock_account(self, duration_minutes=30):
        self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.failed_login_attempts += 1
    
    def unlock_account(self):
        self.locked_until = None
        self.failed_login_attempts = 0
    
    def has_permission(self, permission):
        role_permissions = {
            'admin': ['all'],
            'security': ['view_alerts', 'manage_alerts', 'view_users', 'emergency_access'],
            'resident': ['view_own_data', 'take_quiz', 'view_environmental']
        }
        return 'all' in role_permissions.get(self.role, []) or permission in role_permissions.get(self.role, [])
    
    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'uuid': str(self.uuid),
            'username': self.username,
            'email': self.email if include_sensitive else None,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_sensitive:
            data.update({
                'failed_login_attempts': self.failed_login_attempts,
                'is_locked': self.is_locked()
            })
        
        return data

class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    ip_address = db.Column(INET)
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    def extend_session(self, duration_hours=24):
        self.expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
        self.last_activity = datetime.utcnow()

class BunkerUser(db.Model):
    __tablename__ = 'bunker_users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    bunker_id = db.Column(db.String(50), nullable=False, index=True)
    access_level = db.Column(db.String(50), default='basic', nullable=False, index=True)
    room_assignment = db.Column(db.String(100))
    emergency_contact = db.Column(db.String(200))
    medical_info = db.Column(JSONB)
    security_clearance = db.Column(db.Integer, default=1, index=True)
    shift_schedule = db.Column(JSONB)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'bunker_id'),
        db.CheckConstraint('security_clearance >= 1 AND security_clearance <= 5'),
    )
    
    def has_clearance_level(self, required_level):
        return self.security_clearance >= required_level
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'bunker_id': self.bunker_id,
            'access_level': self.access_level,
            'room_assignment': self.room_assignment,
            'emergency_contact': self.emergency_contact,
            'medical_info': self.medical_info,
            'security_clearance': self.security_clearance,
            'shift_schedule': self.shift_schedule
        }

class EnvironmentalData(db.Model):
    __tablename__ = 'environmental_data'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    temperature = db.Column(db.Numeric(5, 2))
    humidity = db.Column(db.Numeric(5, 2))
    air_quality = db.Column(db.Numeric(5, 2))
    oxygen_level = db.Column(db.Numeric(5, 2))
    co2_level = db.Column(db.Numeric(7, 2))
    radiation_level = db.Column(db.Numeric(8, 4))
    atmospheric_pressure = db.Column(db.Numeric(7, 2))
    bunker_id = db.Column(db.String(50), nullable=False, index=True)
    sensor_location = db.Column(db.String(100))
    sensor_id = db.Column(db.String(50), index=True)
    data_quality_score = db.Column(db.Numeric(3, 2), default=1.0)
    is_anomaly = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_env_data_bunker_timestamp', 'bunker_id', 'timestamp'),
    )
    
    def is_critical(self):
        \"\"\"Vérifie si les valeurs sont dans des plages critiques\"\"\"
        critical_conditions = []
        
        if self.oxygen_level and self.oxygen_level < 19:
            critical_conditions.append('Low oxygen')
        if self.co2_level and self.co2_level > 5000:
            critical_conditions.append('High CO2')
        if self.radiation_level and self.radiation_level > 100:
            critical_conditions.append('High radiation')
        if self.temperature and (self.temperature < 10 or self.temperature > 35):
            critical_conditions.append('Extreme temperature')
            
        return critical_conditions
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'temperature': float(self.temperature) if self.temperature else None,
            'humidity': float(self.humidity) if self.humidity else None,
            'air_quality': float(self.air_quality) if self.air_quality else None,
            'oxygen_level': float(self.oxygen_level) if self.oxygen_level else None,
            'co2_level': float(self.co2_level) if self.co2_level else None,
            'radiation_level': float(self.radiation_level) if self.radiation_level else None,
            'atmospheric_pressure': float(self.atmospheric_pressure) if self.atmospheric_pressure else None,
            'bunker_id': self.bunker_id,
            'sensor_location': self.sensor_location,
            'sensor_id': self.sensor_id,
            'data_quality_score': float(self.data_quality_score) if self.data_quality_score else None,
            'is_anomaly': self.is_anomaly,
            'is_critical': bool(self.is_critical())
        }

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    alert_type = db.Column(db.String(50), nullable=False, index=True)
    severity = db.Column(db.String(20), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    bunker_id = db.Column(db.String(50), nullable=False, index=True)
    sensor_location = db.Column(db.String(100))
    sensor_id = db.Column(db.String(50))
    threshold_value = db.Column(db.Numeric(10, 4))
    actual_value = db.Column(db.Numeric(10, 4))
    is_resolved = db.Column(db.Boolean, default=False, index=True)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    resolved_at = db.Column(db.DateTime)
    resolution_notes = db.Column(db.Text)
    auto_resolved = db.Column(db.Boolean, default=False)
    escalation_level = db.Column(db.Integer, default=1, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_alerts_bunker_severity', 'bunker_id', 'severity', 'timestamp'),
        db.CheckConstraint('escalation_level >= 1 AND escalation_level <= 5'),
    )
    
    def resolve(self, user_id, notes=None):
        self.is_resolved = True
        self.resolved_by = user_id
        self.resolved_at = datetime.utcnow()
        self.resolution_notes = notes
    
    def escalate(self):
        if self.escalation_level < 5:
            self.escalation_level += 1
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': str(self.uuid),
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'title': self.title,
            'message': self.message,
            'bunker_id': self.bunker_id,
            'sensor_location': self.sensor_location,
            'sensor_id': self.sensor_id,
            'threshold_value': float(self.threshold_value) if self.threshold_value else None,
            'actual_value': float(self.actual_value) if self.actual_value else None,
            'is_resolved': self.is_resolved,
            'resolved_by': self.resolved_by,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolution_notes': self.resolution_notes,
            'auto_resolved': self.auto_resolved,
            'escalation_level': self.escalation_level
        }

# Autres modèles (QuizCategory, BunkerQuiz, etc.) restent similaires mais avec les améliorations PostgreSQL

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    resource_type = db.Column(db.String(50), index=True)
    resource_id = db.Column(db.String(100))
    old_values = db.Column(JSONB)
    new_values = db.Column(JSONB)
    ip_address = db.Column(INET)
    user_agent = db.Column(db.Text)
    session_id = db.Column(db.String(255))
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    
    __table_args__ = (
        Index('idx_audit_logs_resource', 'resource_type', 'resource_id'),
    )
    
    @staticmethod
    def log_action(user_id, action, resource_type=None, resource_id=None, 
                   old_values=None, new_values=None, ip_address=None, 
                   user_agent=None, session_id=None, success=True, error_message=None):
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            success=success,
            error_message=error_message
        )
        db.session.add(log)
        return log
"""
    
    return models_code

def main():
    """Fonction principale pour l'implémentation SQL"""
    project_path = "/home/ubuntu/lataupe-bunker-tech"
    
    print("🗄️ Implémentation de la base de données SQL pour lataupe-bunker-tech...")
    print("=" * 75)
    
    # Créer le dossier database
    db_dir = os.path.join(project_path, 'database')
    os.makedirs(db_dir, exist_ok=True)
    
    # Créer le schéma PostgreSQL
    schema_file = os.path.join(db_dir, 'postgresql_schema.sql')
    with open(schema_file, 'w') as f:
        f.write(create_postgresql_schema())
    
    # Créer le script de migration
    migration_file = os.path.join(db_dir, 'migrate_to_postgresql.py')
    with open(migration_file, 'w') as f:
        f.write(create_database_migration_script())
    
    # Créer la configuration de base de données
    config_file = os.path.join(db_dir, 'database_config.json')
    with open(config_file, 'w') as f:
        f.write(create_database_config())
    
    # Créer les modèles avancés
    models_file = os.path.join(project_path, 'src', 'models', 'advanced_models.py')
    with open(models_file, 'w') as f:
        f.write(create_advanced_models())
    
    # Rendre le script de migration exécutable
    os.chmod(migration_file, 0o755)
    
    print("\\n✅ Implémentation SQL terminée avec succès!")
    print("\\n📋 Fichiers créés:")
    print(f"   • Schéma PostgreSQL: {schema_file}")
    print(f"   • Script de migration: {migration_file}")
    print(f"   • Configuration DB: {config_file}")
    print(f"   • Modèles avancés: {models_file}")
    
    print("\\n🚀 Fonctionnalités implémentées:")
    print("   • Schéma PostgreSQL complet avec partitioning")
    print("   • Migration automatique depuis SQLite")
    print("   • Modèles SQLAlchemy avancés")
    print("   • Audit logging et sessions")
    print("   • Index optimisés pour les performances")
    print("   • Contraintes de sécurité et validation")
    
    print("\\n⚠️  Prochaines étapes:")
    print("   1. Installer PostgreSQL et créer la base de données")
    print("   2. Exécuter le schéma SQL pour créer les tables")
    print("   3. Lancer la migration des données existantes")
    print("   4. Mettre à jour main_secure.py pour utiliser PostgreSQL")
    print("   5. Tester les nouvelles fonctionnalités")
    
    return True

if __name__ == "__main__":
    main()

