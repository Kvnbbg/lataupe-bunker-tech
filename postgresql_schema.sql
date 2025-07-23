
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
