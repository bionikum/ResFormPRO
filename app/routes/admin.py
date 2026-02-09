from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import User, PostureAnalysis, Recommendation
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.before_request
def check_admin():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.url))
    
    # Проверяем что пользователь - администратор
    if not current_user.is_admin():
        flash('Доступ запрещен. Требуются права администратора.', 'danger')
        return redirect(url_for('main.dashboard'))

@bp.route('/')
@login_required
def admin_panel():
    # Статистика
    total_users = User.query.count()
    total_analyses = PostureAnalysis.query.count()
    pending_analyses = PostureAnalysis.query.filter_by(status='pending').count()
    
    # Новые пользователи за последние 7 дней
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    # Используем date_created или created_at
    new_users = User.query.filter(
        User.date_created >= week_ago if User.date_created is not None else User.created_at >= week_ago
    ).count()
    
    # Активность
    recent_analyses = PostureAnalysis.query.order_by(PostureAnalysis.created_at.desc()).limit(10).all()
    
    return render_template('admin/panel.html',
                         total_users=total_users,
                         total_analyses=total_analyses,
                         pending_analyses=pending_analyses,
                         new_users=new_users,
                         recent_analyses=recent_analyses)

@bp.route('/users')
@login_required
def manage_users():
    users = User.query.order_by(User.date_created.desc() if User.date_created is not None else User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@bp.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.role = request.form.get('role', user.role)
        user.first_name = request.form.get('first_name', user.first_name)
        user.last_name = request.form.get('last_name', user.last_name)
        
        new_password = request.form.get('password')
        if new_password:
            user.set_password(new_password)
        
        db.session.commit()
        flash('Пользователь обновлен', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/edit_user.html', user=user)

@bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Нельзя удалить самого себя
    if user.id == current_user.id:
        flash('Нельзя удалить свой аккаунт', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash('Пользователь удален', 'success')
    return redirect(url_for('admin.manage_users'))

@bp.route('/analyses')
@login_required
def manage_analyses():
    analyses = PostureAnalysis.query.order_by(PostureAnalysis.created_at.desc()).all()
    return render_template('admin/analyses.html', analyses=analyses)

@bp.route('/recommendations')
@login_required
def manage_recommendations():
    recommendations = Recommendation.query.order_by(Recommendation.created_at.desc()).all()
    return render_template('admin/recommendations.html', recommendations=recommendations)

@bp.route('/settings')
@login_required
def settings():
    return render_template('admin/settings.html')

@bp.route('/api/stats')
@login_required
def get_stats():
    # Статистика по дням за последние 30 дней
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Новые пользователи по дням
    user_stats = db.session.query(
        func.date(User.date_created if User.date_created is not None else User.created_at).label('date'),
        func.count(User.id).label('count')
    ).filter((User.date_created >= thirty_days_ago) if User.date_created is not None else (User.created_at >= thirty_days_ago))\
     .group_by(func.date(User.date_created if User.date_created is not None else User.created_at))\
     .order_by('date')\
     .all()
    
    # Анализы по дням
    analysis_stats = db.session.query(
        func.date(PostureAnalysis.created_at).label('date'),
        func.count(PostureAnalysis.id).label('count')
    ).filter(PostureAnalysis.created_at >= thirty_days_ago)\
     .group_by(func.date(PostureAnalysis.created_at))\
     .order_by('date')\
     .all()
    
    return jsonify({
        'users': [{'date': str(stat.date), 'count': stat.count} for stat in user_stats],
        'analyses': [{'date': str(stat.date), 'count': stat.count} for stat in analysis_stats]
    })
