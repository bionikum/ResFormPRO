from flask import Blueprint, render_template

subscription_bp = Blueprint('subscription', __name__)

@subscription_bp.route('/subscription')
def index():
    return render_template('subscription/index.html', message="Раздел в разработке")
