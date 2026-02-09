from flask import Blueprint, render_template

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/analysis')
def index():
    return render_template('analysis/index.html', message="Раздел в разработке")
