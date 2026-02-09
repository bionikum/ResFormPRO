"""
API routes
"""

from flask import Blueprint, jsonify

api_bp = Blueprint('api', __name__)

@api_bp.route('/test')
def test():
    return jsonify({'message': 'API is working'})

@api_bp.route('/health')
def health():
    return jsonify({'status': 'ok'})
