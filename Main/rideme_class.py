from datetime import datetime, timedelta  
import random 
import time  

# ==== VEHICLE CLASSES ====

class Vehicle:
    def __init__(self, vehicle_id, cost_per_mile, capacity, speed=1.0):
        self.vehicle_id = vehicle_id
        self.cost_per_mile = cost_per_mile  # magkano kada km/mile
        self.capacity = capacity  # ilan pwede sakay
        self.status = "available"
        self.vehicle_type = "Generic Vehicle"
        self.speed = speed  # pang compute ng ETA

    def calculate_cost(self, distance):
        return self.cost_per_mile * distance  # basic cost computation lang
    
    def from_type(vehicle_type, vehicle_id):
        mapping = {
            "Motorcycle": Motorcycle,
            "Car (4-Seater)": Car4Seater,
            "Truck": Truck,
            "Helicopter": Helicopter,
            "Cruise Ship": CruiseShip,
            "UFO": UFO
        }
        cls = mapping.get(vehicle_type)
        if cls:
            return cls(vehicle_id)
        else:
            raise ValueError(f"Unknown vehicle type: {vehicle_type}")

    def __str__(self):
        return f"{self.vehicle_type} (ID: {self.vehicle_id}) - Capacity: {self.capacity}, Cost/Mile: ₱{self.cost_per_mile}, Status: {self.status}"

# ==== VEHICLE TYPES (subclasses ng Vehicle) ====

class Motorcycle(Vehicle):
    def __init__(self, vehicle_id):
        super().__init__(vehicle_id, cost_per_mile=5, capacity=1, speed=1.5)
        self.vehicle_type = "Motorcycle"

class Car4Seater(Vehicle):
    def __init__(self, vehicle_id):
        super().__init__(vehicle_id, cost_per_mile=10, capacity=4, speed=1.3)
        self.vehicle_type = "Car (4-Seater)"

    def calculate_cost(self, distance):
        return self.cost_per_mile * distance + 100 if distance > 50 else self.cost_per_mile * distance

class Car6Seater(Vehicle):
    def __init__(self, vehicle_id):
        super().__init__(vehicle_id, cost_per_mile=15, capacity=6, speed=1.2)
        self.vehicle_type = "Car (6-Seater)"

class Truck(Vehicle):
    def __init__(self, vehicle_id):
        super().__init__(vehicle_id, cost_per_mile=25, capacity=2, speed=0.8)
        self.vehicle_type = "Truck"

    def calculate_cost(self, distance):
        return (self.cost_per_mile * distance) + 200

class Helicopter(Vehicle):
    def __init__(self, vehicle_id):
        super().__init__(vehicle_id, cost_per_mile=150, capacity=5, speed=3.5)
        self.vehicle_type = "Helicopter"

    def calculate_cost(self, distance):
        return 1000 + (self.cost_per_mile * distance)

class CruiseShip(Vehicle):
    def __init__(self, vehicle_id):
        super().__init__(vehicle_id, cost_per_mile=100, capacity=100, speed=0.5)
        self.vehicle_type = "Cruise Ship"

    def calculate_cost(self, distance):
        # may 10% discount pag long distance (>200km)
        return (self.cost_per_mile * distance) * 0.9 if distance > 200 else self.cost_per_mile * distance

class UFO(Vehicle):
    def __init__(self, vehicle_id):
        super().__init__(vehicle_id, cost_per_mile=300, capacity=3, speed=5.0)
        self.vehicle_type = "UFO"

    def calculate_cost(self, distance):
        return self.cost_per_mile * distance + 5000  # may fixed na mahal na charge

# ==== USER CLASS ====

class User:
    def __init__(self, user_id, name, password):
        # simple user profile
        self.user_id = user_id
        self.name = name
        self.password = password
        self.booking_history = []  # para sa list ng bookings niya

    def add_booking(self, booking):
        self.booking_history.append(booking)

    def has_active_booking(self):
        # check kung may naka-active na booking pa
        return any(b.status == "active" for b in self.booking_history)

    def get_active_booking(self):
        # kunin yung current active booking
        for b in self.booking_history:
            if b.status == "active":
                return b
        return None

    def view_booking_history(self):
        # print booking records ng user
        return "No bookings yet." if not self.booking_history else "\n\n".join(str(b) for b in self.booking_history)

    def __str__(self):
        return f"Welcome back, {self.name}! You have {len(self.booking_history)} booking(s) in your history.\n"

# ==== BOOKING CLASS ====

class Booking:
    def __init__(self, booking_id, vehicle, start_location, end_location, distance, timestamp=None, status="active"):
        self.booking_id = booking_id
        self.vehicle = vehicle
        self.start_location = start_location
        self.end_location = end_location
        self.distance = distance
        self.timestamp = timestamp if timestamp else datetime.now()
        self.status = status

        # driver info generated randomly
        self.driver_name = random.choice(["Juan Dela Cruz", "Maria Santos", "Jose Rizal", "Andres Bonifacio"])
        self.driver_plate = f"{random.choice(['ABC', 'XYZ', 'MNL'])}-{random.randint(100,999)}"

        # compute estimated arrival time (in minutes)
        self.eta = int((self.distance / self.vehicle.speed) * 1.5 + random.randint(0, 5))

        self.rating = None  # user rating (after ride)

    def simulate_ride_status(self):
        # simulate actual ride, with delays and messages
        print("Booking your ride...")
        time.sleep(1.5)
        print("Finding a driver...")
        time.sleep(3)
        print("Driver found! Driver is on the way...")
        travel_time = min(120, max(30, self.eta * 60))  # clamp travel time para di sobrang tagal
        time.sleep(travel_time / 100.0)
        print("Driver has arrived. Enjoy your ride!")

    def calculate_total_cost(self):
        # compute full cost including tax
        base_cost = self.vehicle.calculate_cost(self.distance)
        tax = base_cost * 0.02  # 2% VAT or service fee
        return base_cost, tax, base_cost + tax

    def cancel(self):
        self.status = "cancelled"

    def complete(self, rating):
        self.status = "completed"
        self.rating = rating

    def __str__(self):
        base, vat, total = self.calculate_total_cost()
        rating_text = f"\nRating: {self.rating}★" if self.rating is not None else ""
        eta_time = (self.timestamp + timedelta(minutes=self.eta)).strftime("%I:%M %p")
        return (
            f"From: {self.start_location} to {self.end_location}\n"
            f"Vehicle: {self.vehicle.vehicle_type}\n"
            f"Distance: {self.distance:.2f} km\n"
            f"Base: ₱{base:.2f}, VAT: ₱{vat:.2f}, Total: ₱{total:.2f}\n"
            f"Driver: {self.driver_name} ({self.driver_plate})\n"
            f"ETA: {self.eta} minutes (Arrives at {eta_time})\n"
            f"Date: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Status: {self.status.title()}{rating_text}"
        )
