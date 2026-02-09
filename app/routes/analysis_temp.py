from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app import db
from app.models import PostureAnalysis

analysis_bp = Blueprint('analysis', __name__)

# Конфигурация загрузки файлов
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@analysis_bp.route('/upload-test', methods=['POST'])
def upload_images_test():
    """Тестовая загрузка фотографий без авторизации"""
    try:
        # Используем фиксированного пользователя для теста
        user_id = 1  # ID администратора
        
        # Создание папки
        user_folder = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            str(user_id),
            datetime.now().strftime('%Y%m%d_%H%M%S')
        )
        os.makedirs(user_folder, exist_ok=True)
        
        # Ожидаемые ракурсы
        views = ['front', 'side', 'back', 'face']
        uploaded_files = {}
        
        # Обработка каждого файла
        for view in views:
            file_key = f'{view}_image'
            
            if file_key not in request.files:
                return jsonify({'error': f'Отсутствует фото: {view}'}), 400
            
            file = request.files[file_key]
            
            if file.filename == '':
                return jsonify({'error': f'Не выбрано фото для: {view}'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({'error': f'Недопустимый формат файла для: {view}'}), 400
            
            # Сохранение файла
            filename = secure_filename(f"{view}_{file.filename}")
            filepath = os.path.join(user_folder, filename)
            file.save(filepath)
            
            uploaded_files[view] = filepath
        
        # Создание записи в БД
        analysis = PostureAnalysis(
            user_id=user_id,
            front_image=uploaded_files.get('front'),
            side_image=uploaded_files.get('side'),
            back_image=uploaded_files.get('back'),
            face_image=uploaded_files.get('face'),
            analysis_date=datetime.utcnow(),
            overall_score=75.0,
            is_completed=True
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        # Тестовые результаты
        test_results = {
            'summary': {'average_score': 80, 'views_analyzed': 4},
            'recommendations': ['Упражнения для осанки', 'Растяжка грудного отдела'],
            'status': 'completed'
        }
        
        analysis.set_analysis_results(test_results)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Фотографии загружены. Анализ завершен.',
            'analysis_id': analysis.id,
            'results': test_results
        })
        
    except Exception as e:
        current_app.logger.error(f'Ошибка загрузки: {str(e)}')
        return jsonify({'error': 'Внутренняя ошибка сервера', 'details': str(e)}), 500

@analysis_bp.route('/test')
def test_endpoint():
    return jsonify({'status': 'success', 'message': 'Analysis module is working'})
