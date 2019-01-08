import json
import traveltime
import weathertoday
import pushnotification
import spreadsheet
import datetime

with open('config.json') as config:
    config_data = json.load(config)     #open config json file


origin_coord = config_data["starting_point_coordinates"][0],config_data["starting_point_coordinates"][1]         #your origin coordinates
destination_coord = config_data["destination_point_coordinates"][0],config_data["destination_point_coordinates"][1]    #your destination
city = config_data["city"]

DarkSky_key = config_data["DarkSky_API_key"]
gmaps_key = config_data["google_maps_API_key"]
gsheets_key = config_data["google_sheets_API_key"]
gsheets_ID = config_data["google_sheet_ID"]
pushbullet_key = config_data["pushbullet_API_key"]


travel_time = traveltime.get_travel_time(origin_coord,destination_coord,gmaps_key)

print("Current travel time is:", travel_time)

sheet = spreadsheet.get_sheet(gsheets_key,gsheets_ID)

sheet_data = sheet.get_all_values() #get the updated sheet data
nr_of_rows = len(sheet_data)

current_hour = datetime.datetime.now().time().hour
current_min = datetime.datetime.now().time().minute

current_col_index = current_hour * 2 + 6     #4 is the offset for the first columns dedicated to the date and weather

if(current_min >= 30):
    current_col_index += 1                                      #if time is within second half of the hour, add one to the column index

print("Collon currently writing to:", current_col_index)
print("Row currently writing to:", nr_of_rows)

if(current_col_index == 6):
    date = datetime.datetime.now()  # current time
    formatted_date = date.strftime("%d.%m.%Y")
    day_of_week = date.strftime("%A")
    lat, long = traveltime.get_city_coordinates(city,gmaps_key)
    summary, high, low, precip_prob = weathertoday.weather_today(lat,long, DarkSky_key)
    new_row_data = formatted_date, day_of_week, str(low) + "/" + str(high), summary, str(precip_prob) + "%", travel_time
    sheet.append_row(new_row_data)
    if(sheet_data[nr_of_rows-2][51]==""):       #if last cell from previous row is empty
        sheet.update_cell(nr_of_rows-1,52,travel_time)
        print("Looks like data is missing in previous column, adding it now.")
else:
    sheet.update_cell(nr_of_rows,current_col_index,travel_time)
    if(sheet_data[nr_of_rows-1][current_col_index-2]==""):      #if previous cell is empty, update it now.
        sheet.update_cell(nr_of_rows,current_col_index-1,travel_time)
        print("Looks like data is missing in previous column, adding it now.")

if(current_hour == 8 and current_min < 30):
    try:
        pushnotification.push_to_iOS("Yesterday's average travel time to cross " + city + " was: " + sheet_data[nr_of_rows-2][-1] + " min"," ",pushbullet_key)
    except:
        print("PushBullet notifications don't work. Try verifying the key!")