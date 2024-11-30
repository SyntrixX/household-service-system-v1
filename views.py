from flask import Blueprint, jsonify, request
from models import Service, Booking, User, db
from flask_login import login_required, current_user

# Remove the API blueprint definition
# api = Blueprint('api', __name__)

# Remove the API routes
# @api.route('/api/services', methods=['GET'])
# @login_required
# def get_services():
#     services = Service.query.all()
#     services_list = [{
#         'id': service.id,
#         'name': service.name,
#         'price': service.price
#     } for service in services]
#     return jsonify({'services': services_list})

# @api.route('/api/service_history', methods=['GET'])
# @login_required
# def get_service_history():
#     bookings = Booking.query.filter_by(customer_id=current_user.id).all()
#     history_list = [{
#         'id': booking.service.id,
#         'name': booking.service.name,
#         'rating': booking.service.rating,
#         'price': booking.service.price
#     } for booking in bookings]
#     return jsonify({'history': history_list})

# @api.route('/api/book_service/<int:service_id>', methods=['POST'])
# @login_required
# def book_service(service_id):
#     booking = Booking(service_id=service_id, customer_id=current_user.id)
#     db.session.add(booking)
#     db.session.commit()
#     service = Service.query.get(service_id)
#     return jsonify({'success': True, 'service': {
#         'id': service.id,
#         'name': service.name,
#         'rating': service.rating,
#         'price': service.price
#     }})

# @api.route('/api/users', methods=['GET'])
# @login_required
# def get_users():
#     users = User.query.all()
#     users_list = [{
#         'id': user.id,
#         'name': user.name,
#         'email': user.email,
#         'role': user.role
#     } for user in users]
#     return jsonify({'users': users_list})

# @api.route('/api/services', methods=['POST'])
# @login_required
# def create_service():
#     data = request.get_json()
#     new_service = Service(
#         name=data['name'],
#         description=data['description'],
#         category=data['category'],
#         location=data['location'],
#         professional_id=data['professional_id'],
#         customer_id=data['customer_id'],
#         status=data['status'],
#         rating=data['rating'],
#         price=data['price']
#     )
#     db.session.add(new_service)
#     db.session.commit()
#     return jsonify({'success': True, 'service': {
#         'id': new_service.id,
#         'name': new_service.name,
#         'description': new_service.description,
#         'category': new_service.category,
#         'location': new_service.location,
#         'professional_id': new_service.professional_id,
#         'customer_id': new_service.customer_id,
#         'status': new_service.status,
#         'rating': new_service.rating,
#         'price': new_service.price
#     }})

# @api.route('/api/services/<int:service_id>', methods=['PUT'])
# @login_required
# def update_service(service_id):
#     data = request.get_json()
#     service = Service.query.get(service_id)
#     if not service:
#         return jsonify({'success': False, 'message': 'Service not found'}), 404

#     service.name = data['name']
#     service.description = data['description']
#     service.category = data['category']
#     service.location = data['location']
#     service.professional_id = data['professional_id']
#     service.customer_id = data['customer_id']
#     service.status = data['status']
#     service.rating = data['rating']
#     service.price = data['price']

#     db.session.commit()
#     return jsonify({'success': True, 'service': {
#         'id': service.id,
#         'name': service.name,
#         'description': service.description,
#         'category': service.category,
#         'location': service.location,
#         'professional_id': service.professional_id,
#         'customer_id': service.customer_id,
#         'status': service.status,
#         'rating': service.rating,
#         'price': service.price
#     }})

# @api.route('/api/services/<int:service_id>', methods=['DELETE'])
# @login_required
# def delete_service(service_id):
#     service = Service.query.get(service_id)
#     if not service:
#         return jsonify({'success': False, 'message': 'Service not found'}), 404

#     db.session.delete(service)
#     db.session.commit()
#     return jsonify({'success': True, 'message': 'Service deleted successfully'})
