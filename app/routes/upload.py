from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app.models import PostureAnalysis
from app import db

bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload')
@login_required
def upload_photos():
    return render_template('upload/upload.html')

@bp.route('/upload', methods=['POST'])
@login_required
def upload_photos_post():
    if 'body_front' not in request.files:
        flash('Не выбраны файлы для загрузки', 'danger')
        return redirect(request.url)
    
    files = request.files.getlist('body_front')
    
    # Создаем запись анализа
    analysis = PostureAnalysis(
        user_id=current_user.id,
        status='pending'
    )
    
    db.session.add(analysis)
    db.session.commit()
    
    # Сохраняем файлы
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{analysis.id}_{file.filename}")
            file.save(os.path.join(upload_folder, filename))
    
    flash('Фотографии успешно загружены! Анализ начат.', 'success')
    return redirect(url_for('main.dashboard'))
