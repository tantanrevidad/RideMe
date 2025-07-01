import customtkinter as ctk
import tkinter.messagebox as mb
from rideme_class import *
from rideme_functions import *
import os
from PIL import Image, ImageTk
from uuid import uuid4

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

current_user = None
manager = BookingManager()
manager.load_bookings("bookings.csv")


def get_users():
    users = {}
    filepath = "accounts/users.csv"
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            next(file, None)
            for line in file:
                parts = line.strip().split(",", 3)
                if len(parts) < 3:
                    continue
                username, name, password = parts[:3]
                users[username] = {"name": name, "password": password}
    return users

def save_user(username, name, password):
    os.makedirs("accounts", exist_ok=True)
    file = "accounts/users.csv"
    write_header = not os.path.exists(file)
    with open(file, "a") as f:
        if write_header:
            f.write("Username,Name,Password,History\n")
        f.write(f"{username},{name},{password},\n")


class RideMeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RideMe")
        self.geometry("600x650")
        self.resizable(False, False)
        self.configure(fg_color="white")
        self.user = None
        self.show_login()

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def center_frame(self, height=400):
        frame = ctk.CTkFrame(
            self,
            corner_radius=20,
            width=500,
            height=height,
            fg_color="#f2f2f2",
        )
        frame.place(relx=0.5, rely=0.5, anchor="center")
        return frame

    def display_logo(self, parent):
        image = ctk.CTkImage(light_image=Image.open("assets/logo.png"), size=(120, 120))
        label = ctk.CTkLabel(parent, image=image, text="")
        label.image = image
        label.pack(pady=(10, 5))

    def show_login(self):
        self.clear()
        frame = self.center_frame()
        self.display_logo(frame)

        ctk.CTkLabel(frame, text="🚘 RideMe", font=("Arial Black", 26)).pack(pady=(10, 30))
        ctk.CTkButton(frame, text="🔐 Login", height=45, width=200, fg_color="#34c759", hover_color="#28a745", font=("Arial", 14), command=self.login_screen).pack(pady=10, padx=15)
        ctk.CTkButton(frame, text="📝 Register", height=45, width=200, fg_color="#34c759", hover_color="#28a745", font=("Arial", 14), command=self.register_screen).pack(pady=(5, 10), padx=15)

    def register_screen(self):
        self.clear()
        frame = self.center_frame(480)
        self.display_logo(frame)

        ctk.CTkLabel(frame, text="📝 Register", font=("Arial Bold", 20)).pack(pady=20)
        user_entry = ctk.CTkEntry(frame, placeholder_text="Username", width=300)
        pass_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=300)
        name_entry = ctk.CTkEntry(frame, placeholder_text="Full Name", width=300)
        user_entry.pack(pady=8)
        pass_entry.pack(pady=8)
        name_entry.pack(pady=8)

        def register_user():
            username, password, name = user_entry.get(), pass_entry.get(), name_entry.get()
            if username in get_users():
                mb.showerror("Error", "Username already exists.")
                return
            save_user(username, name, password)
            mb.showinfo("Success", "User registered!")
            self.show_login()

        ctk.CTkButton(frame, text="✅ Register", fg_color="#34c759", hover_color="#28a745", command=register_user).pack(pady=15, padx=5)
        ctk.CTkButton(frame, text="🔙 Back", command=self.show_login).pack()

    def login_screen(self):
        self.clear()
        frame = self.center_frame(400)

        ctk.CTkLabel(frame, text="🔐 Login", font=("Arial Bold", 20)).pack(pady=20)
        user_entry = ctk.CTkEntry(frame, placeholder_text="Username", width=300)
        pass_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=300)
        user_entry.pack(pady=10)
        pass_entry.pack(pady=10)

        def login_user():
            users = get_users()
            username, password = user_entry.get(), pass_entry.get()
            if username not in users or users[username]["password"] != password:
                mb.showerror("Login Failed", "Invalid username or password")
                return
            self.user = User(user_id=username, name=users[username]["name"], password=password)
            self.main_menu()

        ctk.CTkButton(frame, text="🔓 Login", fg_color="#34c759", hover_color="#28a745", command=login_user).pack(pady=20)
        ctk.CTkButton(frame, text="🔙 Back", command=self.show_login).pack()

    def main_menu(self):
        self.clear()
        frame = self.center_frame(350)

        ctk.CTkLabel(frame, text=f"🎉 Welcome, {self.user.name}!", font=("Arial Bold", 25)).pack(pady=20)
        ctk.CTkButton(frame, text="🚖 Book Now",font=("Arial Bold", 18), command=self.book_now_screen, height=45, width=220).pack(pady=10, padx=5)
        ctk.CTkButton(frame, text="📖 Manage Bookings",font=("Arial Bold", 18), command=self.manage_bookings, height=45, width=220).pack(pady=10, padx=5)
        ctk.CTkButton(frame, text="🚪 Logout", font=("Arial Bold", 18), command=self.show_login, height=45, width=220).pack(pady=10, padx=5)


    def manage_bookings(self):
        self.clear()
        frame = self.center_frame(520)

        ctk.CTkLabel(frame, text="📂 Your Bookings", font=("Arial Bold", 20)).pack(pady=(15, 5))

        scroll = ctk.CTkScrollableFrame(frame, width=460, height=400, corner_radius=12)
        scroll.pack(pady=10)

        user_file = f"user_logs/{self.user.user_id}_history.csv"
        if not os.path.exists(user_file):
            ctk.CTkLabel(scroll, text="🚫 No bookings yet!", font=("Arial", 14)).pack(pady=20)
            ctk.CTkButton(frame, text="🔙 Back", command=self.main_menu).pack(pady=10)
            return

        latest_bookings = {}

        with open(user_file, "r") as file:
            header = next(file)
            for row in file:
                cols = row.strip().split(",")
                if len(cols) < 13:  # we need up to index 12
                    continue
                booking_id = cols[0]
                latest_bookings[booking_id] = cols

        for booking_id, cols in latest_bookings.items():
            origin = cols[4]
            destination = cols[5]
            fare = cols[10]
            status = cols[11].lower()
            driver = cols[2]
            plate = cols[3]

            # Status display
            if status == "completed":
                status_text = "✅ Completed"
                bg_color = "#e2ffe2"
            elif status == "cancelled":
                status_text = "❌ Cancelled"
                bg_color = "#ffe2e2"
            else:
                status_text = "⏳ Pending"
                bg_color = "#f2f2f2"

            card = ctk.CTkFrame(scroll, fg_color=bg_color, corner_radius=12)
            card.pack(fill="x", padx=8, pady=6)

            summary = (
                f"🆔 Booking ID: {booking_id}\n"
                f"📍 From: {origin} ➡️ {destination}\n"
                f"💸 Fare: ₱{fare} | Status: {status_text}\n"
                f"👨‍✈️ Driver: {driver}\n"
                f"🪪 Plate: {plate}"
            )

            ctk.CTkLabel(
                card,
                text=summary,
                anchor="w",
                justify="left",
                font=("Arial", 13),
            ).pack(padx=12, pady=10)

        ctk.CTkButton(frame, text="🔙 Back", command=self.main_menu).pack(pady=10)

    def book_now_screen(self):
        self.clear()
        
        frame = ctk.CTkFrame(self, fg_color="#f2f2f2", corner_radius=15)
        frame.pack(pady=40, padx=40, fill="both", expand=True)

        ctk.CTkLabel(frame, text="🚘 Select Vehicle", font=("Arial Black", 20)).pack(pady=20)

        vehicles = {
            "Motorcycle 🏍️": Motorcycle,
            "Car (4-Seater) 🚗": Car4Seater,
            "Car (6-Seater) 🚙": Car6Seater,
            "Truck 🚛": Truck,
            "Helicopter 🚁": Helicopter,
            "Cruise Ship 🛳️": CruiseShip,
            "UFO 🛸": UFO
        }

        def select_vehicle(vtype):
            self.vehicle = vehicles[vtype](f"{self.user.user_id}-{str(uuid4())[:4]}")
            self.pick_drop_screen()

        for v in vehicles:
            ctk.CTkButton(
                frame, text=v, command=lambda v=v: select_vehicle(v),
                height=45, font=("Arial", 14)
            ).pack(pady=5, padx=40)

        ctk.CTkButton(frame, text="🔙 Back", command=self.main_menu, height=35).pack(pady=20)


    def pick_drop_screen(self):
        self.clear()

        frame = ctk.CTkFrame(self, fg_color="#f2f2f2", corner_radius=15)
        frame.pack(pady=40, padx=40, fill="both", expand=True)

        ctk.CTkLabel(frame, text="📍 Enter Location", font=("Arial Black", 20)).pack(pady=20)

        pickup = ctk.CTkEntry(frame, placeholder_text="🛫 Pickup Location")
        drop = ctk.CTkEntry(frame, placeholder_text="🛬 Dropoff Location")
        pickup.pack(pady=10, padx=40)
        drop.pack(pady=10, padx=40)

        def confirm_booking():
            try:
                distance = calculate_distance(pickup.get(), drop.get())
                booking = Booking(manager.generate_booking_id(), self.vehicle, pickup.get(), drop.get(), distance)
                self.user.add_booking(booking)
                manager.add_booking(booking)
                self.simulate_ride_screen(booking)
            except ValueError as e:
                mb.showerror("❌ Error", str(e))

        ctk.CTkButton(frame, text="✅ Confirm", command=confirm_booking, height=40).pack(pady=10)
        ctk.CTkButton(frame, text="🔙 Back", command=self.book_now_screen, height=35).pack()


    def simulate_ride_screen(self, booking):
        self.clear()

        frame = ctk.CTkFrame(self, fg_color="#f2f2f2", corner_radius=15)
        frame.pack(pady=40, padx=40, fill="both", expand=True)

        status_label = ctk.CTkLabel(frame, text="🔍 Looking for a driver...", font=("Arial", 16))
        status_label.pack(pady=20)

        def cancel_and_return():
            manager.cancel_booking(booking.booking_id)
            self.manage_bookings() 

        cancel_btn = ctk.CTkButton(self, text="❌ Cancel Ride", command=cancel_and_return)
        cancel_btn.pack(pady=10)

        self.update()
        steps = [
            "🔍 Looking for a driver...",
            "✅ Found a driver",
            "🚗 Driver Arrived, Ride Safe!",
            "🛣️ Driver is driving to your destination...",
            "🏁 You have arrived. Thank You!"
        ]

        def ride_progress(i=0):
            if i < len(steps):
                if status_label.winfo_exists():
                    status_label.configure(text=steps[i])
                    self.after(1500, lambda: ride_progress(i + 1))
            else:
                if self.winfo_exists():  # double check
                    self.rate_driver(booking)

        ride_progress()

    def rate_driver(self, booking):
        self.clear()

        frame = ctk.CTkFrame(self, fg_color="#f2f2f2", corner_radius=15)
        frame.pack(pady=40, padx=40, fill="both", expand=True)

        ctk.CTkLabel(frame, text="🌟 Rate Your Driver", font=("Arial Black", 20)).pack(pady=20)

        rating_var = ctk.IntVar()
        for i in range(1, 6):
            ctk.CTkRadioButton(frame, text=f"{i} ⭐", variable=rating_var, value=i).pack(pady=2)

        def submit_rating():
            rating = rating_var.get()
            if rating == 0:
                mb.showerror("⚠️ Error", "Please select a rating.")
                return
            manager.complete_booking(booking.booking_id, rating)
            self.main_menu()

        ctk.CTkButton(frame, text="📤 Submit Rating", command=submit_rating, height=40).pack(pady=15)

if __name__ == "__main__":
    app = RideMeApp()
    app.mainloop()
