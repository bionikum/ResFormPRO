import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, List
from datetime import datetime
import base64

class PoseAnalyzer:
    """Упрощенный анализатор осанки для тестирования"""
    
    def __init__(self):
        try:
            self.mp_pose = mp.solutions.pose
            self.mp_drawing = mp.solutions.drawing_utils
            self.pose = self.mp_pose.Pose(
                static_image_mode=True,
                model_complexity=1,
                min_detection_confidence=0.5
            )
            self.initialized = True
        except Exception as e:
            print(f"Ошибка инициализации MediaPipe: {e}")
            self.initialized = False
    
    def analyze_image(self, image_path: str, view_type: str) -> Dict:
        """
        Анализ одного изображения
        """
        if not self.initialized:
            return {"error": "AI модуль не инициализирован"}
        
        try:
            # Чтение изображения
            image = cv2.imread(image_path)
            if image is None:
                return {"error": f"Не удалось загрузить изображение: {image_path}"}
            
            # Конвертация цвета
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            
            # Детекция позы
            results = self.pose.process(image_rgb)
            
            if not results.pose_landmarks:
                return {
                    "success": False,
                    "message": "Не удалось определить позу на изображении",
                    "view_type": view_type
                }
            
            # Базовая информация
            h, w = image.shape[:2]
            landmarks_count = len(results.pose_landmarks.landmark)
            
            # Простой анализ в зависимости от ракурса
            analysis = self._simple_analysis(view_type, h, w)
            
            return {
                "success": True,
                "view_type": view_type,
                "image_dimensions": {"height": h, "width": w},
                "landmarks_detected": landmarks_count,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": f"Ошибка анализа: {str(e)}",
                "view_type": view_type
            }
    
    def _simple_analysis(self, view_type: str, height: int, width: int) -> Dict:
        """Простой анализ для тестирования"""
        if view_type == 'front':
            return {
                "symmetry": "проверка симметрии плеч",
                "posture": "оценка фронтальной осанки",
                "score": 85,
                "recommendations": ["Следить за симметрией плеч", "Упражнения на выравнивание"]
            }
        elif view_type == 'side':
            return {
                "curvature": "анализ изгиба позвоночника",
                "alignment": "проверка вертикального выравнивания",
                "score": 78,
                "recommendations": ["Укрепление мышц кора", "Растяжка грудного отдела"]
            }
        elif view_type == 'back':
            return {
                "symmetry": "симметрия лопаток",
                "pelvis": "уровень таза",
                "score": 82,
                "recommendations": ["Упражнения для спины", "Коррекция осанки"]
            }
        elif view_type == 'face':
            return {
                "symmetry": "симметрия лица",
                "alignment": "выравнивание головы",
                "score": 90,
                "recommendations": ["Упражнения для шеи", "Работа с осанкой головы"]
            }
        else:
            return {
                "score": 75,
                "message": "Базовый анализ завершен"
            }
    
    def generate_report(self, analyses: Dict[str, Dict]) -> Dict:
        """Генерация простого отчета"""
        issues = []
        total_score = 0
        count = 0
        
        for view_type, analysis in analyses.items():
            if analysis.get('success'):
                if 'analysis' in analysis and 'score' in analysis['analysis']:
                    total_score += analysis['analysis']['score']
                    count += 1
                if 'analysis' in analysis and 'recommendations' in analysis['analysis']:
                    issues.extend(analysis['analysis']['recommendations'])
        
        avg_score = total_score / count if count > 0 else 0
        
        return {
            'summary': {
                'average_score': round(avg_score, 1),
                'views_analyzed': count,
                'total_issues': len(set(issues))
            },
            'recommendations': list(set(issues))[:3],  # Уникальные рекомендации
            'timestamp': datetime.now().isoformat()
        }
