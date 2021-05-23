from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy import func, asc, desc
#from sqlalchemy.sql import func
from sqlalchemy import *


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class ExpensesModel(db.Model):
	month = db.Column(db.Integer, primary_key=True, nullable=False)
	day = db.Column(db.Integer, primary_key=True, nullable=False)
	rent = db.Column(db.Integer, default=0)
	utilities = db.Column(db.Integer, default=0)
	groceries = db.Column(db.Integer, default=0)
	other = db.Column(db.Integer, default=0)


	def __repr__(self):
		return f"Expenses(month = {month},day = {day}, rent = {rent}, utilities = {utilities}, groceries = {groceries}, other = {other})"

# initialize it for only once
# db.create_()

expenses_args = reqparse.RequestParser() 
expenses_args.add_argument("rent", type=int)
expenses_args.add_argument("utilities", type=int)
expenses_args.add_argument("groceries", type=int)
expenses_args.add_argument("other", type=int)


resource_fields = {
	'month': fields.Integer,
	'day': fields.Integer,
	'rent': fields.Integer,
	'utilities': fields.Integer,
	'groceries': fields.Integer,
	'other':fields.Integer,
}

# This function check if the given month and day is a valid date in 2021
def date_valid_2021(month, day):
	if month <= 0 or month > 12 or day <= 0:
		return False
	thirty = [4,6,9,11]
	thirty_one = [1,3,5,7,8,10,12]
	if month == 2 and day > 28:
		return False
	elif month in thirty and day > 30:
		return False
	elif month in thirty_one and day > 31:
		return False
	return True


# we use this class to add, get, modify and delete expenses of a given date(month/day)
class Expenses(Resource):
	@marshal_with(resource_fields)
	def get(self, expenses_month, expenses_day):
		if not date_valid_2021(expenses_month, expenses_day):
			abort(404, message="The given date is invalid")
		result = ExpensesModel.query.filter_by(month=expenses_month,day=expenses_day).first()
		if not result:
			abort(404, message="Could not find the expenses of the given date")
		return result

	@marshal_with(resource_fields)
	def put(self, expenses_month, expenses_day):
		if not date_valid_2021(expenses_month, expenses_day):
			abort(404, message="The given date is invalid")
		args = expenses_args.parse_args()
		result = ExpensesModel.query.filter_by(month=expenses_month,day=expenses_day).first()
		if result:
			abort(409, message="Expenses of the date has already been initialized")

		expenses = ExpensesModel(month=expenses_month, day=expenses_day, rent=args['rent'], utilities=args['utilities'], groceries=args['groceries'],other=args['other'])
		db.session.add(expenses)
		db.session.commit()
		return expenses, 201

	@marshal_with(resource_fields)
	def patch(self, expenses_month, expenses_day):
		if not date_valid_2021(expenses_month, expenses_day):
			abort(404, message="The given date is invalid")
		args = expenses_args.parse_args()
		result = ExpensesModel.query.filter_by(month=expenses_month,day=expenses_day).first()
		if not result:
			abort(404, message="Expenses of the date doesn't exist, cannot update. Please create it first")

		if args['rent']:
			result.rent = args['rent']
		if args['utilities']:
			result.utilities = args['utilities']
		if args['groceries']:
			result.groceries = args['groceries']
		if args['other']:
			result.other = args['other']

		db.session.commit()

		return result


	def delete(self, expenses_month, expenses_day):
		if not date_valid_2021(expenses_month, expenses_day):
			abort(404, message="The given date is invalid")
		result = ExpensesModel.query.filter_by(month=expenses_month,day=expenses_day).first()
		if not result:
			abort(404, message="Expenses of the date doesn't exist, cannot delete")

	
		db.session.delete(result)
		db.session.commit()
		return '', 204

# we use this class to get the sum of a certain expense in a given month
class Sum_month_type(Resource):
	def get(self, mon, type):
		if mon <=0 or mon > 12:
			abort(404, message="The given month is invalid")
		if type == "rent":
			result = db.session.query(func.sum(ExpensesModel.rent)).filter(ExpensesModel.month==mon).scalar()
		elif type == "utilities":
			result = db.session.query(func.sum(ExpensesModel.utilities)).filter(ExpensesModel.month==mon).scalar()
		elif type == "groceries":
			result = db.session.query(func.sum(ExpensesModel.groceries)).filter(ExpensesModel.month==mon).scalar()
		elif type == "other":
			result = db.session.query(func.sum(ExpensesModel.other)).filter(ExpensesModel.month==mon).scalar()
		if not result:
			result = 0
		return result

# we use this class to get the sum of the expense in a given date
class Sum_of_a_day(Resource):
	def get(self, expenses_month, expenses_day):
		if not date_valid_2021(expenses_month, expenses_day):
			abort(404, message="The given date is invalid")
		result = ExpensesModel.query.filter_by(month=expenses_month,day=expenses_day).first()
		if not result:
			abort(404, message="Could not find the expenses of the given date")
		total = result.rent + result.utilities + result.groceries + result.other
		return total

# we use this class to get the sum of the expense in a given month
class Sum_of_a_month(Resource):
	def get(self, mon):
		if mon <= 0 or mon > 12:
			abort(404, message="The given month is invalid")
		result = ExpensesModel.query.filter_by(month=mon)
		if not result:
			abort(404, message="Could not find the expenses of the given month")
		total = 0
		for item in result:
			total += item.rent + item.utilities + item.groceries + item.other
		return total




# we use this class to get the maximum of a certain expense in a given month
class Max_month_type(Resource):
	def get(self, mon, type): 
		if mon <=0 or mon > 12:
			abort(404, message="The given month is invalid")
		if type == "rent":
			result = ExpensesModel.query.filter_by(month=mon).order_by(desc(ExpensesModel.rent)).first()
			return result.rent
		elif type == "utilities":
			result = ExpensesModel.query.filter_by(month=mon).order_by(desc(ExpensesModel.utilities)).first()
			return result.utilities
		elif type == "groceries":
			#result = db.session.query(func.max(ExpensesModel.groceries)).select_from(ExpensesModel).filter(ExpensesModel.month==mon)
			result = ExpensesModel.query.filter_by(month=mon).order_by(desc(ExpensesModel.groceries)).first()
			return result.groceries
		elif type == "other":
			result = ExpensesModel.query.filter_by(month=mon).order_by(desc(ExpensesModel.other)).first()
			return result.other
		if not result:
			return 0



api.add_resource(Expenses, "/expenses/<int:expenses_month>/<int:expenses_day>")
api.add_resource(Max_month_type, "/max/<int:mon>/<string:type>")
api.add_resource(Sum_month_type, "/sum_of_a_type/<int:mon>/<string:type>")
api.add_resource(Sum_of_a_day, "/sum_of_a_day//<int:expenses_month>/<int:expenses_day>")
api.add_resource(Sum_of_a_month, "/sum_of_a_month/<int:mon>")

if __name__ == "__main__":
	app.run(debug=True)
