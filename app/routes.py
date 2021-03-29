from flask import request, jsonify
from . import app, db
from .components import *
from .functions import *


@app.route('/couriers', methods = ['POST'])
def couriers():
	data = request.get_json()
	if create_couriers(data):
		return make_server_response( \
						{ \
							'couriers': \
								Courier.query.all() \
						}, 201 \
					)
	return make_server_response( \
					{ \
						'couriers': \
							Courier.query.all() \
						}, 400 \
				)


@app.route('/couriers/<int:id>', methods = ['GET', 'PATCH'])
def couriers_id(id):
	if request.method == 'GET':
		return make_server_response(Courier.query.get_or_404(id).get_method(), 200)
	else:
		data = request.get_json()
		c = Courier.query.get_or_404(id)
		if c.update(data):
			return make_server_response(c.get_method(), 200)
		return make_server_response('', 400)


@app.route('/orders', methods = ['POST'])
def orders():
	data = request.get_json()
	if create_orders(data):
		return make_server_response( \
						{ \
							'orders': \
								Orders.query.all() \
						}, 201 \
					)
	return make_server_response( \
					{ \
						'orders': \
							Orders.query.all() \
					}, 400 \
				)


@app.route('/orders/assign', methods = ['POST'])
def assign_order():
	data = request.get_json()
	ans = assign_order(data)
	if isinstance(ans, tuple):
		return make_server_response(ans[0],200)
	return make_server_response('', 400)


@app.route('/orders/complete', methods = ['POST'])
def complete_order():
	data = request.get_json()
	if mark_order_as_complete(data):
		return 200
	return make_server_response('', 400)

