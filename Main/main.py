import customtkinter as ctk
import tkinter as tk
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
        image = ctk.CTkImage(light_image=Image.open("assets/logo.png"), size=(200, 200))
        label = ctk.CTkLabel(parent, image=image, text="")
        label.image = image
        label.pack()

    def show_login(self):
        self.clear()
        frame = self.center_frame()
        self.display_logo(frame)

        ctk.CTkLabel(frame, text="RideMe™",anchor="center", justify="center", font=("Arial Black", 26)).pack(pady=(10, 30))
        ctk.CTkButton(frame, text="🔐 Login", height=45, width=200, fg_color="#34c759", hover_color="#159b34", font=("Arial Bold", 15), command=self.login_screen).pack(pady=10, padx=15)
        ctk.CTkButton(frame, text="📝 Register", height=45, width=200, fg_color="#166b2b", hover_color="#28a745", font=("Arial Bold", 15), command=self.register_screen).pack(pady=(5, 10), padx=15)

    def register_screen(self):
        self.clear()
        frame = self.center_frame(480)
        self.display_logo(frame)

        ctk.CTkLabel(frame, text="📝 Register", font=("Arial Bold", 30)).pack(pady=20)
        user_entry = ctk.CTkEntry(frame, placeholder_text="Username", width=300)
        pass_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=300)
        name_entry = ctk.CTkEntry(frame, placeholder_text="Full Name", width=300)
        user_entry.pack(pady=8, padx=5)
        pass_entry.pack(pady=8, padx=5)
        name_entry.pack(pady=8, padx=5)

        def register_user():
            username, password, name = user_entry.get(), pass_entry.get(), name_entry.get()
            if username in get_users():
                mb.showerror("Error", "Username already exists.")
                return
            save_user(username, name, password)
            mb.showinfo("Success", "User registered!")
            self.show_login()

        ctk.CTkButton(frame, text="✅ Register",font=("Arial Bold", 14), fg_color="#34c759", hover_color="#28a745", command=register_user).pack(pady=15, padx=5)
        ctk.CTkButton(frame, text="🔙 Back",font=("Arial Bold", 14),fg_color="#004e14", hover_color="#287a3b", command=self.show_login).pack(pady=(0,10))

    def login_screen(self):
        self.clear()
        frame = self.center_frame(400)

        ctk.CTkLabel(frame, text="🔐 Login", font=("Arial Black", 30)).pack(pady=20)
        user_entry = ctk.CTkEntry(frame, placeholder_text="Username", width=300)
        pass_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=300)
        user_entry.pack(pady=10, padx=10)
        pass_entry.pack(pady=10, padx=10)

        def login_user():
            users = get_users()
            username, password = user_entry.get(), pass_entry.get()
            if username not in users or users[username]["password"] != password:
                mb.showerror("Login Failed", "Invalid username or password")
                return
            self.user = User(user_id=username, name=users[username]["name"], password=password)
            self.main_menu()

        ctk.CTkButton(frame, text="🔓 Login",font=("Arial Bold", 14), fg_color="#34c759", hover_color="#28a745", command=login_user).pack(pady=20)
        ctk.CTkButton(frame, text="🔙 Back",font=("Arial Bold", 14),fg_color="#004e14", hover_color="#287a3b", command=self.show_login).pack(pady=(0,10))

    def main_menu(self):
        self.clear()
        frame = self.center_frame(350)
        self.display_logo(frame)

        ctk.CTkLabel(frame, text=f"🎉 Welcome, {self.user.name}!", font=("Arial Black", 30)).pack(pady=20, padx=15)
        ctk.CTkButton(frame, text="🚖 Book Now",font=("Arial Bold", 18), command=self.book_now_screen, height=45, width=220).pack(pady=10, padx=10)
        ctk.CTkButton(frame, text="📖 View Bookings",font=("Arial Bold", 18), command=self.manage_bookings, height=45, width=220).pack(pady=10, padx=10)
        ctk.CTkButton(frame, text="🚪 Logout", font=("Arial Bold", 18), command=self.show_login, height=45, width=220).pack(pady=10, padx=10)


    def manage_bookings(self):
        self.clear()
        frame = self.center_frame(550)

        ctk.CTkLabel(frame, text="📂 Your Bookings", font=("Arial Bold", 20)).pack(pady=(15, 5))

        scroll = ctk.CTkScrollableFrame(frame, width=460, height=420, corner_radius=12)
        scroll.pack(pady=10)

        user_file = f"user_logs/{self.user.user_id}_history.csv"
        if not os.path.exists(user_file):
            ctk.CTkLabel(scroll, text="🚫 No bookings yet!", font=("Arial", 14)).pack(pady=20)
            ctk.CTkButton(frame, text="🔙 Back", command=self.main_menu).pack(pady=10)
            return

        # Load icons and star images once
        icon_size = (40, 40)
        vehicle_icons = {
            "Motorcycle": ctk.CTkImage(Image.open("assets/moto.png"), size=icon_size),
            "Car (4-Seater)": ctk.CTkImage(Image.open("assets/car.png"), size=icon_size),
            "Truck": ctk.CTkImage(Image.open("assets/truck.png"), size=icon_size),
            "Helicopter": ctk.CTkImage(Image.open("assets/helicopter.png"), size=icon_size),
            "Cruise Ship": ctk.CTkImage(Image.open("assets/ship.png"), size=icon_size),
            "UFO": ctk.CTkImage(Image.open("assets/ufo.png"), size=icon_size),
        }

        star_empty = ctk.CTkImage(Image.open("assets/star_empty.png"), size=(20, 20))
        star_filled = ctk.CTkImage(Image.open("assets/star_filled.png"), size=(20, 20))

        latest_bookings = {}
        with open(user_file, "r") as file:
            next(file)
            for row in file:
                cols = row.strip().split(",")
                if len(cols) < 15:
                    continue
                booking_id = cols[0]
                latest_bookings[booking_id] = cols

        for booking_id, cols in latest_bookings.items():
            timestamp = cols[1]
            vehicle = cols[7]
            rate_per_km = cols[8]
            distance = cols[9]
            fare = cols[12]
            status = cols[13].lower()
            rating = cols[14]
            driver = cols[3]
            plate = cols[4]
            origin = cols[5].title()
            destination = cols[6].title()

            # Set status label & background color
            if status == "completed":
                status_text = "✅ Completed"
                bg_color = "#80c696"
            elif status == "cancelled":
                status_text = "❌ Cancelled"
                bg_color = "#da7a7a"
            else:
                status_text = "⏳ Pending"
                bg_color = "#f2f2f2"

            # Vehicle icon fallback
            icon = vehicle_icons.get(vehicle, None)

            # Create booking card
            card = ctk.CTkFrame(scroll, fg_color=bg_color, corner_radius=12)
            card.pack(fill="x", padx=8, pady=6)

            inner_frame = ctk.CTkFrame(card, fg_color="transparent")
            inner_frame.pack(fill="both", expand=True, padx=10, pady=8)

            inner_frame.grid_columnconfigure(1, weight=1)

            # Left: Vehicle Icon
            if icon:
                ctk.CTkLabel(inner_frame, image=icon, text="").grid(row=0, column=0, rowspan=3, padx=(0, 12), pady=2, sticky="w")

            # Center: Booking Info
            summary = (
                f"🆔 {booking_id}\n"
                f"📍 {origin} ➡️ {destination}\n"
                f"🕓 {timestamp}\n"
                f"💸 ₱{fare} | {status_text}\n"
                f"👨‍✈️ {driver} | 🪪 {plate}"
            )
            ctk.CTkLabel(inner_frame, text=summary, anchor="w", justify="left", font=("Verdana", 11)).grid(row=0, column=1, sticky="w")

            # Right: Star rating
            if rating.strip().isdigit():
                rating_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
                rating_frame.grid(row=0, column=2, padx=(20, 0), sticky="e")

                rating_value = int(rating.strip())
                for i in range(5):
                    ctk.CTkLabel(
                        rating_frame,
                        image=star_filled if i < rating_value else star_empty,
                        text="", anchor="e",
                    ).grid(row=0, column=i, padx=1, sticky="e")

        ctk.CTkButton(frame, text="🔙 Back", command=self.main_menu).pack(pady=10)

    def book_now_screen(self):
        self.clear()

        frame = ctk.CTkFrame(self, fg_color="#f2f2f2", corner_radius=15)
        frame.pack(pady=40, padx=40, fill="both", expand=True)

        # Title
        ctk.CTkLabel(
            frame,
            text="🚘 Select Vehicle",
            font=("Arial Black", 30)
        ).pack(pady=(20, 10))

        vehicles = {
            "Motorcycle": Motorcycle,
            "Car": Car4Seater,
            "Truck": Truck,
            "Helicopter": Helicopter,
            "Cruise Ship": CruiseShip,
            "UFO": UFO
        }

        icon_size = (40, 40)
        image_paths = {
            "Motorcycle": "assets/moto.png",
            "Car": "assets/car.png",
            "Truck": "assets/truck.png",
            "Helicopter": "assets/helicopter.png",
            "Cruise Ship": "assets/ship.png",
            "UFO": "assets/ufo.png"
        }

        vehicle_images = {
            name: ctk.CTkImage(Image.open(path), size=icon_size)
            for name, path in image_paths.items()
        }

        def select_vehicle(vtype):
            self.vehicle = vehicles[vtype](f"{self.user.user_id}-{str(uuid4())[:4]}")
            self.pick_drop_screen()

        # Button Grid Frame
        button_grid = ctk.CTkFrame(frame, fg_color="transparent")
        button_grid.pack(pady=10)

        # Grid layout: 2 columns
        max_cols = 2
        button_size = 100 # Square size

        for i, (label, cls) in enumerate(vehicles.items()):
            row, col = divmod(i, max_cols)

            btn = ctk.CTkButton(
                button_grid,
                text=label,
                image=vehicle_images[label],
                compound="top",
                command=lambda v=label: select_vehicle(v),
                width=button_size,
                height=button_size,
                font=("Arial Bold", 14),
                fg_color="#6DBD98",
                hover_color="#3F825B",
                text_color="white",
                corner_radius=12
            )
            btn.grid(row=row, column=col, padx=15, pady=15)

        ctk.CTkButton(frame, text="🔙 Back",font=("Arial Bold", 14),fg_color="#004e14", hover_color="#287a3b", command=self.main_menu).pack(pady=(15,10))


    def pick_drop_screen(self):
        self.clear()

        frame = ctk.CTkFrame(self, fg_color="#f2f2f2", corner_radius=15)
        frame.pack(pady=40, padx=40, fill="both", expand=True)
        self.display_logo(frame)

        ctk.CTkLabel(frame, text="📍Enter Location",anchor="center", justify="center", font=("Arial Black", 30)).pack(pady=20)

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

        ctk.CTkButton(frame, text="✅ Confirm",font=("Arial Bold", 14),hover_color="#479566", command=confirm_booking, height=40).pack(pady=10)
        ctk.CTkButton(frame, text="🔙 Back",font=("Arial Bold", 14),fg_color="#004e14", hover_color="#287a3b", command=self.book_now_screen, height=35).pack()


    def simulate_ride_screen(self, booking):
        self.clear()

        frame = ctk.CTkFrame(self, fg_color="#f2f2f2", corner_radius=15)
        frame.pack(pady=40, padx=40, fill="both", expand=True)
        self.display_logo(frame)

        # Status label
        status_label = ctk.CTkLabel(frame, text="🔍 Starting ride simulation...", font=("Arial", 16))
        status_label.pack(pady=(20, 10))

        # Progress bar
        progress_bar = ctk.CTkProgressBar(frame, orientation="horizontal", width=300)
        progress_bar.pack(pady=10)
        progress_bar.set(0)

        # Info frame (hidden initially)
        info_frame = ctk.CTkFrame(frame, fg_color="#e8e8e8", corner_radius=10)
        info_frame.pack(pady=(10, 20))
        info_frame.pack_forget()

        distance_label = ctk.CTkLabel(info_frame, text="", font=("Arial", 14))
        distance_label.pack(pady=5, padx=10)

        price_label = ctk.CTkLabel(info_frame, text="", font=("Arial", 14))
        price_label.pack(pady=5, padx=10)

        # Cancel button
        def cancel_and_return():
            manager.cancel_booking(booking.booking_id)
            self.manage_bookings()

        cancel_btn = ctk.CTkButton(self, text="❌ Cancel Ride",font=("Arial", 14),fg_color="#bb3131", hover_color="#901919", command=cancel_and_return)
        cancel_btn.pack(pady=10)

        # Ride steps
        steps = [
            ("🔍 Looking for a driver...", 0.2),
            ("✅ Found a driver", 0.4),
            ("🚗 Driver Arrived, Ride Safe!", 0.6),
            ("🛣️ Driver is driving to your destination...", 0.8),
            ("🏁 You have arrived. Thank You!", 1.0)
        ]
        
        # Load ride details
        user_file = f"user_logs/{self.user.user_id}_history.csv"
        latest_bookings = {}

        with open(user_file, "r") as file:
            header = next(file)
            for row in file:
                cols = row.strip().split(",")
                if len(cols) < 15:  # we need up to index 12
                    continue
                booking_id = cols[0]
                latest_bookings[booking_id] = cols

        for booking_id, cols in latest_bookings.items():
            distance = cols[9]
            price = cols[10]

        # Step transition logic
        def next_step(i=0):
            if i < len(steps):
                text, progress = steps[i]
                if status_label.winfo_exists():  # 🛑 Make sure the widget still exists
                    status_label.configure(text=text)
                    progress_bar.set(progress)

                    # Show ride info after driver is found
                    if "Found a driver" in text and info_frame.winfo_exists():
                        info_frame.pack(pady=(10, 20))
                        distance_label.configure(text=f"📏 Distance: {distance} km")
                        price_label.configure(text=f"💰 Amount: ₱{price}")

                    self.after(1800, lambda: next_step(i + 1))
            else:
                # ✅ Only switch to rating if still on this screen
                if status_label.winfo_exists():
                    self.rate_driver(booking)

        next_step()

    def rate_driver(self, booking):
        self.clear()

        frame = ctk.CTkFrame(self, fg_color="#f2f2f2", corner_radius=15)
        frame.pack(pady=40, padx=40, fill="both", expand=True)
        self.display_logo(frame)

        ctk.CTkLabel(frame, text="🌟 Rate Your Driver", font=("Arial Black", 30)).pack(pady=20)

        # Load star icons
        empty_star = ctk.CTkImage(Image.open("assets/star_empty.png"), size=(40, 40))
        filled_star = ctk.CTkImage(Image.open("assets/star_filled.png"), size=(40, 40))

        # State variable to track selected rating
        self.selected_rating = ctk.IntVar(value=0)

        # Create star buttons in a horizontal frame
        star_frame = ctk.CTkFrame(frame, fg_color="transparent")
        star_frame.pack(pady=10)

        # Function to update which stars are filled
        def update_stars(n):
            self.selected_rating.set(n)
            for i in range(5):
                self.star_buttons[i].configure(image=filled_star if i < n else empty_star)

        # Create and store star buttons
        self.star_buttons = []
        for i in range(5):
            btn = ctk.CTkButton(
                star_frame,
                text="",
                image=empty_star,
                width=50,
                height=50,
                fg_color="transparent",
                hover=False,
                command=lambda i=i: update_stars(i + 1)
            )
            btn.grid(row=0, column=i, padx=5)
            self.star_buttons.append(btn)

        # Submit button logic
        def submit_rating():
            rating = self.selected_rating.get()
            if rating == 0:
                mb.showerror("⚠️ Error", "Please select a rating.")
                return
            manager.complete_booking(booking.booking_id, rating)
            self.main_menu()

        # Submit button
        ctk.CTkButton(
            frame,
            text="📤 Submit Rating",
            command=submit_rating,
            font=("Arial Bold", 14),
            fg_color="#2ecc71",
            hover_color="#14783d",
            text_color="white",
            corner_radius=12,
            height=45
        ).pack(pady=25, padx=50, fill="x")

if __name__ == "__main__":
    app = RideMeApp()
    app.mainloop()
