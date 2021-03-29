from datetime import time


from . import db
from .functions import calculate_rating


class Courier(db.Model):

	id = db.Column(db.Integer, primary_key=True)
	type = db.Column(db.Integer)
	regions = db.Column(db.Text)
	working_hours = db.Column(db.Text)
	count_solved = db.Column(db.Integer, default=0)
	rating = db.Column(db.Integer, default=0)
	minus_before = db.Column(db.Integer, default=0)
	earnings_all_time = db.Column(db.Integer, default=0)
	couriers_in_region = db.relationship('CouriersInRegion', backref='courier', lazy='dynamic')
	courier_in_time = db.relationship('CourierInTimeInterval', backref='courier', lazy='dynamic')

	def __init__(self, id, type, regions, hours):
		if not isinstance(regions, list):
			return None
		if not isinstance(hours, list):
			return None
		self.id 		= id
		if not Type.query.filter(Type.type == type).first():
			db.session.add(Type(type))
			db.session.commit()
		self.type		= Type.query.filter(Type.type == type).first().id
		self.regions 		= ','.join(list(map(str, regions)))
		self.working_hours 	= ','.join(hours)
		'''
			Assuming working ours is an array of such type:
			[!Hint]:
				* Same is right for Orders->Delivery_time
			%hh:%mm-%hh-%mm
			E.g.:
			[
				12:00-15:00,
				16:00-20:00
			]
			[!ToDo]:
				* Make more 'convenient' time system
		'''
		for timelapse in hours:
			timelapse_array = timelapse.split('-')
			time_0 = time(timelapse_array[0], '%H:%M').time()
			time_1 = time(timelapse_array[1], '%H:%M').time()
			if not TimeIntervals.query.filter(TimeIntervals.border_left == time_0).\
						filter(TimeIntervals.border_right == time_1):
				db.session.add( \
					TimeIntervals( \
						time_0, \
						time_1 \
						)
				)
				db.session.commit()
			db.session.add( \
					CourierInTimeInterval( \
						self,
						TimeIntervals.query.filter(TimeIntervals.border_left == time_0).\
									filter(TimeIntervals.border_right == time_1) \
						)
				)
			db.session.commit()
		for region in regions:
			if not Regions.query.filter(Regions.region_code == region).first():
				db.session.add(Regions(region))
				db.session.commit()
			db.session.add( \
				CouriersInRegion(self, Regions.query.filter(Regions.region_code == region).first()) \
			)
			db.session.commit()

	def __repr__(self):
		return str(self.id)

	def check(self, key):
		if key in ['courier_id', 'courier_type', 'regions', 'working_hours']:
			return True
		return False

	def get_method(self):
		result 			= {}
		result['courier_id'] 	= self.id
		result['courier_type'] 	= self.type
		result['regions'] 	= self.regions.split(',')
		result['working_hours'] = self.working_hours.split(',')
		result['rating'] 	= self.rating
		result['earnings'] 	= self.count_solved * COST_PER_ONE
		return result

	def update(self, data):
		if not isinstance(data, dict):
			return False
		for key in data.keys():
			if key == 'courier_type':
				self.type = Type.query.filter(Type.type == data['courier_type']).first()
			if key == 'regions':
				new_regions = data['regions']
				if not isinstance(new_regions, list):
					continue
				regions = self.regions.split(',')
				if regions == new_regions:
					continue
				for region in regions:
					db.session.delete( \
						CourierInRegions.query.filter( \
							CourierInRegions.courier_id == self.id \
						) \
					)
				db.session.commit()
				for region in new_regions:
					db.session.add( \
						CourierInRegions( \
							self, \
							Regions.query.filter(Regions.region_code == region).first() \
						) \
					)
				self.regions = ','.join(list(map(str, data['regions'])))
			if key == 'working_hours':
				for timelapse in self.working_hours.split(','):
					timelapse_array = timelapse.split('-')
					time_0 = time(timelapse_array[0], '%H:%M').time()
					time_1 = time(timelapse_array[1], '%H:%M').time()
					db.session.delete( \
						CourierInTimeInterval.query.filter(
							CourierInTimeInterval.time_id == \
							TimeIntervals.query.filter(TimeIntervals.border_left == time_0).\
								filter(TimeIntervals.border_right == time_1).id \
						)
                                	)
					db.session.commit()
				for timelapse in data['working_hours']:
					timelapse_array = timelapse.split('-')
					time_0 = time(timelapse_array[0], '%H:%M').time()
					time_1 = time(timelapse_array[1], '%H:%M').time()
					if not TimeIntervals.query.filter(TimeIntervals.border_left == time_0).\
							filter(TimeIntervals.border_right == time_1):
						db.session.add( \
							TimeIntervals( \
								time_0, \
								time_1 \
							) \
						)
						db.session.commit()
					db.session.add( \
						CourierInTimeInterval( \
							self,
							TimeIntervals.query.filter(TimeIntervals.border_left == time_0).\
                                                                        filter(TimeIntervals.border_right == time_1) \
                                                	) \
                                		)
					db.session.commit()
				self.working_hours = ','.join(data['working_hours'])
		db.session.commit()
		return True


class Orders(db.Model):

	id = db.Column(db.Integer, primary_key=True)
	complete = db.Column(db.Boolean, default=0)
	weight = db.Column(db.Float)
	region = db.Column(db.Integer)
	delivery_hours = db.Column(db.Text)
	courier_id = db.Column(db.Integer)
	start_serving = db.Column(db.DateTime)
	ended_serving = db.Column(db.DateTime)
	orders_in_region = db.relationship('OrdersInRegion',  backref='order', lazy='dynamic')
	orders_in_time = db.relationship('OrdersInTimeInterval', backref='order', lazy='dynamic')

	def __init__(self, order_id, weight, region, hours):
		self.id = order_id
		self.weight = weight
		if not Regions.query.filter(Regions.region_code == region):
			db.session.add(Regions(region))
			db.session.commit()
		self.region = Regions.query.filter(Regions.region_code == region).first().id
		self.delivery_hours = ','.join(hours)
		db.session.add( \
				OrdersInRegion( \
					self, \
					Regions.query.get(self.region) \
				)
			)
		for timelapse in hours:
			timelapse_array = timelapse.split('-')
			time_0 = time(timelapse_array[0], '%H:%M').time()
			time_1 = time(timelapse_array[1], '%H:%M').time()
			if not TimeIntervals.query.filter(TimeIntervals.border_left == time_0).\
						filter(TimeIntervals.border_right == time_1):
				db.session.add( \
					TimeIntervals( \
                                                time_0, \
                                                time_1 \
                                                )
                                )
				db.session.commit()
			db.session.add( \
				OrdersInTimeInterval( \
					self,
					TimeIntervals.query.filter(TimeIntervals.border_left == time_0).\
							filter(TimeIntervals.border_right == time_1) \
					) \
				)
		db.session.commit()

	def __repr__(self):
		return str(self.id)


class Type(db.Model):

	id = db.Column(db.Integer, primary_key=True)
	type = db.Column(db.String(128), index=True, unique=True)

	def __init__(self, type):
		self.type = type

	def __repr__(self):
		return str(self.id)

	def __str__(self):
		return str(self.id)


class Regions(db.Model):

	id = db.Column(db.Integer, primary_key=True)
	region_code = db.Column(db.Integer, unique=True)
	orders_in_region = db.relationship('OrdersInRegion', backref='regions', lazy='dynamic')
	couriers_in_region = db.relationship('CouriersInRegion', backref='regions', lazy='dynamic')

	def __init__(self, key):
		self.region_code = key

	def __repr__(self):
		return 'Region <{0}>'.format(str(self.region_code))


class TimeIntervals(db.Model):

	__tablename__ = 'timelapse'
	'''
		Table view(E.g.):
		id	Start	End
		0	10:00	12:00
		1	12:00	13:00
		2	14:00	14:30
			<-...->
			 |  |
			 |  |
			 |  |
			_|  |_
			\    /
			 \  /
			  \/
	'''

	id = db.Column(db.Integer, primary_key=True)
	border_left = db.Column(db.Time)
	border_right = db.Column(db.Time)
	orders_in_time = db.relationship('OrdersInTimeInterval', backref='time', lazy='dynamic')
	couriers_in_time = db.relationship('CouriersInTimeInterval', backref='time', lazy='dynamic')

	def __init__(self, time0, time1):
		self.border_left = time0
		self.border_right = time1

	def __repr__(self):
		return 'TimeLapse <{1} - {0}>'.format( \
								[ \
									str(self.before.strftime('%H:%M')), \
									str(self.before.hour.strftime('%H:%M')) \
								] \
							)


class OrdersInRegion(db.Model):

	id = db.Column(db.Integer, primary_key=True)
	order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
	region_id = db.Column(db.Integer, db.ForeignKey('regions.id'))

	def __init__(self, order, region):
		self.order = order
		self.regions = region


class OrdersInTimeInterval(db.Model):

	id = db.Column(db.Integer, primary_key=True)
	order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
	time_id = db.Column(db.Integer, db.ForeignKey('timelapse.id'))

	def __init__(self, order, time):
		self.order = order
		self.time = time


class CouriersInRegion(db.Model):

	id = db.Column(db.Integer, primary_key=True)
	courier_id = db.Column(db.Integer, db.ForeignKey('courier.id'))
	region_id = db.Column(db.Integer, db.ForeignKey('regions.id'))

	def __init__(self, courier, region):
		self.courier = courier
		self.regions = region


class CourierInTimeInterval(db.Model):

	id = db.Column(db.Integer, primary_key=True)
	courier_id = db.Column(db.Integer, db.ForeignKey('courier.id'))
	time_id = db.Column(db.Integer, db.ForeignKey('timelapse.id'))

	def __init__(self, courier, time):
		self.courier = courier
		self.time = time

