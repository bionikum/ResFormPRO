from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import User, PostureAnalysis, Recommendation
from app import db
from app.forms import RecommendationForm

bp = Blueprint('specialist', __name__, url_prefix='/specialist')

@bp.route('/')
@login_required
def panel():
    # Проверяем, что пользователь - специалист
    if current_user.role != 'specialist' and current_user.role != 'admin':
        flash('Доступ запрещен. Требуются права специалиста.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Получаем статистику
    total_users = User.query.count()
    total_analyses = PostureAnalysis.query.count()
    pending_analyses = PostureAnalysis.query.filter_by(status='pending').count()
    
    # Последние анализы
    recent_analyses = PostureAnalysis.query.order_by(PostureAnalysis.created_at.desc()).limit(5).all()
    
    return render_template('specialist/panel.html',
                         total_users=total_users,
                         total_analyses=total_analyses,
                         pending_analyses=pending_analyses,
                         recent_analyses=recent_analyses)

@bp.route('/analyses')
@login_required
def analyses():
    if current_user.role != 'specialist' and current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    
    # Получаем все анализы
    all_analyses = PostureAnalysis.query.order_by(PostureAnalysis.created_at.desc()).all()
    
    return render_template('specialist/analyses.html', analyses=all_analyses)

@bp.route('/analysis/<int:analysis_id>')
@login_required
def view_analysis(analysis_id):
    if current_user.role != 'specialist' and current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    
    analysis = PostureAnalysis.query.get_or_404(analysis_id)
    user = User.query.get(analysis.user_id)
    
    return render_template('specialist/analysis_detail.html', 
                         analysis=analysis, 
                         user=user)

@bp.route('/recommendations', methods=['GET', 'POST'])
@login_required
def recommendations():
    if current_user.role != 'specialist' and current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    
    form = RecommendationForm()
    
    if form.validate_on_submit():
        recommendation = Recommendation(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            difficulty=form.difficulty.data,
            created_by=current_user.id
        )
        
        db.session.add(recommendation)
        db.session.commit()
        
        flash('Рекомендация успешно добавлена!', 'success')
        return redirect(url_for('specialist.recommendations'))
    
    # Получаем все рекомендации
    all_recommendations = Recommendation.query.order_by(Recommendation.created_at.desc()).all()
    
    return render_template('specialist/recommendations.html', 
                         form=form, 
                         recommendations=all_recommendations)

@bp.route('/users')
@login_required
def users():
    if current_user.role != 'specialist' and current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    
    all_users = User.query.order_by(User.date_created.desc()).all()
    
    return render_template('specialist/users.html', users=all_users)

@bp.route('/api/add_recommendation', methods=['POST'])
@login_required
def add_recommendation():
    if current_user.role != 'specialist' and current_user.role != 'admin':
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    data = request.json
    
    recommendation = Recommendation(
        title=data.get('title'),
        description=data.get('description'),
        category=data.get('category', 'general'),
        difficulty=data.get('difficulty', 'beginner'),
        created_by=current_user.id
    )
    
    db.session.add(recommendation)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Рекомендация добавлена',
        'id': recommendation.id
    })
