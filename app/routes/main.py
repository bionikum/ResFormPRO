from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import User, PostureAnalysis, Recommendation
from app import db

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    # Получаем анализы пользователя
    analyses = PostureAnalysis.query.filter_by(user_id=current_user.id)\
        .order_by(PostureAnalysis.created_at.desc()).all()
    
    # Получаем рекомендации
    recommendations = Recommendation.query.order_by(Recommendation.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         analyses=analyses,
                         recommendations=recommendations)

@bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@bp.route('/analyses')
@login_required
def analyses():
    analyses = PostureAnalysis.query.filter_by(user_id=current_user.id)\
        .order_by(PostureAnalysis.created_at.desc()).all()
    return render_template('analysis/index.html', analyses=analyses)

@bp.route('/analysis/<int:analysis_id>')
@login_required
def view_analysis(analysis_id):
    analysis = PostureAnalysis.query.get_or_404(analysis_id)
    
    # Проверяем, что анализ принадлежит пользователю или пользователь - админ/специалист
    if analysis.user_id != current_user.id and not (current_user.is_admin() or current_user.is_specialist()):
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('main.dashboard'))
    
    return render_template('analysis/detail.html', analysis=analysis)

@bp.route('/recommendations')
@login_required
def recommendations():
    all_recommendations = Recommendation.query.order_by(Recommendation.created_at.desc()).all()
    return render_template('recommendations.html', recommendations=all_recommendations)

@bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@bp.route('/about')
def about():
    return render_template('about.html')

@bp.route('/privacy')
def privacy():
    return render_template('privacy.html')

@bp.route('/terms')
def terms():
    return render_template('terms.html')

@bp.route('/api/user_stats')
@login_required
def user_stats():
    # Статистика пользователя
    total_analyses = PostureAnalysis.query.filter_by(user_id=current_user.id).count()
    completed_analyses = PostureAnalysis.query.filter_by(
        user_id=current_user.id, 
        status='completed'
    ).count()
    
    # Средние оценки
    avg_posture = db.session.query(db.func.avg(PostureAnalysis.posture_score))\
        .filter_by(user_id=current_user.id, status='completed')\
        .scalar() or 0
    
    avg_symmetry = db.session.query(db.func.avg(PostureAnalysis.symmetry_score))\
        .filter_by(user_id=current_user.id, status='completed')\
        .scalar() or 0
    
    return jsonify({
        'total_analyses': total_analyses,
        'completed_analyses': completed_analyses,
        'avg_posture': float(avg_posture),
        'avg_symmetry': float(avg_symmetry)
    })
