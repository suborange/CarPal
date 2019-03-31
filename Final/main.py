from flask import Flask, render_template, request, redirect

from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map

import smartcar

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import datetime

# TODO:

client = smartcar.AuthClient(
	client_id = '',
	client_secret = '',
	redirect_uri = 'http://localhost:5000/after-auth',
)

sheets_scope = ['https://spreadsheets.google.com/feeds',
         		'https://www.googleapis.com/auth/drive']
sheets_creds = ServiceAccountCredentials.from_json_keyfile_name('sheet_creds.json', sheets_scope)
gc = gspread.authorize(sheets_creds)
sht = gc.open_by_url('')

report_sheet = sht.get_worksheet(0)
smartcar_sheet = sht.get_worksheet(1)

app = Flask(__name__)

GoogleMaps(app, key="")

#@app.route('/location')
def get_location():
	# Pulls from sheet
	access_token = smartcar_sheet.acell('A2').value

	response = smartcar.get_vehicle_ids(access_token)

	vid = response['vehicles'][0]
	
	vehicle = smartcar.Vehicle(vid, access_token)

	location = vehicle.location()

	print(location)

	pos = [location['data']['latitude'], location['data']['longitude']]

	return pos

@app.route('/')
def index():
	list_of_lists = report_sheet.get_all_values()

	report_positions = []

	for row in list_of_lists:
		if row[0] ==  'drunk':
			row_dic = {
				'icon': 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
             	'lat': row[3],
             	'lng': row[4],
             	'infobox': "<b> License Plate:" + row[2] + "</b>"
			}
			report_positions.append(row_dic)
		elif row[0] == 'pothole':
			row_dic = {
				'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
             	'lat': row[3],
             	'lng': row[4],
             	'infobox': "<b> Lane:" + row[5] + "</b>"
			}
			report_positions.append(row_dic)

	mymap = Map(
	        identifier="view-side",
	        lat= 34.0699, # Center pos
	        lng= -118.4466,
	        markers= report_positions
	        #markers=[(latitude, longitude)]
	)

	return render_template('index.html', all=list_of_lists, mymap=mymap)


@app.route('/drunk', methods=['POST', 'GET'])
def drunk():
	if request.method == 'POST':
		location = get_location()
		empty_row = len(report_sheet.col_values(1)) + 1
		report_sheet.update_cell(empty_row, 1, 'drunk')
		report_sheet.update_cell(empty_row, 2, str(datetime.datetime.now()))
		report_sheet.update_cell(empty_row, 3, '')
		report_sheet.update_cell(empty_row, 4, location[0] + (int(request.form['mod']) / 7000))
		report_sheet.update_cell(empty_row, 5, location[1] + (int(request.form['mod']) / 7000))
		return redirect('/') 

	if request.method == 'GET':
		return render_template('drunk.html')

	#return 'You entered: {}, {}'.format(request.form['lat'], request.form['lng'])

@app.route('/pothole', methods=['POST'])
def pothole():
	location = get_location()
	empty_row = len(report_sheet.col_values(1)) + 1
	report_sheet.update_cell(empty_row, 1, 'pothole')
	report_sheet.update_cell(empty_row, 2, str(datetime.datetime.now()))
	report_sheet.update_cell(empty_row, 4, location[0] + (int(request.form['mod']) / 7000))
	report_sheet.update_cell(empty_row, 5, location[1] + (int(request.form['mod']) / 7000))
	report_sheet.update_cell(empty_row, 6, request.form['lane'])

	return redirect('/') 

@app.route('/sheets')
def get_sheet():
	values_list = report_sheet.row_values(1)

	return render_template('sheets.html', first_row=values_list)

@app.route('/get-auth')
def get_auth():
	auth_url = client.get_auth_url()
	print(auth_url)
	link = auth_url
	return render_template('get-auth.html', auth_link=link)

@app.route('/after-auth', methods=['GET'])
def after_auth():
	if request.method == 'GET':
		auth_code = request.args.get('code', None)
		access = client.exchange_code(auth_code)

		access_token = access['access_token']

		# Saves to sheet
		smartcar_sheet.update_acell('A2', access_token)

		print(access)
		response = smartcar.get_vehicle_ids(access_token)

		print(response)

		vid = response['vehicles'][0]

		print(vid)

		vehicle = smartcar.Vehicle(vid, access_token)

		location = vehicle.location()

		print(location)

		smartcar_authenticated = True

		latitude = location['data']['latitude']
		longitude = location['data']['longitude']

		mymap = Map(
		        identifier="view-side",
		        lat= latitude,
		        lng= longitude,
		        markers=[(latitude, longitude)]
		)

		return render_template('after_auth.html', code=auth_code, lat=latitude, lon=longitude, mymap=mymap)

if __name__ == "__main__":
	app.run()