from datetime import time
from math import pi, e

from .components import Courier


class AppConfiguration:

	COST_PER_ONE 		= 200					# Assuming this is equivalent to real money(No matter)
	DEFAULT_TIME_OF_SERVING = time(hour=0, minute=30, second=0)	# Assuming this is in minutes
	TARGET_TIME_OF_SERVING	= time(hour=0, minute=20, second=0)	# This is the best time

	@classmethod
	def __rn(cls, t, tx, rnb, c):
		v = (((rnb*c)/(c+1))**2 + (tx.ctime()/t.ctime())**2)
		if tx == cls.DEFAULT_TIME_OF_SERVING:
			return pi/v
		return 2*pi/v

	@classmethod
	def calculate_rating(cls, time_of_delivery, courier):
		if not isinstance(time_of_delivery, time):
			return -1
		if not isinstance(courier, Courier):
			return -1
		served = courier.count_solved
		rating = courier.rating
		minus_before = courier.minus_before
		if time_of_delivery > cls.DEFAULT_TIME_OF_SERVING:
			edit = cls.__rn(time_of_delivery, cls.DEFAULT_TIME_OF_SERVING, rating, served)
			edit += (minus_before + 1)/e
			courier.minus_before += 1
			db.session.commit()
			if rating > edit:
				rating -= edit
			else:
				rating = 0
		elif time_of_delivery < cls.TARGET_TIME_OF_SERVING:
			edit = cls.__rn(time_of_delivery, cls.TARGET_TIME_OF_SERVING, rating, served)
			courier.minus_before = 0
			db.session.commit()
			if rating < 5 - edit:
				rating += edit
			elif rating > 5 - edit:
				rating = 5
		else:
			edit = cls.__rn(time_of_delivery, cls.DEFAULT_TIME_OF_SERVING, rating, served)
			if rating < 5 - edit:
				rating += edit
			elif rating > 5 - edit:
				rating = 5
		return rating
