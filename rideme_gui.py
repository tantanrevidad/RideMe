#chinat gpt ko lang to for beta testing sorry HAHAHHA 

import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import threading
import time
import csv
from datetime import timedelta
from rideme_functions import calculate_distance, BookingManager
from rideme_class import *
from rideme_functions import *

class RideMeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RideMe - Book Your Adventure")
        self.root.geometry("520x640")
        self.root.configure(bg="#fff7f0")

        self.user_db = {}
        self.current_user = None
        self.booking_manager = BookingManager()
        self.booking_manager.load_bookings("bookings.csv")
        self.load_users()

        self.vehicle_types = {
            "Motorcycle": Motorcycle("MOT-1"),
            "Car (4-Seater)": Car4Seater("CAR4-1"),
            "Car (6-Seater)": Car6Seater("CAR6-1"),
            "Truck": Truck("TRK-1"),
            "Helicopter": Helicopter("HEL-1"),
            "Cruise Ship": CruiseShip("CRS-1"),
            "UFO": UFO("UFO-1")
        }

        self.welcome_screen()

    def load_users(self):
        if os.path.exists("users.csv"):
            with open("users.csv", newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.user_db[row['Username']] = User(row['Username'], row['Name'], row['Password'])

    def save_users(self):
        with open("users.csv", "w", newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["Username", "Name", "Password"])
            writer.writeheader()
            for user in self.user_db.values():
                writer.writerow({"Username": user.user_id, "Name": user.name, "Password": user.password})

    def save_user_history(self, booking):
        os.makedirs("user_logs", exist_ok=True)
        filename = f"user_logs/{self.current_user.user_id}_history.csv"
        write_header = not os.path.exists(filename)
        base, vat, total = booking.calculate_total_cost()

        with open(filename, "a", newline='') as file:
            writer = csv.writer(file)
            if write_header:
                writer.writerow(["Time", "User", "Driver", "Plate", "Start", "End", "Rate/km", "Distance", "Cost", "Tax", "Total", "Status", "Rating"])
            writer.writerow([
                booking.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                self.current_user.user_id,
                booking.driver_name,
                booking.driver_plate,
                booking.start_location,
                booking.end_location,
                booking.vehicle.cost_per_mile,
                booking.distance,
                f"{base:.2f}", f"{vat:.2f}", f"{total:.2f}",
                booking.status,
                booking.rating if booking.rating else ""
            ])

            print("✅ CSV saved:", os.path.abspath(filename))

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def welcome_screen(self):
        self.clear_window()
        tk.Label(self.root, text="🚗 RideMe", font=("Helvetica", 28, "bold"), fg="#880000", bg="#fff7f0").pack(pady=20)
        tk.Label(self.root, text="Choose an option", font=("Arial", 16), bg="#fff7f0").pack(pady=10)
        tk.Button(self.root, text="Login", font=("Arial", 14), command=self.login_screen, bg="#b8860b", fg="white").pack(pady=10)
        tk.Button(self.root, text="Register", font=("Arial", 14), command=self.register_screen).pack(pady=5)

    def register_screen(self):
        self.clear_window()
        tk.Label(self.root, text="📝 Register", font=("Helvetica", 24, "bold"), fg="#880000", bg="#fff7f0").pack(pady=20)
        name_entry = tk.Entry(self.root); user_entry = tk.Entry(self.root); pass_entry = tk.Entry(self.root, show="*")
        for lbl, ent in zip(["Name", "Username", "Password"], [name_entry, user_entry, pass_entry]):
            tk.Label(self.root, text=lbl, bg="#fff7f0").pack(); ent.pack()

        def register():
            name, user, pw = name_entry.get(), user_entry.get(), pass_entry.get()
            if user in self.user_db:
                messagebox.showerror("Error", "Username already taken.")
            else:
                self.user_db[user] = User(user, name, pw)
                self.save_users()
                messagebox.showinfo("Success", "Account created!")
                self.login_screen()

        tk.Button(self.root, text="Register", command=register, bg="#880000", fg="white").pack(pady=10)
        tk.Button(self.root, text="Back", command=self.welcome_screen).pack()

    def login_screen(self):
        self.clear_window()
        tk.Label(self.root, text="🔑 Login", font=("Helvetica", 24, "bold"), fg="#880000", bg="#fff7f0").pack(pady=20)
        user_entry = tk.Entry(self.root); pass_entry = tk.Entry(self.root, show="*")
        for lbl, ent in zip(["Username", "Password"], [user_entry, pass_entry]):
            tk.Label(self.root, text=lbl, bg="#fff7f0").pack(); ent.pack()

        def login():
            user, pw = user_entry.get(), pass_entry.get()
            if user in self.user_db and self.user_db[user].password == pw:
                self.current_user = self.user_db[user]
                self.main_menu()
            else:
                messagebox.showerror("Error", "Invalid login.")

        tk.Button(self.root, text="Login", command=login, bg="#880000", fg="white").pack(pady=10)
        tk.Button(self.root, text="Back", command=self.welcome_screen).pack()


    def main_menu(self):
        self.clear_window()
        tk.Label(self.root, text=f"Hi {self.current_user.name}!", font=("Helvetica", 20), bg="#fff7f0").pack(pady=10)
        active_booking = self.current_user.get_active_booking()
        if active_booking:
            tk.Label(self.root, text="🚕 Ongoing Ride", font=("Arial", 16, "bold"), bg="#fff7f0", fg="#006400").pack(pady=10)
            tk.Label(self.root, text=str(active_booking), bg="#fff7f0", justify="left", wraplength=460).pack(pady=10)
            tk.Button(self.root, text="Cancel Ride", command=lambda: self.cancel_ride(active_booking)).pack(pady=5)
        else:
            tk.Button(self.root, text="Book a Ride", font=("Arial", 14), command=self.book_ride).pack(pady=10)
        tk.Button(self.root, text="Booking History", font=("Arial", 14), command=self.view_history).pack(pady=10)
        if not active_booking:
            tk.Button(self.root, text="Logout", font=("Arial", 14), command=self.welcome_screen).pack(pady=10)

    def cancel_ride(self, booking):
        if messagebox.askyesno("Cancel Ride", "Are you sure you want to cancel your current ride?"):
            self.booking_manager.cancel_booking(booking.booking_id)
            self.main_menu()

    def book_ride(self):
        if self.current_user.has_active_booking():
            messagebox.showwarning("Warning", "You have an ongoing ride. Finish or cancel it first.")
            return

        self.clear_window()
        tk.Label(self.root, text="Book a Ride", font=("Helvetica", 24, "bold"), fg="#880000", bg="#fff7f0").pack(pady=10)
        start_entry = tk.Entry(self.root); end_entry = tk.Entry(self.root)
        for lbl, ent in zip(["Start Location (e.g. Manila)", "Destination (e.g. Quezon City)"], [start_entry, end_entry]):
            tk.Label(self.root, text=lbl, bg="#fff7f0").pack(); ent.pack()

        sorted_vehicles = sorted(self.vehicle_types.items(), key=lambda kv: kv[1].calculate_cost(10))
        vehicle_dropdown = ttk.Combobox(self.root, values=[v[0] for v in sorted_vehicles])
        vehicle_dropdown.pack()

        def confirm():
            def simulate_and_book():
                try:
                    start, end = start_entry.get(), end_entry.get()
                    vehicle = self.vehicle_types[vehicle_dropdown.get()]
                    distance = calculate_distance(start, end)
                    self.clear_window()

                    booking_id = self.booking_manager.generate_booking_id()
                    booking = Booking(booking_id, vehicle, start, end, distance)
                    self.current_user.add_booking(booking)
                    self.booking_manager.add_booking(booking)
                    self.booking_manager.save_bookings("bookings.csv")
                    self.save_user_history(booking)

                    tk.Label(self.root, text="Finding a driver...", font=("Arial", 16), bg="#fff7f0").pack(pady=10)
                    self.root.update(); time.sleep(2)

                    tk.Label(self.root, text="🚕 Driver is on the way to your location...", bg="#fff7f0").pack(pady=5)
                    self.root.update(); time.sleep(2)

                    tk.Label(self.root, text="📍 Driver has arrived at pickup location!", bg="#fff7f0").pack(pady=5)
                    self.root.update(); time.sleep(2)

                    tk.Label(self.root, text="🧍 You've been picked up. Heading to destination...", bg="#fff7f0").pack(pady=5)
                    self.root.update(); time.sleep(1)

                    progress = ttk.Progressbar(self.root, length=400, mode='determinate')
                    progress.pack(pady=20)

                    def simulate_dropoff():
                        for i in range(booking.eta * 2):
                            progress['value'] = (i + 1) / (booking.eta * 2) * 100
                            self.root.update()
                            time.sleep(1)

                        def final_step():
                            messagebox.showinfo("Arrived!", "You have arrived at your destination.")
                            rating = simpledialog.askinteger("Rate Driver", f"Rate your driver {booking.driver_name} (1-5):", minvalue=1, maxvalue=5, parent=self.root)
                            comment = simpledialog.askstring("Feedback", f"Any comment for your driver?", parent=self.root)

                            if rating:
                                booking.comment = comment
                                self.booking_manager.complete_booking(booking.booking_id, rating)
                                self.save_user_history(booking)

                    threading.Thread(target=simulate_dropoff).start()

                except ValueError as e:
                    messagebox.showerror("Error", str(e))
                    self.main_menu()

            threading.Thread(target=simulate_and_book).start()

        tk.Button(self.root, text="Confirm Ride", command=confirm, bg="#880000", fg="white").pack(pady=10)
        tk.Button(self.root, text="Back", command=self.main_menu).pack()

    def view_history(self):
        self.clear_window()
        tk.Label(self.root, text="📖 Booking History", font=("Helvetica", 22, "bold"), fg="#880000", bg="#fff7f0").pack(pady=10)
        history_text = tk.Text(self.root, width=60, height=20)
        history_text.insert(tk.END, self.current_user.view_booking_history())
        history_text.pack()
        tk.Button(self.root, text="Book Again", command=self.book_ride).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.main_menu).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = RideMeApp(root)
    root.mainloop()
