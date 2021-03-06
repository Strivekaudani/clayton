
import cv2
import pytesseract
import numpy as np
# from picamera.array import PiRGBArray
# from picamera import PiCamera
from threading import Thread
from time import sleep
from os import system

from boom_gate import open_and_close
from utils import text_from_image, uuid, now
import constants
# from persistents import persistent_vc

module = {};
module['prev_plate'] = '';


def get_fee(car_type):

	if (car_type == 'family_car'):
		return constants.FAMILY_CAR_TOLL_FEE
	else:
		return constants.HEAVY_VEHICLE_TOLL_FEE;

def check_car_type(cars, number_plate):

	car_type = None;


	for car in cars:
		if (car.get('number_plate') == number_plate):
			car_type = car.get('car_type');
			break;

	return car_type;


def auto_scan(request, response, emit, mail, Message):

	try:

		vc = cv2.VideoCapture('http://localhost:5000/video-feed');

		while (True):
			ret, frame = vc.read();

			if (ret):
				image = np.array(frame)
				break

		text = text_from_image(image)

		if (len(text) == 0):
			response.set_json_body({
				'message': 'NO CAR DETECTED'
			});
			response.status = 404
			return response.render();

		# return if the plate is atill the same as last scanned
		prev_plate = request.args.get('prev_plate');

		if (prev_plate == text):

			response.status = 200;

			response.set_json_body({
				'message': 'Previous plate',
				'number_plate': text
			});

			return response.render();

	   # querying the database
		db = request.db;
		query = { "cars.number_plate": text }
		projection = { "funds": 1, "email": 1, 'cars': 1 }

		user = db.users.find_one(query, projection);

		if (user == None):

			message = 'Car not recognized'
			emit('notice', message , broadcast=True)
			emit('unrecognized_number_plate', text, broadcast=True);
			response.set_json_body({
				'message': message,
				'number_plate': text
			});
			response.status = 404;
			return response.render();

		# checking funds
		funds = user["funds"];
		car_type = check_car_type(user['cars'], text);
		fee = get_fee(car_type);

		if (funds < fee):

			message = 'The driver\'s account has insufficient funds. We have added a debit on their account, and added a penalty of 10%'
			emit('notice', message , broadcast=True);

			response.status = 400;
			fee = fee * 1.1

		response.set_json_body({
			'message': 'The driver\'s account has insufficient funds. We have added a debit on their account, and added a penalty of 10%',
			'number_plate': text
		});

		# deduct account
		funds = funds - fee;
		update = {
			"$set": {
				"funds": funds
			}
		}

		email = user["email"]
		query = { "email": email }

		db.users.update(query, update)

		# record transaction
		db.transactions.insert_one({
			'type': 'ACCOUNT_DEDUCTION',
			'amount': float(fee),
			'done_by': f'AUTO_SCAN',
			'time': now(),
			'notes': f'Car {text} paid a toll fee of ${fee}'
		});

		try:
			email_message = Message('We have debited your account', sender="Autogate <autogate@gmail.com>", recipients=[ email ]) 
			email_message.body = f'We have debited ${fee} from your account. New balance is ${funds}';
			mail.send(email_message);
		except:
			pass

		# open get
		open_and_close()
		return response.render();


	except Exception as e:
		print(str(e))
		response.set_json_body("Something went wrong. Please try again.");
		response.status = 500;
		return response.render();



def scan_plates(request, response):

	# authentication;
	user = request.user;

	if (user == None):
	    return response.redirect_302('/notice?message=You need to login to access this page.');

	is_not_admin = not user["is_admin"];

	if (is_not_admin):
	    return response.redirect_302('/notice?message=You are not authorized to access this page.');
	
	try:

		# capture frame
		vc = cv2.VideoCapture('http://localhost:5000/video-feed');

		while (True):
			ret, frame = vc.read();

			if (ret):
				image = np.array(frame)
				break

		text = text_from_image(image)

		if (len(text) == 0):
			response.set_json_body('NO CAR DETECTED')
			response.status = 404
			return response.render();

	   # querying the database
		db = request.db;
		query = { "cars.number_plate": text }
		projection = { "funds": 1, "email": 1, 'cars': 1 }

		user = db.users.find_one(query, projection);

		if (user == None):
			response.set_json_body('Car not recognized');
			response.status = 404;
			return response.render();

		# checking funds
		funds = user["funds"];
		car_type = check_car_type(user[cars], text);
		fee = get_fee(car_type);

		if (funds < fee):
			response.set_json_body('The driver\'s account has insufficient funds. We have added a debit on their account, and added a penalty of 10%');
			response.status = 400;
			fee = fee * 1.1

		# deduct account
		funds = funds - fee;
		update = {
			"$set": {
				"funds": funds
			}
		}

		email = user["email"]
		query = { "email": email }

		db.users.update(query, update)


		# record transaction
		db.transactions.insert_one({
			'type': 'ACCOUNT_DEDUCTION',
			'amount': float(fee),
			'done_by': f'MANUAL_SCAN',
			'time': now(),
			'notes': f'Car {text} paid a toll fee of ${fee}'
		});

		# open get
		open_and_close()
		return response.render();


	except Exception as e:
		print(str(e))
		response.set_json_body("Something went wrong. Please try again.");
		response.status = 500;
		return response.render();
				


