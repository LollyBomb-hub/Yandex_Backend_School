from flask import make_response
from datetime import *

#local imports
from . import db
from . import components


def create_couriers(data):
	if 'data' not in data.keys():
		return False
	if not isinstance(data['data'], list):
		return False
	couriers = data['data']
	for courier in couriers:
		if not isinstance(courier, dict):
			return False
		if 'courier_id' not in courier.keys():
			return False
		if 'courier_type' not in courier.keys():
			return False
		if 'regions' not in courier.keys():
			return False
		if 'working_hours' not in courier.keys():
			return False
		courier_id = courier['courier_id']
		if Courier.query.get(courier_id):
			return False # Attempt to rewrite data.
		courier_type = courier['courier_type']
		courier_regions = courier['regions']
		courier_hours = courier['working_hours']
		c = Courier( \
				courier_id, \
				courier_type, \
				courier_regions, \
				courier_hours \
			)
		db.session.add(c)
		db.session.commit()
	return True

def create_orders(data):
	if 'data' not in data.keys():
		return False
	if not isinstance(data['data'], list):
		return False
	orders = data['data']
	for order in orders:
		if not isinstance(order, dict):
			return False
		if 'order_id' not in order.keys():
			return False
		if 'weight' not in order.keys():
			return False
		if 'region' not in order.keys():
			return False
		if 'delivery_hours' not in order.keys():
			return False
		order_id 	= order['order_id']
		if Order.query.get(order_id):
			return False
		order_weight 	= order['weight']
		order_region 	= order['region']
		order_time 	= order['delivery_hours']
		db.session.add( \
				Order( \
					id = order_id, \
					weight = order_weight, \
					region = order_region, \
					time = order_time \
					) \
				)
		db.session.commit()
	return True

def assign_order(data):
	if not isinstance(data, dict):
		return False
	if 'courier_id' not in data.keys():
		return False
	courier_id = data['courier_id']
	courier = Courier.query.get_or_404(courier_id)
	'''
		Task is to find matching by time and region order
	'''
	possible_orders = db.session.query(OrdersInRegion).\
			join(CourierInRegion, CourierInRegion.region_id == OrdersInRegion.region_id).\
			join(OrdersInTimeInterval, OrdersInTimeInterval.order_id == OrdersInRegion.order_id).\
			all()
	hours = [i.time_id for i in CouriersInTimeInterval.query.filter(CourierInTimeInterval.courier_id == courier_id).all()]
	hours = [TimeIntervals.query.get(i).first for i in hours]
	for possible_order in possible_orders:
		time_interval = TimeIntervals.query.get(possible_order.time_id).first()
		time_0, time_1 = time_interval.border_left, time_interval.border_right
		for timelapse in hours:
			timelapse_0, timelapse_1 = timelapse.border_left, timelapse.border_right
			if time_0 > timelapse_0 and time_1 < timelapse_1:
				possible_order.courier_id = courier_id
				possible_order.start_serving = datetime.today()
				db.session.commit()
				return ( \
					{'orders': \
						Orders.query.all(), \
					'assign_time': \
						possible_order.start_serving.isoformat() + 'Z'} \
				)
	return False

def mark_order_as_complete(data):
	if not isinstance(data, dict):
		return False
	if 'courier_id' not in data.keys():
		return False
	if 'order_id' not in data.keys():
		return False
	if 'complete_time' not in data.keys():
		return False
	time = data['complete_time']
	courier = Courier.query.get(data['courier_id'])
	order = Orders.query.get(data['order_id'])
	started = order.start_serving
	courier.rating = AppConfiguration.calculate_rating(time - started, courier)
	courier.earnings_all_time += AppConfiguration.COST_PER_ONE
	courier.count_solved += 1
	order = Orders.query.get(data['order_id'])
	order.complete = 1
	order.ended_serving = time
	db.session.commit()
	return True

def make_server_response(text, code=200):
	response = make_response((str(text), code))
	response.headers['Content-Type'] = 'application/json'
	response.headers['Server'] = 'Yo & Yandex'
	return response

