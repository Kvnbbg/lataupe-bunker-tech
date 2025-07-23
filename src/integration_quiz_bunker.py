#!/usr/bin/env python3
"""
Script d'intégration des fonctionnalités quiz de shiny-dollop dans lataupe-bunker-tech
Adapte le système de quiz pour le contexte de survie en bunker
"""

import os
import json
from pathlib import Path

def create_bunker_quiz_models():
    """Crée les modèles de données pour les quiz bunker"""
    quiz_models = """from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class QuizCategory(db.Model):
    __tablename__ = 'quiz_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # Emoji ou classe d'icône
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    quizzes = db.relationship('BunkerQuiz', backref='category', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'is_active': self.is_active,
            'quiz_count': self.quizzes.count()
        }

class BunkerQuiz(db.Model):
    __tablename__ = 'bunker_quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('quiz_categories.id'), nullable=False)
    difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard, expert
    required_for_role = db.Column(db.String(50))  # admin, security, resident
    is_mandatory = db.Column(db.Boolean, default=False)
    time_limit = db.Column(db.Integer, default=300)  # secondes
    passing_score = db.Column(db.Integer, default=70)  # pourcentage
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    questions = db.relationship('QuizQuestion', backref='quiz', lazy='dynamic', cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category.name if self.category else None,
            'difficulty': self.difficulty,
            'required_for_role': self.required_for_role,
            'is_mandatory': self.is_mandatory,
            'time_limit': self.time_limit,
            'passing_score': self.passing_score,
            'question_count': self.questions.count(),
            'is_active': self.is_active
        }

class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('bunker_quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), default='multiple_choice')  # multiple_choice, true_false, text
    options = db.Column(db.JSON)  # Liste des options pour les questions à choix multiples
    correct_answer = db.Column(db.String(500), nullable=False)
    explanation = db.Column(db.Text)  # Explication de la réponse correcte
    points = db.Column(db.Integer, default=1)
    order_index = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'options': self.options,
            'explanation': self.explanation,
            'points': self.points,
            'order_index': self.order_index
        }

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('bunker_quizzes.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    score = db.Column(db.Integer)  # Pourcentage
    total_questions = db.Column(db.Integer)
    correct_answers = db.Column(db.Integer)
    time_taken = db.Column(db.Integer)  # secondes
    is_passed = db.Column(db.Boolean)
    answers = db.Column(db.JSON)  # Stockage des réponses données
    
    # Relations
    user = db.relationship('User', backref='quiz_attempts')
    
    # Index pour les requêtes fréquentes
    __table_args__ = (
        db.Index('idx_user_quiz_attempts', 'user_id', 'quiz_id', 'completed_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'quiz_id': self.quiz_id,
            'quiz_title': self.quiz.title if self.quiz else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'score': self.score,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'time_taken': self.time_taken,
            'is_passed': self.is_passed
        }

class UserSubscription(db.Model):
    __tablename__ = 'user_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subscription_type = db.Column(db.String(50), nullable=False)  # free, lataupe_plus
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    features = db.Column(db.JSON)  # Liste des fonctionnalités disponibles
    
    # Relations
    user = db.relationship('User', backref=db.backref('subscription', uselist=False))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subscription_type': self.subscription_type,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'features': self.features
        }
"""
    return quiz_models

def create_bunker_quiz_routes():
    """Crée les routes pour les quiz bunker"""
    quiz_routes = """from flask import Blueprint, request, jsonify, session, render_template
from flask_wtf import FlaskForm
from wtforms import RadioField, HiddenField, SubmitField
from wtforms.validators import DataRequired
from src.models.user import db, User
from src.models.quiz import QuizCategory, BunkerQuiz, QuizQuestion, QuizAttempt, UserSubscription
from datetime import datetime
import json

quiz_bp = Blueprint('quiz', __name__, url_prefix='/api/quiz')

class QuizForm(FlaskForm):
    choice = RadioField('Choice', validators=[DataRequired()])
    question_id = HiddenField()
    submit = SubmitField('Next Question')

def check_subscription_access(user, feature):
    \"\"\"Vérifie si l'utilisateur a accès à une fonctionnalité\"\"\"
    if not user.subscription:
        return feature in ['basic_quiz', 'emergency_training']
    
    return feature in user.subscription.features

@quiz_bp.route('/categories')
def get_categories():
    \"\"\"Récupère les catégories de quiz disponibles\"\"\"
    categories = QuizCategory.query.filter_by(is_active=True).all()
    return jsonify([cat.to_dict() for cat in categories])

@quiz_bp.route('/category/<int:category_id>/quizzes')
def get_quizzes_by_category(category_id):
    \"\"\"Récupère les quiz d'une catégorie\"\"\"
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.get(session['user_id'])
    quizzes = BunkerQuiz.query.filter_by(category_id=category_id, is_active=True).all()
    
    result = []
    for quiz in quizzes:
        quiz_data = quiz.to_dict()
        
        # Vérifier l'accès selon l'abonnement
        if quiz.required_for_role and quiz.required_for_role != user.role:
            if not check_subscription_access(user, 'advanced_training'):
                quiz_data['locked'] = True
                quiz_data['lock_reason'] = 'Requires Lataupe+ subscription'
        
        # Ajouter les statistiques de l'utilisateur
        last_attempt = QuizAttempt.query.filter_by(
            user_id=user.id, 
            quiz_id=quiz.id
        ).order_by(QuizAttempt.completed_at.desc()).first()
        
        if last_attempt:
            quiz_data['last_score'] = last_attempt.score
            quiz_data['is_passed'] = last_attempt.is_passed
            quiz_data['last_attempt'] = last_attempt.completed_at.isoformat()
        
        result.append(quiz_data)
    
    return jsonify(result)

@quiz_bp.route('/quiz/<int:quiz_id>/start', methods=['POST'])
def start_quiz(quiz_id):
    \"\"\"Démarre une nouvelle tentative de quiz\"\"\"
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.get(session['user_id'])
    quiz = BunkerQuiz.query.get_or_404(quiz_id)
    
    # Vérifier l'accès
    if quiz.required_for_role and quiz.required_for_role != user.role:
        if not check_subscription_access(user, 'advanced_training'):
            return jsonify({'error': 'Lataupe+ subscription required'}), 403
    
    # Créer une nouvelle tentative
    attempt = QuizAttempt(
        user_id=user.id,
        quiz_id=quiz_id,
        total_questions=quiz.questions.count()
    )
    
    db.session.add(attempt)
    db.session.commit()
    
    # Récupérer la première question
    first_question = quiz.questions.filter_by(is_active=True).order_by(QuizQuestion.order_index).first()
    
    return jsonify({
        'attempt_id': attempt.id,
        'quiz': quiz.to_dict(),
        'first_question': first_question.to_dict() if first_question else None,
        'time_limit': quiz.time_limit
    })

@quiz_bp.route('/attempt/<int:attempt_id>/question/<int:question_id>', methods=['GET'])
def get_question(attempt_id, question_id):
    \"\"\"Récupère une question spécifique\"\"\"
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    if attempt.user_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    question = QuizQuestion.query.get_or_404(question_id)
    if question.quiz_id != attempt.quiz_id:
        return jsonify({'error': 'Question not in this quiz'}), 400
    
    return jsonify(question.to_dict())

@quiz_bp.route('/attempt/<int:attempt_id>/answer', methods=['POST'])
def submit_answer(attempt_id):
    \"\"\"Soumet une réponse à une question\"\"\"
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    if attempt.user_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if attempt.completed_at:
        return jsonify({'error': 'Quiz already completed'}), 400
    
    question_id = data.get('question_id')
    answer = data.get('answer')
    
    question = QuizQuestion.query.get_or_404(question_id)
    
    # Stocker la réponse
    if not attempt.answers:
        attempt.answers = {}
    
    attempt.answers[str(question_id)] = {
        'answer': answer,
        'correct': answer == question.correct_answer,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # Marquer les changements sur le champ JSON
    db.session.merge(attempt)
    db.session.commit()
    
    # Récupérer la question suivante
    next_question = QuizQuestion.query.filter(
        QuizQuestion.quiz_id == attempt.quiz_id,
        QuizQuestion.order_index > question.order_index,
        QuizQuestion.is_active == True
    ).order_by(QuizQuestion.order_index).first()
    
    return jsonify({
        'correct': answer == question.correct_answer,
        'explanation': question.explanation,
        'next_question': next_question.to_dict() if next_question else None,
        'is_last_question': next_question is None
    })

@quiz_bp.route('/attempt/<int:attempt_id>/complete', methods=['POST'])
def complete_quiz(attempt_id):
    \"\"\"Termine un quiz et calcule le score\"\"\"
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    if attempt.user_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if attempt.completed_at:
        return jsonify({'error': 'Quiz already completed'}), 400
    
    # Calculer le score
    correct_count = 0
    total_questions = attempt.total_questions
    
    if attempt.answers:
        for answer_data in attempt.answers.values():
            if answer_data.get('correct', False):
                correct_count += 1
    
    score = int((correct_count / total_questions) * 100) if total_questions > 0 else 0
    time_taken = int((datetime.utcnow() - attempt.started_at).total_seconds())
    
    # Mettre à jour la tentative
    attempt.completed_at = datetime.utcnow()
    attempt.score = score
    attempt.correct_answers = correct_count
    attempt.time_taken = time_taken
    attempt.is_passed = score >= attempt.quiz.passing_score
    
    db.session.commit()
    
    return jsonify({
        'score': score,
        'correct_answers': correct_count,
        'total_questions': total_questions,
        'time_taken': time_taken,
        'is_passed': attempt.is_passed,
        'passing_score': attempt.quiz.passing_score
    })

@quiz_bp.route('/user/stats')
def get_user_stats():
    \"\"\"Récupère les statistiques de quiz de l'utilisateur\"\"\"
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    # Statistiques générales
    total_attempts = QuizAttempt.query.filter_by(user_id=user_id).filter(
        QuizAttempt.completed_at.isnot(None)
    ).count()
    
    passed_attempts = QuizAttempt.query.filter_by(user_id=user_id, is_passed=True).count()
    
    avg_score = db.session.query(db.func.avg(QuizAttempt.score)).filter_by(
        user_id=user_id
    ).filter(QuizAttempt.completed_at.isnot(None)).scalar()
    
    # Quiz obligatoires complétés
    mandatory_quizzes = BunkerQuiz.query.filter_by(is_mandatory=True).count()
    completed_mandatory = db.session.query(QuizAttempt).join(BunkerQuiz).filter(
        QuizAttempt.user_id == user_id,
        QuizAttempt.is_passed == True,
        BunkerQuiz.is_mandatory == True
    ).count()
    
    return jsonify({
        'total_attempts': total_attempts,
        'passed_attempts': passed_attempts,
        'pass_rate': int((passed_attempts / total_attempts) * 100) if total_attempts > 0 else 0,
        'average_score': int(avg_score) if avg_score else 0,
        'mandatory_completed': completed_mandatory,
        'mandatory_total': mandatory_quizzes,
        'mandatory_progress': int((completed_mandatory / mandatory_quizzes) * 100) if mandatory_quizzes > 0 else 0
    })

# Routes pour les pop-up d'enregistrement
@quiz_bp.route('/subscription/check')
def check_subscription():
    \"\"\"Vérifie le statut d'abonnement de l'utilisateur\"\"\"
    if 'user_id' not in session:
        return jsonify({'authenticated': False, 'subscription': 'none'})
    
    user = User.query.get(session['user_id'])
    subscription = user.subscription if user else None
    
    return jsonify({
        'authenticated': True,
        'subscription': subscription.subscription_type if subscription else 'free',
        'features': subscription.features if subscription else ['basic_quiz', 'emergency_training'],
        'expires_at': subscription.expires_at.isoformat() if subscription and subscription.expires_at else None
    })

@quiz_bp.route('/subscription/upgrade-popup')
def show_upgrade_popup():
    \"\"\"Affiche le pop-up d'upgrade vers Lataupe+\"\"\"
    return jsonify({
        'title': 'Upgrade to Lataupe+',
        'message': 'Unlock advanced training modules, detailed analytics, and priority support.',
        'features': [
            'Advanced survival training',
            'Detailed performance analytics',
            'Priority emergency support',
            'Unlimited quiz attempts',
            'Custom training programs'
        ],
        'price': '€9.99/month',
        'trial_available': True
    })
"""
    return quiz_routes

def create_bunker_quiz_data():
    """Crée les données de quiz adaptées au contexte bunker"""
    quiz_data = {
        "categories": [
            {
                "name": "Survival Basics",
                "description": "Essential survival skills for bunker life",
                "icon": "🏠",
                "quizzes": [
                    {
                        "title": "Air Quality Management",
                        "description": "Understanding and maintaining air quality in enclosed spaces",
                        "difficulty": "medium",
                        "required_for_role": "resident",
                        "is_mandatory": True,
                        "time_limit": 300,
                        "passing_score": 80,
                        "questions": [
                            {
                                "question_text": "What is the ideal oxygen level for a bunker environment?",
                                "question_type": "multiple_choice",
                                "options": ["16-18%", "19-21%", "22-24%", "25-27%"],
                                "correct_answer": "19-21%",
                                "explanation": "Normal atmospheric oxygen levels are 20.9%. Levels below 19% can cause hypoxia.",
                                "points": 2
                            },
                            {
                                "question_text": "CO2 levels above 1000 PPM indicate poor ventilation.",
                                "question_type": "true_false",
                                "options": ["True", "False"],
                                "correct_answer": "True",
                                "explanation": "CO2 levels above 1000 PPM indicate inadequate ventilation and can cause drowsiness.",
                                "points": 1
                            }
                        ]
                    }
                ]
            },
            {
                "name": "Emergency Procedures",
                "description": "Critical emergency response protocols",
                "icon": "🚨",
                "quizzes": [
                    {
                        "title": "Radiation Detection",
                        "description": "Identifying and responding to radiation threats",
                        "difficulty": "hard",
                        "required_for_role": "security",
                        "is_mandatory": True,
                        "time_limit": 600,
                        "passing_score": 85,
                        "questions": [
                            {
                                "question_text": "What radiation level requires immediate evacuation?",
                                "question_type": "multiple_choice",
                                "options": ["1 µSv/h", "10 µSv/h", "100 µSv/h", "1000 µSv/h"],
                                "correct_answer": "100 µSv/h",
                                "explanation": "Levels above 100 µSv/h require immediate protective action.",
                                "points": 3
                            }
                        ]
                    }
                ]
            },
            {
                "name": "System Maintenance",
                "description": "Technical maintenance and troubleshooting",
                "icon": "🔧",
                "quizzes": [
                    {
                        "title": "HVAC System Basics",
                        "description": "Understanding heating, ventilation, and air conditioning systems",
                        "difficulty": "expert",
                        "required_for_role": "admin",
                        "is_mandatory": False,
                        "time_limit": 900,
                        "passing_score": 90,
                        "questions": [
                            {
                                "question_text": "What is the primary function of a HEPA filter?",
                                "question_type": "multiple_choice",
                                "options": [
                                    "Remove odors",
                                    "Remove particles ≥0.3 microns",
                                    "Remove gases",
                                    "Regulate temperature"
                                ],
                                "correct_answer": "Remove particles ≥0.3 microns",
                                "explanation": "HEPA filters remove 99.97% of particles 0.3 microns or larger.",
                                "points": 2
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    return json.dumps(quiz_data, indent=2)

def create_quiz_frontend_components():
    """Crée les composants frontend pour les quiz"""
    
    # CSS pour les quiz bunker
    quiz_css = """/* Quiz Bunker Styles */
.quiz-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

.quiz-card {
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    border: 1px solid #444;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    color: #fff;
}

.quiz-header {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
}

.quiz-icon {
    font-size: 2rem;
    margin-right: 12px;
}

.quiz-title {
    font-size: 1.5rem;
    font-weight: bold;
    margin: 0;
}

.quiz-difficulty {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: bold;
    margin-left: auto;
}

.difficulty-easy { background-color: #28a745; }
.difficulty-medium { background-color: #ffc107; color: #000; }
.difficulty-hard { background-color: #fd7e14; }
.difficulty-expert { background-color: #dc3545; }

.quiz-stats {
    display: flex;
    gap: 20px;
    margin-top: 16px;
    font-size: 0.9rem;
    color: #ccc;
}

.quiz-question {
    background: #333;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
}

.question-text {
    font-size: 1.1rem;
    margin-bottom: 16px;
    line-height: 1.5;
}

.quiz-options {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.quiz-option {
    background: #444;
    border: 2px solid #555;
    border-radius: 8px;
    padding: 12px 16px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
}

.quiz-option:hover {
    background: #555;
    border-color: #007bff;
}

.quiz-option.selected {
    background: #007bff;
    border-color: #0056b3;
}

.quiz-option.correct {
    background: #28a745;
    border-color: #1e7e34;
}

.quiz-option.incorrect {
    background: #dc3545;
    border-color: #c82333;
}

.quiz-timer {
    position: fixed;
    top: 20px;
    right: 20px;
    background: #dc3545;
    color: white;
    padding: 10px 16px;
    border-radius: 20px;
    font-weight: bold;
    z-index: 1000;
}

.quiz-timer.warning {
    background: #ffc107;
    color: #000;
    animation: pulse 1s infinite;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

.quiz-progress {
    background: #333;
    border-radius: 10px;
    height: 8px;
    margin-bottom: 20px;
    overflow: hidden;
}

.quiz-progress-bar {
    background: linear-gradient(90deg, #007bff, #28a745);
    height: 100%;
    transition: width 0.3s ease;
}

.quiz-results {
    text-align: center;
    padding: 40px 20px;
}

.score-display {
    font-size: 3rem;
    font-weight: bold;
    margin-bottom: 20px;
}

.score-passed { color: #28a745; }
.score-failed { color: #dc3545; }

.subscription-popup {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
}

.popup-content {
    background: #2d2d2d;
    border-radius: 12px;
    padding: 30px;
    max-width: 500px;
    width: 90%;
    color: #fff;
    text-align: center;
}

.popup-features {
    list-style: none;
    padding: 0;
    margin: 20px 0;
}

.popup-features li {
    padding: 8px 0;
    border-bottom: 1px solid #444;
}

.popup-features li:before {
    content: "✓ ";
    color: #28a745;
    font-weight: bold;
}

.btn-upgrade {
    background: linear-gradient(135deg, #007bff, #0056b3);
    border: none;
    color: white;
    padding: 12px 24px;
    border-radius: 6px;
    font-weight: bold;
    cursor: pointer;
    transition: transform 0.2s ease;
}

.btn-upgrade:hover {
    transform: translateY(-2px);
}

/* Responsive design */
@media (max-width: 768px) {
    .quiz-container {
        padding: 10px;
    }
    
    .quiz-card {
        padding: 16px;
    }
    
    .quiz-timer {
        position: relative;
        top: auto;
        right: auto;
        margin-bottom: 20px;
        display: inline-block;
    }
}
"""
    
    # JavaScript pour les quiz bunker
    quiz_js = """// Quiz Bunker JavaScript
class BunkerQuizManager {
    constructor() {
        this.currentAttempt = null;
        this.currentQuestion = null;
        this.timeRemaining = 0;
        this.timerInterval = null;
        this.answers = {};
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // Gestionnaires d'événements pour les quiz
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('start-quiz-btn')) {
                this.startQuiz(e.target.dataset.quizId);
            }
            
            if (e.target.classList.contains('quiz-option')) {
                this.selectOption(e.target);
            }
            
            if (e.target.classList.contains('next-question-btn')) {
                this.nextQuestion();
            }
            
            if (e.target.classList.contains('close-popup')) {
                this.closePopup();
            }
        });
    }
    
    async startQuiz(quizId) {
        try {
            const response = await fetch(`/api/quiz/quiz/${quizId}/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (response.status === 403) {
                this.showSubscriptionPopup();
                return;
            }
            
            const data = await response.json();
            this.currentAttempt = data.attempt_id;
            this.timeRemaining = data.time_limit;
            
            this.displayQuestion(data.first_question);
            this.startTimer();
            
        } catch (error) {
            console.error('Error starting quiz:', error);
            this.showError('Failed to start quiz. Please try again.');
        }
    }
    
    displayQuestion(question) {
        this.currentQuestion = question;
        const container = document.getElementById('quiz-container');
        
        container.innerHTML = `
            <div class="quiz-card">
                <div class="quiz-timer" id="timer">${this.formatTime(this.timeRemaining)}</div>
                <div class="quiz-question">
                    <div class="question-text">${question.question_text}</div>
                    <div class="quiz-options" id="quiz-options">
                        ${this.renderOptions(question)}
                    </div>
                </div>
                <button class="btn btn-primary next-question-btn" disabled>
                    Next Question
                </button>
            </div>
        `;
    }
    
    renderOptions(question) {
        if (question.question_type === 'multiple_choice') {
            return question.options.map((option, index) => `
                <div class="quiz-option" data-value="${option}">
                    <span>${option}</span>
                </div>
            `).join('');
        } else if (question.question_type === 'true_false') {
            return `
                <div class="quiz-option" data-value="True">True</div>
                <div class="quiz-option" data-value="False">False</div>
            `;
        }
        return '';
    }
    
    selectOption(optionElement) {
        // Désélectionner toutes les options
        document.querySelectorAll('.quiz-option').forEach(opt => {
            opt.classList.remove('selected');
        });
        
        // Sélectionner l'option cliquée
        optionElement.classList.add('selected');
        
        // Activer le bouton suivant
        document.querySelector('.next-question-btn').disabled = false;
        
        // Stocker la réponse
        this.answers[this.currentQuestion.id] = optionElement.dataset.value;
    }
    
    async nextQuestion() {
        const selectedAnswer = this.answers[this.currentQuestion.id];
        
        try {
            const response = await fetch(`/api/quiz/attempt/${this.currentAttempt}/answer`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    question_id: this.currentQuestion.id,
                    answer: selectedAnswer
                })
            });
            
            const data = await response.json();
            
            // Afficher la correction
            this.showAnswerFeedback(data);
            
            // Passer à la question suivante ou terminer
            setTimeout(() => {
                if (data.next_question) {
                    this.displayQuestion(data.next_question);
                } else {
                    this.completeQuiz();
                }
            }, 2000);
            
        } catch (error) {
            console.error('Error submitting answer:', error);
        }
    }
    
    showAnswerFeedback(data) {
        const options = document.querySelectorAll('.quiz-option');
        options.forEach(option => {
            if (option.classList.contains('selected')) {
                option.classList.add(data.correct ? 'correct' : 'incorrect');
            }
        });
        
        if (data.explanation) {
            const explanationDiv = document.createElement('div');
            explanationDiv.className = 'answer-explanation';
            explanationDiv.innerHTML = `<p><strong>Explanation:</strong> ${data.explanation}</p>`;
            document.querySelector('.quiz-question').appendChild(explanationDiv);
        }
    }
    
    async completeQuiz() {
        this.stopTimer();
        
        try {
            const response = await fetch(`/api/quiz/attempt/${this.currentAttempt}/complete`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            const results = await response.json();
            this.displayResults(results);
            
        } catch (error) {
            console.error('Error completing quiz:', error);
        }
    }
    
    displayResults(results) {
        const container = document.getElementById('quiz-container');
        const scoreClass = results.is_passed ? 'score-passed' : 'score-failed';
        
        container.innerHTML = `
            <div class="quiz-results">
                <div class="score-display ${scoreClass}">
                    ${results.score}%
                </div>
                <h3>${results.is_passed ? 'Congratulations!' : 'Keep Training!'}</h3>
                <p>You scored ${results.correct_answers} out of ${results.total_questions} questions correctly.</p>
                <p>Time taken: ${this.formatTime(results.time_taken)}</p>
                <p>Passing score: ${results.passing_score}%</p>
                
                <div class="mt-4">
                    <button class="btn btn-primary" onclick="location.reload()">
                        Take Another Quiz
                    </button>
                </div>
            </div>
        `;
    }
    
    startTimer() {
        this.timerInterval = setInterval(() => {
            this.timeRemaining--;
            
            const timerElement = document.getElementById('timer');
            if (timerElement) {
                timerElement.textContent = this.formatTime(this.timeRemaining);
                
                if (this.timeRemaining <= 60) {
                    timerElement.classList.add('warning');
                }
            }
            
            if (this.timeRemaining <= 0) {
                this.completeQuiz();
            }
        }, 1000);
    }
    
    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }
    
    formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    
    showSubscriptionPopup() {
        fetch('/api/quiz/subscription/upgrade-popup')
            .then(response => response.json())
            .then(data => {
                const popup = document.createElement('div');
                popup.className = 'subscription-popup';
                popup.innerHTML = `
                    <div class="popup-content">
                        <h3>${data.title}</h3>
                        <p>${data.message}</p>
                        <ul class="popup-features">
                            ${data.features.map(feature => `<li>${feature}</li>`).join('')}
                        </ul>
                        <div class="popup-actions">
                            <button class="btn-upgrade">
                                Upgrade Now - ${data.price}
                            </button>
                            <button class="btn btn-secondary close-popup">
                                Maybe Later
                            </button>
                        </div>
                    </div>
                `;
                document.body.appendChild(popup);
            });
    }
    
    closePopup() {
        const popup = document.querySelector('.subscription-popup');
        if (popup) {
            popup.remove();
        }
    }
    
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger';
        errorDiv.textContent = message;
        document.body.insertBefore(errorDiv, document.body.firstChild);
        
        setTimeout(() => errorDiv.remove(), 5000);
    }
    
    getCSRFToken() {
        return document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || '';
    }
}

// Initialiser le gestionnaire de quiz
document.addEventListener('DOMContentLoaded', () => {
    new BunkerQuizManager();
});
"""
    
    return {
        'css': quiz_css,
        'js': quiz_js
    }

def create_integration_files(project_path):
    """Crée tous les fichiers d'intégration"""
    
    # Créer le dossier pour les nouveaux modèles
    models_dir = os.path.join(project_path, 'src', 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    # Créer le modèle quiz
    quiz_model_file = os.path.join(models_dir, 'quiz.py')
    with open(quiz_model_file, 'w') as f:
        f.write(create_bunker_quiz_models())
    
    # Créer le dossier pour les nouvelles routes
    routes_dir = os.path.join(project_path, 'src', 'routes')
    os.makedirs(routes_dir, exist_ok=True)
    
    # Créer les routes quiz
    quiz_routes_file = os.path.join(routes_dir, 'quiz.py')
    with open(quiz_routes_file, 'w') as f:
        f.write(create_bunker_quiz_routes())
    
    # Créer les données de quiz
    data_dir = os.path.join(project_path, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    quiz_data_file = os.path.join(data_dir, 'bunker_quiz_data.json')
    with open(quiz_data_file, 'w') as f:
        f.write(create_bunker_quiz_data())
    
    # Créer les composants frontend
    static_dir = os.path.join(project_path, 'src', 'static')
    css_dir = os.path.join(static_dir, 'css')
    js_dir = os.path.join(static_dir, 'js')
    
    os.makedirs(css_dir, exist_ok=True)
    os.makedirs(js_dir, exist_ok=True)
    
    frontend_components = create_quiz_frontend_components()
    
    with open(os.path.join(css_dir, 'quiz_bunker.css'), 'w') as f:
        f.write(frontend_components['css'])
    
    with open(os.path.join(js_dir, 'quiz_bunker.js'), 'w') as f:
        f.write(frontend_components['js'])
    
    return {
        'models': quiz_model_file,
        'routes': quiz_routes_file,
        'data': quiz_data_file,
        'css': os.path.join(css_dir, 'quiz_bunker.css'),
        'js': os.path.join(js_dir, 'quiz_bunker.js')
    }

def main():
    """Fonction principale pour l'intégration des quiz"""
    project_path = "/home/ubuntu/lataupe-bunker-tech"
    
    print("🎯 Intégration des fonctionnalités quiz dans lataupe-bunker-tech...")
    print("=" * 70)
    
    # Créer tous les fichiers d'intégration
    created_files = create_integration_files(project_path)
    
    print("\\n✅ Fichiers d'intégration créés avec succès!")
    print("\\n📋 Fichiers créés:")
    for file_type, file_path in created_files.items():
        print(f"   • {file_type.upper()}: {file_path}")
    
    print("\\n🎮 Fonctionnalités intégrées:")
    print("   • Système de quiz adapté au contexte bunker")
    print("   • Catégories: Survie, Urgences, Maintenance")
    print("   • Pop-up d'upgrade vers Lataupe+")
    print("   • Système de scoring et statistiques")
    print("   • Interface responsive et sécurisée")
    
    print("\\n⚠️  Actions requises:")
    print("   1. Intégrer les nouveaux modèles dans main_secure.py")
    print("   2. Ajouter les routes quiz au blueprint principal")
    print("   3. Créer les templates HTML pour l'interface quiz")
    print("   4. Tester les fonctionnalités avec des données de test")
    print("   5. Configurer le système d'abonnement Lataupe+")
    
    return True

if __name__ == "__main__":
    main()

