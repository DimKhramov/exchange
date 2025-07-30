from flask import Flask, render_template, request, jsonify
from database import get_db
from models import APIKey
import secrets
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/api-key', methods=['POST'])
def generate_api_key():
    if request.method == 'POST':
        db = get_db()
        try:
            # Создаем новый API ключ
            new_key = APIKey(
                key=secrets.token_urlsafe(32),
                created_at=datetime.now(),
                requests_limit=1000,  # Лимит запросов
                active=True
            )
            db.add(new_key)
            db.commit()
            
            return jsonify({
                'success': True,
                'api_key': new_key.key,
                'limit': new_key.requests_limit,
                'created_at': new_key.created_at.isoformat()
            })
        except Exception as e:
            db.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
        finally:
            db.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
