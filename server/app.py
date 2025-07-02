from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at.asc()).all()
        return make_response([message.to_dict() for message in messages], 200)
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            message = Message(
                body=data['body'],
                username=data['username']
            )
            db.session.add(message)
            db.session.commit()
            return make_response(message.to_dict(), 201)
        except (KeyError, TypeError):
            return make_response({'error': 'body and username are required.'}, 400)

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()
 
    if not message:
        return make_response({'error': 'Message not found'}, 404)
 
    if request.method == 'PATCH':
        data = request.get_json()
        # The README specifies only updating the body
        message.body = data.get('body', message.body)
 
        db.session.add(message)
        db.session.commit()
 
        return make_response(message.to_dict(), 200)
 
    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        # A 204 No Content response is standard for a successful DELETE
        return make_response('', 204)
