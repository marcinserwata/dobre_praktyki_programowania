from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.environ.get('DATABASE_PATH', os.path.join(base_dir, 'results.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class AnalysisResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=False)
    people_count = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'image_url': self.image_url,
            'people_count': self.people_count,
            'created_at': self.created_at.isoformat()
        }


with app.app_context():
    db.create_all()


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/results', methods=['POST'])
def save_result():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Brak danych'}), 400
    
    if 'image_url' not in data or 'people_count' not in data:
        return jsonify({'error': 'Brakuje wymaganych pól: image_url i people_count'}), 400
    
    result = AnalysisResult(
        image_url=data['image_url'],
        people_count=data['people_count']
    )
    
    db.session.add(result)
    db.session.commit()
    
    return jsonify(result.to_dict()), 201


@app.route('/results', methods=['GET'])
def get_results():
    results = AnalysisResult.query.all()
    return jsonify([r.to_dict() for r in results])


@app.route('/results/<int:result_id>', methods=['GET'])
def get_result(result_id):
    result = AnalysisResult.query.get(result_id)
    if not result:
        return jsonify({'error': 'Nie znaleziono wyniku'}), 404
    return jsonify(result.to_dict())


@app.route('/results/<int:result_id>', methods=['DELETE'])
def delete_result(result_id):
    result = AnalysisResult.query.get(result_id)
    if not result:
        return jsonify({'error': 'Nie znaleziono wyniku'}), 404
    
    db.session.delete(result)
    db.session.commit()
    
    return jsonify({'message': 'Usunięto'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
