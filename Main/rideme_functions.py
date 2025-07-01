# ========== IMPORTS ==========
import csv  # for saving/loading bookings in CSV
import time  # for delay simulation
from datetime import datetime  # pang timestamp
from geopy.geocoders import Nominatim  # para sa geolocation by location name
from geopy.distance import geodesic  # para makuha distance between 2 points
from geopy.exc import GeocoderTimedOut, GeocoderServiceError  # error handling sa geopy
from uuid import uuid4  # pang unique booking ID
import os  # for file/folder handling
from rideme_class import *  # import mo yung mga classes like User, Booking, Vehicle etc

# ========== BOOKING MANAGER CLASS ==========
class BookingManager:
    def __init__(self):
        self.bookings = []  # list of all bookings

    def generate_booking_id(self):
        # generate random unique short booking ID
        return str(uuid4())[:8]

    def add_booking(self, booking):
        # add booking to list then save to file and update user info
        self.bookings.append(booking)
        self.save_user_booking(booking)
        self.update_user_account(booking)

    def cancel_booking(self, booking_id):
        # mark booking as cancelled based on ID
        for b in self.bookings:
            if b.booking_id == booking_id:
                b.cancel()
                self.save_user_booking(b)
                self.update_user_account(b)
                self.save_bookings("bookings.csv")
                return True
        return False

    def complete_booking(self, booking_id, rating):
        # mark booking as completed and save data + driver rating
        for b in self.bookings:
            if b.booking_id == booking_id and b.status == "active":
                b.complete(rating)
                self.save_user_booking(b)
                self.update_user_account(b)
                self.save_bookings("bookings.csv")
                self.save_driver_rating(b.driver_name, b.driver_plate, rating, b.timestamp)
                return True
        return False

    def find_booking(self, booking_id):
        # hanapin booking based sa ID
        for b in self.bookings:
            if b.booking_id == booking_id:
                return b
        return None

    def get_bookings(self, include_cancelled=True):
        # return all bookings, pwede exclude cancelled
        return self.bookings if include_cancelled else [b for b in self.bookings if b.status != "cancelled"]

    def save_bookings(self, filename):
        # save lahat ng bookings to CSV file
        try:
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["BookingID", "Start", "End", "Distance", "Vehicle", "Plate", "Driver", "ETA", "Status", "Timestamp", "Rating"])
                for b in self.bookings:
                    writer.writerow([
                        b.booking_id, b.start_location, b.end_location, b.distance,
                        b.vehicle.vehicle_type, b.driver_plate, b.driver_name,
                        b.eta, b.status, b.timestamp.strftime('%Y-%m-%d %H:%M:%S'), b.rating if b.rating is not None else ""
                    ])
        except Exception as e:
            print("Error saving bookings:", e)

    def load_bookings(self, filename):
        # load bookings from CSV and create Booking objects
        try:
            with open(filename, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    dummy_vehicle = Vehicle("TEMP", 10, 4)  # temp vehicle lang since di naka-save lahat ng info
                    booking = Booking(
                        booking_id=row["BookingID"],
                        vehicle=dummy_vehicle,
                        start_location=row["Start"],
                        end_location=row["End"],
                        distance=float(row["Distance"]),
                        timestamp=datetime.strptime(row["Timestamp"], "%Y-%m-%d %H:%M:%S"),
                        status=row["Status"]
                    )
                    # restore driver info & rating
                    booking.driver_plate = row["Plate"]
                    booking.driver_name = row["Driver"]
                    booking.eta = int(row["ETA"])
                    if row.get("Rating"):
                        booking.rating = int(row["Rating"])
                    self.bookings.append(booking)
        except FileNotFoundError:
            print(f"{filename} not found. Starting fresh.")
        except Exception as e:
            print("Error loading bookings:", e)

    def save_user_booking(self, booking):
        # save user's individual booking history to their own CSV
        username = booking.vehicle.vehicle_id.split('-')[0]  # extract username from vehicle_id
        filepath = f"user_logs/{username}_history.csv"
        os.makedirs("user_logs", exist_ok=True)
        write_header = not os.path.exists(filepath)

        base, vat, total = booking.calculate_total_cost()
        try:
            with open(filepath, 'a', newline='') as file:
                writer = csv.writer(file)
                if write_header:
                    writer.writerow(["Time", "User", "Driver", "Plate", "Start", "End", "Rate/km", "Distance", "Cost", "Tax", "Total", "Status", "Rating"])
                writer.writerow([
                    booking.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    username,
                    booking.driver_name,
                    booking.driver_plate,
                    booking.start_location,
                    booking.end_location,
                    booking.vehicle.cost_per_mile,
                    booking.distance,
                    f"{base:.2f}",
                    f"{vat:.2f}",
                    f"{total:.2f}",
                    booking.status,
                    booking.rating if booking.rating is not None else ""
                ])
        except Exception as e:
            print("Error saving user history:", e)

    def update_user_account(self, booking):
        # update user account info file (like name, history, etc.)
        try:
            os.makedirs("accounts", exist_ok=True)
            filepath = "accounts/users.csv"
            users_data = {}

            if os.path.exists(filepath):
                # load current users
                with open(filepath, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        users_data[row['Username']] = row

            username = booking.vehicle.vehicle_id.split('-')[0]
            user_info = users_data.get(username, {
                "Username": username,
                "Name": username,
                "Password": "****",
                "History": ""
            })

            # append booking info to user's history
            history = f"{booking.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | {booking.start_location} -> {booking.end_location} | {booking.status.title()}"
            if user_info["History"]:
                user_info["History"] += f"\n{history}"
            else:
                user_info["History"] = history

            users_data[username] = user_info

            # write back to users.csv
            with open(filepath, 'w', newline='') as f:
                fieldnames = ["Username", "Name", "Password", "History"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for user in users_data.values():
                    writer.writerow(user)

        except Exception as e:
            print("Error saving user account info:", e)

    def save_driver_rating(self, name, plate, rating, timestamp):
        # append driver rating to ratings.csv
        try:
            with open("ratings.csv", "a", newline='') as file:
                writer = csv.writer(file)
                writer.writerow([name, plate, rating, timestamp.strftime('%Y-%m-%d %H:%M:%S')])
        except Exception as e:
            print("Error saving driver rating:", e)

# ========== LOCATION DISTANCE CALCULATOR ==========
def calculate_distance(start, end):
    # main function to convert location names into coordinates and get distance in km
    if not start.strip() or not end.strip():
        raise ValueError("Please enter both pickup and drop-off locations.")

    geolocator = Nominatim(user_agent="rideme-app")
    try:
        print("Geocoding... Please wait (respecting rate limits)")
        time.sleep(1.5)
        start_location = geolocator.geocode(start)
        time.sleep(1.5)
        end_location = geolocator.geocode(end)

        # handle pag di nahanap yung address
        if not start_location:
            raise ValueError("Pick up location couldn't be found. Try being more specific (e.g., 'Manila City Hall').")
        if not end_location:
            raise ValueError("Drop off location couldn't be found. Try being more specific (e.g., 'Manila City Hall').")
        if not start_location and not end_location:
            raise ValueError("Both locations couldn't be found. Try being more specific (e.g., 'Manila City Hall').")

        coords_1 = (start_location.latitude, start_location.longitude)
        coords_2 = (end_location.latitude, end_location.longitude)
        return round(geodesic(coords_1, coords_2).km, 2)
    
# ========== ERROR HANDLING ==========

    except GeocoderTimedOut:
        raise ValueError("Geocoding timed out. Please check your internet or try again later.")

    except GeocoderServiceError:
        raise ValueError("You're sending requests too fast or too many. Wait a bit or switch to another network (VPN/hotspot).")

    except Exception as e:
        raise ValueError(f"Unexpected error while measuring distance: {str(e)}")

