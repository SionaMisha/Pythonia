# Name : Siona Misha Nazareth
# Student ID: s4106743
# Highest attempted - All parts
# Problems - None


import csv
from datetime import datetime
import sys

# Below defined classes are used to raise various exceptions that might occur during the code exceution
class InvalidGuestNameError(Exception):
    #Exception raised for invalid guest names.
    def __init__(self, message="Guest name must contain only alphabetic characters."):
        self.message = message
        super().__init__(self.message)

class InvalidProductError(Exception):
    #Exception raised for invalid product entries.
    def __init__(self, message="The product entered is not valid."):
        self.message = message
        super().__init__(self.message)

class InvalidQuantityError(Exception):
    #Exception raised for invalid quantities.
    def __init__(self, message="Quantity must be a positive integer."):
        self.message = message
        super().__init__(self.message)

class DateDiscrepancyError(Exception):
    #Exception raised for discrepancies with dates.
    def __init__(self, message="There is a date discrepancy."):
        self.message = message
        super().__init__(self.message)


#Bookinf class has the functions used for booking process
class Booking:
    def __init__(self,guest):
        #Initialize a Booking with a guest and prepare product lists and records.
        self.products = []  # List to store selected products
        self.apartment = None # List to store apartment products
        self.records = Records()   # Instance to manage records of orders
        self.guest = guest    # Store guest information
    
    #Add a product to the booking. Ensure only one apartment can be booked.
    def add_product(self, product, quantity):
        if isinstance(product, ApartmentUnit):
            if self.apartment is not None:
                raise Exception("An order can only contain one apartment reservation.")
            self.apartment = product     # Store the apartment if it's valid
        self.products.append((product, quantity))    # Add product and quantity to the list


    #Process a booking that includes a bundle of products.
    def process_bundle_booking(self,guest,length_of_stay):
        # Get the bundle ID from the user
        bundle_id = input("Enter the Bundle ID: ").strip()
        
        # Find the bundle in products.csv
        bundle = self.records.find_product(bundle_id)    # Check if the bundle exists
        if not bundle or not bundle.bundle_id.startswith('B'):
            print(f"Bundle with ID {bundle_id} not found!")
            return
        
        # Extract apartment and supplementary item details
        apartment_id = None
        apartment_name = None
        apartment_price = None
        supplementary_items = []  #List to hold supplementary items
        
        
        for item, quantity in bundle.components:  # Each item is a tuple (product, quantity)
            product = item  # This is the actual product object (e.g., ApartmentUnit or SupplementaryItem)
            
            if isinstance(product, ApartmentUnit):  # Check if it's an apartment
                apartment_id = product.product_id  # Get apartment ID
                apartment_name = product.name  # Get apartment name
                apartment_price = product.price  # Get apartment price
                apartment_capacity = product.capacity

            elif isinstance(product, SupplementaryItem):  # Check if it's a supplementary item
                supplementary_items.append((product,quantity))   # Add to the list of supplementary items

        # Validate that we found an apartment
        if apartment_id is None or apartment_name is None or apartment_price is None:
            print(f"Apartment details for ID {apartment_id} not found!")
            return

        # Loop to get the number of guests
        while True:
            try:
                num_guests = int(input(f"Number of guests (max {apartment_capacity}): "))
                if num_guests <= apartment_capacity:
                    break   # Valid input, exit loop
                else:
                    print(f"Number of guests exceeds apartment capacity ({apartment_capacity}).")
            except ValueError:
                print("Invalid input. Please enter a valid number.")
    

        supplementary_items_cost = 0
        
        # Calculate cost of supplementary items

        for product, quantity in supplementary_items:  # Now each element is a tuple (product, quantity)
            if product.product_id.startswith('SI'):
                product_price = self.records.find_product(product.product_id).price   #Fetch the price
                supplementary_items_cost += product_price * quantity  # Add price * quantity to total cost
        
        # Get the length of stay from the user

        order = Order(guest,apartment_name, length_of_stay)  # Create an order instanc

        # Calculate total cost using compute_cost
        apartment_sub_total, original_cost, discount, final_total_cost, earned_reward = order.compute_cost(
            apartment_price, length_of_stay, supplementary_items_cost
        )
    
        # Save the order (using guest's name, the formatted product quantities, final cost, and earned rewards)
        guest_name = guest.name 
       
        # Save only the products in the bundle
        product_quantities = [f"1 x {apartment_id}"]  # Start with the apartment
        for product, quantity in supplementary_items:
            if quantity > 0:
                product_quantities.append(f"{quantity} x {product.product_id}")  # Add supplementary items from the bundle
        self.records.save_order(guest_name, product_quantities, final_total_cost, earned_reward)
        return num_guests,apartment_name,apartment_price, apartment_sub_total,supplementary_items_cost,supplementary_items, original_cost, discount, final_total_cost, earned_reward 

    
    #Process a standard booking without bundles.
    def process_normal_booking(self,guest,length_of_stay):
        extra_bed_cost = 0  #Initialize extra bed cost
        extra_car_park_cost= 0  # Initialize car park cost

        while True:
            try:
                apartment_id = input("Enter apartment ID: ")
                apartment = self.records.find_product(apartment_id)
                if isinstance(apartment, ApartmentUnit):
                    self.add_product(apartment, 1)  #add apartment to booking
                    break
                else:
                    print("Please choose a valid Apartment Unit.")
            except InvalidProductError as e:
                print(e)

         # Enter the number of guests and nights
        while True:
            try:
                num_guests = int(input(f"Number of guests (max {apartment.capacity}): "))
                if num_guests <= apartment.capacity:
                    break
                else:
                    print(f"Number of guests exceeds apartment capacity ({apartment.capacity}).")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

        # Validate extra beds
        order = Order(guest, apartment, length_of_stay)    # Create an order instance
        self.records.orders.append(order)  # Store the order in records (optional)
        
        # Validate number of guests and offer extra beds if needed
        if num_guests > apartment.capacity:
            extra_beds_needed = num_guests - apartment.capacity     # Calculate extra beds required
            print(f"{extra_beds_needed} extra bed(s) required since the number of guests exceeds apartment capacity.")
            
            # Calculate the number of extra beds required for each night
            nights = length_of_stay  # Number of nights the guest will stay
            min_extra_beds = extra_beds_needed * nights  # Minimum number of extra beds required for all nights

            print(f"Since the guest is staying for {nights} nights, at least {min_extra_beds} extra beds are needed.")
            
            extra_bed_id = "SI6"  # Assuming extra bed product ID according to products.csv file
            extra_bed = self.records.find_product(extra_bed_id)
            
            while True:
                try:
                    # Ask for the number of extra beds (minimum based on the stay)
                    num_extra_beds = int(input(f"How many extra beds do you need (min {min_extra_beds} for {nights} night(s)): "))
                    if num_extra_beds >= min_extra_beds:
                        extra_bed_cost = num_extra_beds * extra_bed.price   # Calculate total cost for extra beds
                        print(f"Total cost for {num_extra_beds} extra bed(s) for {nights} night(s): ${extra_bed_cost:.2f}")
                        
                        # Add extra bed details to the order
                        order.add_product(extra_bed, num_extra_beds)
                        break
                    else:
                        print(f"You need to order at least {min_extra_beds} extra bed(s) for {nights} night(s).")
                except ValueError:
                    print("Invalid input. Please enter a valid integer for the number of extra beds.")

        # Validate car park
        car_park_needed = input("Do you need a car park? (y/n): ")   # Ask if car park is needed
        if car_park_needed.lower() == 'y':
            while True:
                try:
                # Prompt the user for the number of car parks they need
                    car_park_id = "SI1"  # Known car park ID
                    car_park = self.records.find_product(car_park_id)  # Retrieve car park details
                    num_car_parks = input(f"How many car parks do you need (at least {length_of_stay}): ")
                    
        
                    num_car_parks = int(num_car_parks)
                    # Check if the number of car parks is less than the number of nights
                    if num_car_parks < length_of_stay:
                        print(f"You must order at least {length_of_stay} car park(s) for {length_of_stay} night(s).")
                        
                    else:
                        extra_car_park_cost = num_car_parks * car_park.price
                        print(f"Total cost for {num_car_parks} car park(s): ${extra_car_park_cost:.2f}")
                        
                        #Add car park details to the order
                        order.add_productC(car_park, num_car_parks)  # You may adjust this method accordingly
                        break
                except ValueError:
                    print("Invalid input. Please enter a valid integer.")
                    continue
        
        supplementary_items = []
        supplementary_items_cost = 0

        while True:
            supp_item = input("Do you want to add supplementary items? (yes/no): ").strip().lower()
            
            if supp_item == 'no':
                print("Finalizing order...")
                break  # Exit the loop if the user says 'no'
            elif supp_item == 'yes':
                supplementary_id = input("Enter supplementary item ID (or leave blank to finish): ")
                if not supplementary_id:
                    break

                supplementary = self.records.find_product(supplementary_id)
                if supplementary and isinstance(supplementary, SupplementaryItem):
                    quantity = get_valid_quantity()
                    item_cost = supplementary.price * quantity
                    supplementary_items_cost += item_cost
                    # Add supplementary items to the order list AND the supplementary_items list for tracking
                    supplementary_items.append((supplementary, quantity))
                    self.add_product(supplementary, quantity)
                    print(f"Added supplementary item: {supplementary.name}, Quantity: {quantity}, Cost: {item_cost:.2f}")
                else:
                    print("Invalid supplementary item. Please try again.")
            
        # Create order
        supp_item_cost = extra_bed_cost+ extra_car_park_cost + supplementary_items_cost
        apartment_sub_total,original_cost, discount, final_total_cost, earned_reward = order.compute_cost(apartment.price, length_of_stay, supp_item_cost)
        
        guest_name = guest.name 
    
        #save Order to csv
        product_quantities = [f"1 x {apartment_id}"]  # Start with the apartment
        for product, quantity in supplementary_items:
            if quantity > 0:
                product_quantities.append(f"{quantity} x {product.product_id}")  # Add supplementary items from the bundle
        self.records.save_order(guest_name, product_quantities, final_total_cost, earned_reward)


        return num_guests,apartment_id, apartment.name, apartment.price,apartment_sub_total,supplementary_items_cost,supplementary_items,original_cost,discount, final_total_cost, earned_reward

# This Function checks if the guest name is valid
def get_valid_guest_name():
    while True:
        try:
            guest_name = input("Enter guest name: ")
            if not guest_name.isalpha():
                raise InvalidGuestNameError
            return guest_name
            
        except InvalidGuestNameError:
            print("Error: Guest name must contain only alphabet characters. Please try again.")
                
        
# This function checks if the quantity is valid
def get_valid_quantity():
    while True:
        try:
            quantity = int(input("Enter quantity: "))
            if quantity <= 0:
                raise InvalidQuantityError
            return quantity
        except (ValueError, InvalidQuantityError):
            print("Error: Quantity must be a positive integer. Please try again.")


#This function Checks if the check_in check_out dates are valid 
def get_valid_dates():
    while True:
        try:
            check_in_date = input("Enter check-in date (D/M/YYYY): ").strip()
            check_out_date = input("Enter check-out date (D/M/YYYY): ").strip()

            check_in = datetime.strptime(check_in_date, "%d/%m/%Y")
            check_out = datetime.strptime(check_out_date, "%d/%m/%Y")

            # Validate date discrepancies
            if check_in < datetime.now():
                raise DateDiscrepancyError("Check-in date cannot be earlier than booking date.")
            if check_out < datetime.now():
                raise DateDiscrepancyError("Check-out date cannot be earlier than booking date.")
            if check_out < check_in:
                raise DateDiscrepancyError("Check-out date cannot be earlier than check-in date.")
            if check_in == check_out:
                raise DateDiscrepancyError("Check-in date cannot be the same as check-out date.")

            # calculate the length of stay
            length_of_stay = (check_out - check_in).days
            return check_in, check_out, length_of_stay
            
        except ValueError:
            print("Invalid date format. Please enter in D/M/YYYY format.")
        except DateDiscrepancyError as e:
            print(e)


# Guest Class: This class encapsulates all relevant data for a guest, such as their ID, name, reward rate, and redeemable rewards.
# This class is designed to handle all guest-related operations, such as updating rewards, retrieving guest information, and setting custom rates.
class Guest:
    # Initializes a Guest with an ID, name, reward rate, total rewards, and redeem rate.
    # The reward rate (default: 100) and redeem rate (default: 1 point = $1) are given default values for flexibility, allowing easy customization per guest.
    # Rewards will be earned based on the total cost of the order, multiplied by the reward rate.
    def __init__(self, guest_id, name, reward_rate=100, reward=0, redeem_rate=1):
        self.guest_id = guest_id
        self.name = name
        self.reward_rate = reward_rate  # in percentage
        self.reward = reward
        self.redeem_rate = redeem_rate  # 1 point = 1 dollar by default
    
    # Returns the guest's ID.
    def get_ID(self):
        return self.ID
    
    # Returns the guest's name.
    def get_name(self):
        return self.name
    
    # Returns the guest's reward rate
    def get_reward_rate(self):
        return self.reward_rate
    
    # Calculates rewards based on the total cost and the guest's reward rate.
    def get_reward(self, total_cost):
        return round(total_cost * (self.reward_rate / 100))

    def update_reward(self, value):
        # Update the reward points
        self.reward += value

    # Displays the guest's information including ID, name, reward rate, reward points, and redeem rate.
    def display_info(self):
        print(f"Guest ID: {self.guest_id}")
        print(f"Name: {self.name}")
        print(f"Reward Rate: {self.reward_rate}%")
        print(f"Reward Points: {self.reward}")
        print(f"Redeem Rate: {self.redeem_rate} point(s) per $")

    def set_reward_rate(self, rate):   
        self.reward_rate = rate

    def set_redeem_rate(self, rate):     
        self.redeem_rate = rate


# Product Class: This base class represents any purchasable product. It encapsulates core properties like ID, name, price, and quantity.
# Other specific products like ApartmentUnits and SupplementaryItems inherit from this class, ensuring a consistent interface for all product types.
class Product:
    def __init__(self, product_id, name, price,quantity=0):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity

    def get_ID(self):
        return self.ID   # Returns the product's ID.

    def get_name(self):
        return self.name            # Returns the product's name.

    def get_price(self):
        return self.price                # Returns the product's price.
    
    def get_quantity(self):
        return self.quantity
    
    def display_info(self):
        pass  
    

    def __str__(self):
        return f"{self.product_id}, {self.name}, {self.price:.2f}, Quantity: {self.quantity}"             # Returns a string representation of the product including ID, name, price, and quantity.


# ExtraBed Class
class ExtraBed(Product):
    def __init__(self, product_id, name, price):
        super().__init__(product_id, name, price)            # Initializes an ExtraBed, a type of Product with a specific ID, name, and price.

# Bundle Class: Represents a collection of products sold as a bundle. The bundle has a unique price, which is calculated by applying a discount.
# Bundling products is common in businesses, and this approach allows for easily extending the bundle to include more product types.
class Bundle:
    # Initializes a Bundle containing a list of components (products) and calculates its price.
    # Components is a list of (product, quantity) tuples. This was chosen for flexibility and allows multiple products with various quantities.
    def __init__(self, bundle_id, name, components,bundle_price):
        self.bundle_id = bundle_id  # ID starting with "B"
        self.name = name  # Bundle name
        self.components = components  # List of products (IDs and quantities)
        self.bundle_price = bundle_price
        self.price = self.calculate_bundle_price()  # 80% of total price

    # Calculates the total price of the bundle, applying a 20% discount.
    def calculate_bundle_price(self):
        total_price = 0.0
        for product, quantity in self.components:
            total_price += product.price * quantity
        return total_price * 0.8  # Apply 20% discount
    

    def display_bundle(self):
        # Create a dictionary to count occurrences of each product
        component_counts = {}
        for product, quantity in self.components:
            if product.product_id in component_counts:
                component_counts[product.product_id] += quantity
            else:
                component_counts[product.product_id] = quantity
        
        # Format the components display
        component_display = []
        for product_id, count in component_counts.items():
            product = next(p for p, q in self.components if p.product_id == product_id)
            if count > 1:
                component_display.append(f"{count} x {product.product_id}")
            else:
                component_display.append(product.product_id)

        component_details = ", ".join(component_display)
        # Display the bundle info
        print("{:<10} {:<30} {:<50} {:<10.2f}".format(self.bundle_id, self.name, component_details, self.bundle_price))

    def __str__(self):
        return f"{self.bundle_id}, {self.name}, {', '.join([f'{p.bundle_id} x {q}' for p, q in self.components])}, {self.price:.2f}"

#class CarPark 
class CarPark:
    # Initializes a CarPark with an ID, description, and price per hour.
    def __init__(self, id, description, price_per_hour):
        self.id = id
        self.description = description
        self.price_per_hour = price_per_hour

# ApartmentUnit Class (Subclass of Product)
class ApartmentUnit(Product):
    def __init__(self, product_id, name, price, capacity,quantity=1):
        super().__init__(product_id, name, price,quantity)
        self.capacity = capacity   #Maximum number of guests
    
    # Returns the maximum capacity of the apartment unit.
    def get_capacity(self):
        return self.capacity
    
    def display_info(self):
        print(f"Apartment ID: {self.product_id}")
        print(f"Apartment Name: {self.name}")
        print(f"Rate per Night: ${self.price}")
        print(f"Capacity: {self.capacity} guest(s)")


# SupplementaryItem Class (Subclass of Product)
class SupplementaryItem(Product):
    def __init__(self, product_id, name, price):
        super().__init__(product_id, name, price)

    def display_info(self):
        print(f"Item ID: {self.product_id}")
        print(f"Item Name: {self.name}")
        print(f"Price: ${self.price}")

# BundleItem Class (Subclass of Product)
class BundleItem(Product):
    def __init__(self, bundle_id, bundle_name,components, bundle_price):
        super().__init__(bundle_id, bundle_name, components,bundle_price)

    def display_info(self):
        print(f"Bundle ID: {self.bundle_id}")
        print(f"Item Name: {self.bundle_name}")
        print(f"Components: {self.components}")
        print(f"Price: ${self.Bundle_price}")


# Order Class: Represents an order placed by a guest. The design separates product handling and cost calculation into distinct methods to ensure clarity and modularity.
class Order:
    # An order is initialized with a guest, product, and the quantity ordered. 
    # Orders are associated with guest instances and products, ensuring proper linking of data and behavior.
    def __init__(self, guest, product, quantity):
        # Initializes an Order object with a guest, product, and quantity.
        self.guest = guest  # Guest instance associated with the order
        self.product = product  # Product instance being ordered
        self.quantity = quantity # Quantity of the product ordered
        self.records = Records()    # Instance of Records class to handle guest and product records
        self.total = 0  # Total cost of the order 
        
    
    #function to add the car to the list
    def add_productC(self, product, quantity):
        # Adds a CarPark product to the order, dynamically calculating the total cost based on the hourly rate.
        # This method handles the special case of car park products where the price depends on hours parked.
        if isinstance(product, CarPark):
            cost = product.price_per_hour * quantity    # Calculate cost based on hourly rate
            self.products.append({
                'product_id': product.id,  # Store product ID
                'quantity': quantity,      # Store quantity ordered
                'cost': cost            # Store calculated cost
            })
            self.total += cost      # Update total cost
            print(f"Added {quantity} car park(s) ({product.product_id}) to the order for ${cost:.2f}.")
        else:
            print("Invalid product type. Cannot add to order.")

    #Function to compute the total cost and the rewards earned
    def compute_cost(self,apartment_rate, length_of_stay, supplementary_items_cost):
        apartment_sub_total = apartment_rate * length_of_stay
        original_cost = apartment_sub_total + supplementary_items_cost

        # Discount based on reward points (100 points = 1 dollar)
        if self.guest is None:  # Check if guest is None
            print("Error: Guest information is missing.")
            return None, None, None, None, None

        # Discount based on reward points (100 points = 1 dollar)
        discount = min(self.guest.reward // 100, original_cost)

        # Final total cost after discount
        final_total_cost = original_cost - discount

        # Earned rewards
        earned_reward = self.guest.get_reward(final_total_cost)

        return apartment_sub_total,original_cost, discount, final_total_cost, earned_reward


# Records Class used to load products and find records
class Records:
    def __init__(self):
        self.guest_list = [] # Initialize the guests list
        self.product_list = [] # Initialize the products list
        self.bundles=[] # If there are bundles, initialize them too
        self.orders=[]    # Initialize the orders list to store Order objects
        self.guests = self.read_guests('guests.csv')
        self.products = self.read_products('products.csv')
        # self.orders = self.load_orders('orders.csv') 

    #Function to read guests from guests.csv file
    def read_guests(self, filename):
        try:
            with open(filename, 'r') as file:
                for line in file:
                    guest_id, name, reward_rate, reward, redeem_rate = [item.strip() for item in line.strip().split(',')]
                    self.guest_list.append(Guest(guest_id, name, int(reward_rate), int(reward), int(redeem_rate)))
        except FileNotFoundError:
            print(f"File {filename} not found. Exiting program.")
            exit(1)

    #Function to read products from products.csv file and differentiates between apartments, supplementarty items and bundles
    def read_products(self, filename):
        try:
            with open(filename, 'r') as file:
                for line in file:
                    product_data= [part.strip() for part in line.strip().split(',')]
                    if product_data[0].startswith('U'):  # Handle ApartmentUnit
                        product = ApartmentUnit(product_data[0], product_data[1], float(product_data[2]), int(product_data[3]))
                    elif product_data[0].startswith('SI'):  # Handle SupplementaryItem
                        product = SupplementaryItem(product_data[0], product_data[1], float(product_data[2]))
                    elif product_data[0].startswith('B'):  # Handle Bundles
                        bundle_id = product_data[0]
                        bundle_name = product_data[1]
                        bundle_components = product_data[2:-1]
                        bundle_price = float(product_data[-1]) #  Components are between the bundle name and price
                        components = []

                        for component_id in bundle_components:
                        # Find the product by ID in product_list
                            product = next((p for p in self.product_list if p.product_id == component_id), None)
                            if product:
                                # Count occurrences of this product in the component list
                                component_count = bundle_components.count(component_id)
                                components.append((product, component_count))
                                # Remove duplicates from further processing
                                bundle_components = [comp for comp in bundle_components if comp != component_id]
                
                        # Create the Bundle object
                        bundle = Bundle(bundle_id, bundle_name, components, bundle_price)
                        self.bundles.append(bundle)
                    self.product_list.append(product)

                    
        except FileNotFoundError:
            print(f"File {filename} not found. Exiting program.")
            exit(1)
        except ValueError as e:
            print(f"ValueError encountered: {e}")
            exit(1)
    
    #Finds the guest from the list of guests
    def find_guest(self, search_value):
        for guest in self.guest_list:
            if guest.guest_id == search_value or guest.name == search_value:
                return guest
        return None

    #Finds the product from the list of products
    def find_product(self, search_value):
        for product in self.product_list:
            if product.product_id == search_value or product.name == search_value:
                return product
            
        for bundle in self.bundles:
            if bundle.bundle_id == search_value or bundle.name == search_value:
                return bundle
        
        return None
    
    #This function executes If user choice is 2.
    #It add and updates the existing apartment details
    def add_update_apartment(self):
        while True:
            updated = False
            filename = 'products.csv'
            apartment_details = input("Enter apartment details (apartment_ID, rate, capacity) of an apartment to Add/Update: ")

            # Split the input based on commas and strip any extra spaces
            details = apartment_details.split(',')

            # Check if exactly three arguments are provided
            if len(details) != 3:
                print("Invalid input. Please enter exactly three arguments separated by commas: apartment_ID, rate, and capacity.")
                continue

            # Unpack the split values into variables
            apartment_id, rate, capacity = [item.strip() for item in details]
            
            # Try converting rate and capacity to the correct data types
            try:
                rate = float(rate)
                capacity = int(capacity)
            except ValueError:
                print("Invalid rate or capacity. Ensure that rate is a number and capacity is an integer.")
                continue
            
            # Read existing products to find and update the apartment
            with open(filename, 'r') as file:
                lines = file.readlines()

            # Validate apartment ID format: starts with 'u' and has alphanumeric characters after
            if apartment_id.startswith('U') and apartment_id[1:].isalnum():
                with open(filename, 'w') as file:
                    for line in lines:
                        product_data = [part.strip() for part in line.strip().split(',')]
                        if product_data[0] == apartment_id:
                            product_data[2] = str(rate)  # Update rate
                            product_data[3] = str(capacity)  # Update capacity
                            updated = True
                        file.write(', '.join(product_data) + '\n')
                
                if updated:
                    print(f"Apartment {apartment_id} updated successfully.")
                else:
                    print(f"Error: Apartment ID {apartment_id} does not exist.")
                break
            else:
                print("Invalid apartment ID format. Apartment ID should start with 'u' followed by alphanumeric characters. Operation cancelled.")


    #This function executes,if user choice = 3
    # The user can add/update the information of a supplementary item to the dictionary
    def add_update_supplementary_items(self):
        while True:
            updated = False
            filename = 'products.csv'
            
            # Input details for the supplementary item
            item_details = input("Enter supplementary item details (item_ID, rate) to Add/Update: ")
            
            # Split the input based on commas and strip any extra spaces
            details = item_details.split(',')
            
            # Check if exactly two arguments are provided
            if len(details) != 2:
                print("Invalid input. Please enter exactly two arguments separated by commas: item_ID and rate.")
                continue
            
            # Unpack the split values into variables
            item_id, rate = [item.strip() for item in details]
            
            # Try converting rate to a float (for price)
            try:
                rate = float(rate)
            except ValueError:
                print("Invalid rate. Ensure that rate is a number.")
                continue
            
            # Read existing products to find and update the supplementary item
            with open(filename, 'r') as file:
                lines = file.readlines()
            
            # Validate supplementary item ID format: starts with 'SI' and followed by digits
            if item_id.startswith('SI') and item_id[2:].isdigit():
                with open(filename, 'w') as file:
                    for line in lines:
                        product_data = [part.strip() for part in line.strip().split(',')]
                        
                        # Check if the item already exists in the file and update it
                        if product_data[0] == item_id:
                            product_data[2] = str(rate)  # Update rate (price)
                            updated = True
                        file.write(', '.join(product_data) + '\n')
                
                if updated:
                    print(f"Supplementary item {item_id} updated successfully.")
                else:
                    print(f"Error: Supplementary item ID {item_id} does not exist.")
                
                break
            else:
                print("Invalid supplementary item ID format. Item ID should start with 'SI' followed by digits. Operation cancelled.")

    
    #This function executes,if user choice = 4
    # The user can add/update the information of a bundle item to the dictionary
    def add_update_bundle(self):
        
        filename = 'products.csv'  # A dictionary to store bundle information
        while True:
            updated = False
            bundle_details = input("Enter bundle details (bundle_ID, included_apartments, included_supplementary_items, bundle_price): ")

            # Split the input based on commas and strip any extra spaces
            details = bundle_details.split(',')

            # Check if at least four arguments are provided
            if len(details) < 4:
                print("Invalid input. Please enter bundle_ID, at least one apartment, at least one supplementary item, and bundle price.")
                continue

            # Unpack the split values into variables
            bundle_id = details[0].strip()
            bundle_name = details[1].strip()
            components = details[2:-1]  # All components are between the bundle_name and the price
            price = details[-1].strip()  # The last value is the price
        

            # Try converting the price to a float
            try:
                price = float(price)
            except ValueError:
                print("Invalid price. Ensure that price is a number.")
                continue
            
            # Read existing products to find and update the bundle
            with open(filename, 'r') as file:
                lines = file.readlines()
            
            # Validate bundle ID format: starts with 'B' and has alphanumeric characters after
            if bundle_id.startswith('B') and bundle_id[1:].isalnum():
                with open(filename, 'w') as file:
                    for line in lines:
                        product_data = [part.strip() for part in line.strip().split(',')]
                        
                        # Check if the bundle exists in the file and update it
                        if product_data[0] == bundle_id:
                            # Update bundle name, components, and price
                            product_data[1] = bundle_name
                            product_data[2:-1] = components  # Update components
                            product_data[-1] = str(price)  # Update price
                            updated = True
                        
                        # Write the updated data back to the file
                        file.write(', '.join(product_data) + '\n')
                
                if updated:
                    print(f"Bundle {bundle_id} updated successfully.")
                else:
                    print(f"Error: Bundle ID {bundle_id} does not exist.")
                
                # Close the file and exit the loop after updating
                break
            else:
                print("Invalid bundle ID format. Bundle ID should start with 'B' followed by alphanumeric characters. Operation cancelled.")

    #This function executes If user choice is 5.
    #The function adjusts the reward rate.
    def adjust_reward_rate(self):
    # 
    # Adjust the reward rate for all guests.
    # The default reward rate is 100%, meaning each dollar converts to a reward point at a 1:1 ratio.
    # Invalid inputs (non-number, zero, or negative) are handled via exceptions.
    # 
        while True:
            try:
                # Prompt user for a new reward rate
                new_reward_rate = input("Enter the new reward rate (as a percentage, e.g., 100 for 100%): ")
                
                # Attempt to convert the input to a float
                new_reward_rate = float(new_reward_rate)
                
                # Ensure the reward rate is positive and greater than 0
                if new_reward_rate <= 0:
                    raise ValueError("Reward rate must be a positive number greater than 0.")
                
                # Update the reward rate for all guests in the system
                for guest in self.guest_list:  # Assuming 'self.guests' is a list of all guest objects
                    guest.reward_rate = new_reward_rate
                print(f"All guests' reward rate successfully updated to {new_reward_rate}%.")
                
                # Exit the loop after successfully updating
                break
            
            except ValueError as e:
                # Handle invalid inputs
                print(f"Invalid input: {e}. Please enter a valid reward rate.")
    
    #This function executes If user choice is 6.
    #The function is used to adjust the redeem rate
    def adjust_redeem_rate(self):
        while True:
            try:
                new_rate = float(input("Enter the new redeem rate (minimum 1%): "))
                if new_rate < 1:
                    raise ValueError("Rate is too low to be worth claiming.")
            except ValueError as e:
                print(f"Invalid input: {e}. Please enter a valid rate.")
            else:
                # Update redeem rate for all guests
                for guest in self.guest_list:
                    guest.redeem_rate = new_rate
                print(f"Redeem rate updated to {new_rate}% for all guests.")
                break

    #This function executes If user choice is 7.
    #It displays the list of existing guests
    def list_guests(self):
        for guest in self.guest_list:
            guest.display_info()

    #This function executes If user choice is 8.
    #It lists the products from the products file.
    def list_products(self, product_type=None):
        for product in self.product_list:
            #if the product is apartment, display apartment information
            if product_type == "apartment" and isinstance(product, ApartmentUnit):
                product.display_info()
            #if the product is supplementary item, display supplementary item information
            elif product_type == "supplementary" and isinstance(product, SupplementaryItem):
                product.display_info()
        
        #if the product is Bundle, display Bundle information
        if product_type == "Bundle": 
            print("{:<10} {:<30} {:<50} {:<10}".format("ID", "Name", "Components", "Price"))
            print("-" * 100)

            for bundle in self.bundles:
                bundle.display_bundle()

    #This function executes If user choice is 11.
    #the function displays all the existing orders.
    def display_all_orders(self):
        filename = "orders.csv"
        try:
            # Open and read the CSV file
            with open(filename, mode='r') as file:
                csv_reader = csv.reader(file)

                print(f"{'Guest Name':<15} {'Products':<65} {'Total Cost':<15} {'Earned Rewards':<15} {'Order Date Time':>20}")
                print('-' * 140)

                for order in csv_reader:
                    if len(order) < 5:
                        continue  # Skip this row if it doesn't have enough fields
                   
                    guest_name = order[0].strip()  # Guest name

                     # Extract the total cost and rewards earned from the end of the row
                    total_cost = float(order[-3].strip())  # Total cost (always third-to-last)
                    rewards_earned = int(order[-2].strip())  # Earned rewards (always second-to-last)
                    order_date = order[-1].strip()  # Order date/time (always the last field)
            
                     # Products ordered are all fields between guest_name and total_cost
                    products = ', '.join(order[1:-3]).strip()
                    print(f"{guest_name:<15} {products:<65} ${total_cost:<13.2f} {rewards_earned:>10} {order_date:>25}")

        except FileNotFoundError:
            print(f"Error: The file '{filename}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    #This function is used to save orders to csv file once the user finalises the order.
    def save_order(self, guest_name, product_quantities, total_cost, earned_rewards):
    # Create the order timestamp
        order_date_time = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        # Prepare the row data
        row = [guest_name] + product_quantities + [total_cost, earned_rewards, order_date_time]
        
        # Open the CSV file in append mode to add the new order
        try:
            with open('orders.csv', mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(row)
            print(f"Order for {guest_name} saved successfully.")
        except Exception as e:
            print(f"An error occurred while saving the order: {e}")


    #This function is used to load all the order form the csv file
    def load_orders(self, filename):
        orders = []
        try:
            with open(filename, mode='r') as file:
                reader = csv.reader(file)

                for row in reader:
                    if not row or len(row) < 4:  # Ensure the row has enough elements
                        continue

                    guest_name = row[0].strip()  # Remove any leading/trailing whitespace
                    try:
                        total_amount = float(row[-3])  # Assuming total amount is 3rd last value in each row
                    except ValueError:
                        print(f"Invalid total amount for guest {guest_name}: {row[-3]}")
                        continue

                    product_strings = row[1:-3]  # Extract product strings
                    products_ordered = self.parse_products(product_strings)  # Parse product and quantities
                    orders.append({
                        'guest_name': guest_name,
                        'products': products_ordered,
                        'total_amount': total_amount,
                    })
        except FileNotFoundError:
            print(f"Cannot load the order file: {filename}. File not found.")
        except Exception as e:
            print(f"Cannot load the order file.An error occurred: {e}")
        return orders

    #This function is used to parse the orders
    def parse_products(self, product_strings):
        products_ordered = {}
        for product_string in product_strings:
            if 'x' in product_string:
                # Ensure we're splitting at the correct 'x' and the string is well-formed
                try:
                    quantity, product_id = product_string.split('x', 1)  # Split only at the first 'x'
                    quantity = int(quantity.strip())  # Clean up and convert quantity to an integer
                    product_id = product_id.strip()  # Clean up product ID
                    products_ordered[product_id] = quantity
                except ValueError:
                    print(f"Error parsing product: {product_string}")
            else:
                print(f"Invalid product string: {product_string}")
        return products_ordered
    
    #This function executes If user choice is 13.
    #It is used to generate key statistics from the orders
    def generate_key_statistics(self):
        # Top 3 Most Valuable Guests
        guest_totals = {}
        for order in self.orders:
            guest_name = order['guest_name']
            total_amount = order['total_amount']
            if guest_name in guest_totals:
                guest_totals[guest_name] += total_amount
            else:
                guest_totals[guest_name] = total_amount
        
        top_guests = sorted(guest_totals.items(), key=lambda g: g[1], reverse=True)[:3]

        # Calculating total product sales (without defaultdict)
        product_sales = {}  
        for order in self.orders:
            for product_id, quantity in order['products'].items():
                if product_id in product_sales:
                    product_sales[product_id] += quantity
                else:
                    product_sales[product_id] = quantity

        # Store already printed products to avoid repetition
        printed_products = set()

        # Top 3 Most Popular Products
        top_products = []
        for product in sorted(self.product_list, key=lambda p: product_sales.get(p.product_id, 0), reverse=True):
            if product.product_id not in printed_products:
                printed_products.add(product.product_id)
                top_products.append(product)
            if len(top_products) == 3:
                break   #collect only the top 3

        # Writing to stats.txt
        with open("stats.txt", mode='w') as file:
            file.write("Top 3 Most Valuable Guests:\n")
            print("Top 3 Most Valuable Guests:")
            for guest, total in top_guests:
                file.write(f"Guest Name: {guest} , Total Amount: {total:.2f}\n")
                print(f"Guest Name: {guest} , Total Amount: {total:.2f}")
           
            file.write("\nTop 3 Most Popular Products:\n")
            print("\nTop 3 Most Popular Products")
            for product in top_products:
                file.write(f"Product Name: {product.name} , Sold Quantity: {product_sales.get(product.product_id, 0)}\n")
                print(f"Product Name: {product.name} , Sold Quantity: {product_sales.get(product.product_id, 0)}")
        print("Statistics saved to stats.txt")

    #This function executes If user choice is 12.
    #This function displays the guest order history from the existing data
    def display_guest_order_history(self):
        guest_orders = {}
    
        # Read the orders.csv file
        with open('orders.csv', 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            
            for row in csvreader:
                guest_name = row[0].strip()  # Guest name

                 # Extract the total cost and rewards earned from the end of the row
                total_cost = float(row[-3].strip())  # Total cost (always third-to-last)
                rewards_earned = int(row[-2].strip())  # Earned rewards (always second-to-last)
                order_date = row[-1].strip()  # Order date/time (always the last field)
                

                 # Products ordered are all fields between guest_name and total_cost
                products = ', '.join(row[1:-3]).strip()

                # Store each order in a dictionary under the guest's name
                if guest_name not in guest_orders:
                    guest_orders[guest_name] = []
                
                guest_orders[guest_name].append({
                    'products': products,
                    'total_cost': total_cost,
                    'rewards_earned': int(rewards_earned),
                    'order_date': order_date
                })
        
        while True:
            guest_name = input("Enter guest name: ")
            
            if guest_name in guest_orders:
                orders = guest_orders[guest_name]
                
                if not orders:
                    print(f"No order history found for {guest_name}.")
                else:
                    print(f"\nThis is the booking and order history for {guest_name}:\n")
                    print(f"{'Order ID':<10} {'Products Ordered':<55} {'Total Cost':<14} {'Earned Rewards':<15} {'Order Date/Time'}")
                    print("-" * 150)
                    
                    # Loop through each order and print the details
                    for i, order in enumerate(orders, start=1):
                        print(f"Order {i:<8} {order['products']:<55} ${order['total_cost']:<13} {order['rewards_earned']:<15} {order['order_date']}")
                
                break  # Exit after showing the history
            else:
                print(f"No order history found for {guest_name}. Please try again.")


# Operations Class (Main Menu)
class Operations:
    def __init__(self):
        self.records = Records()

        # Set default file names
        guest_file = 'guests.csv'
        product_file = 'products.csv'
        order_file = 'orders.csv'  # Optional order file
        
        # Check if command-line arguments are provided
        if len(sys.argv) > 1:
            if len(sys.argv) == 3 or len(sys.argv) == 4:
                guest_file = sys.argv[1]  # First argument is guest file
                product_file = sys.argv[2]  # Second argument is product file
                if len(sys.argv) == 4:
                    order_file = sys.argv[3]  # Third argument (optional) is order file
            else:
                print("Usage: python script.py <guest_file> <product_file> [order_file]")
                sys.exit(1)
        
        try:
            # Read the mandatory guest and product files
            self.records.read_guests(guest_file)
            self.records.read_products(product_file)
            
            # Optionally load the orders file if present
            if order_file:
                self.records.load_orders(order_file)  # Add this method if not implemented
        except FileNotFoundError as e:
            print(f"Error: {e}")
            print("Cannot load the order file")
            return
        
    #This is the main menu for the user to choose
    def display_menu(self):
        while True:
            print("\nMenu:")
            print("1. Make a booking")
            print("2. Add/Update Apartment Units")
            print("3. Add/Update Supplementary Items")
            print("4. Add/Update Bundles")
            print("5. Adjust the reward rate of all guests")
            print("6. Adjust the redeem rate of all guests")
            print("7. Display existing guests")
            print("8. Display existing apartment units")
            print("9. Display existing supplementary items")
            print("10. Display existing Bundle items")
            print("11. Display All orders")
            print("12.Display a guest order history")
            print("13.Generate key statistics")
            print("14. Exit")

            choice = input("Enter your choice: ")

            if choice == '1':
                self.make_booking()
            elif choice == '2':
                self.records.add_update_apartment()
            elif choice == '3':
                self.records.add_update_supplementary_items()
            elif choice =='4':
                self.records.add_update_bundle()
            elif choice =='5':
                self.records.adjust_reward_rate()
            elif choice =='6':
                self.records.adjust_redeem_rate()
            elif choice == '7':
                self.records.list_guests()
            elif choice == '8':
                self.records.list_products("apartment")
            elif choice == '9':
                self.records.list_products("supplementary")
            elif choice == '10':
                self.records.list_products("Bundle")   
            elif choice == '11':
                self.records.display_all_orders()
            elif choice == '12':
                self.records.display_guest_order_history()
            elif choice == '13':
                self.records.generate_key_statistics()
            elif choice == '14':
                print("Exiting program...")
                break
            else:
                print("Invalid option. Try again.")

    #This function has the logic for the booking process
    def make_booking(self):
        
        guest_name = get_valid_guest_name()   # get the guest name from user and validate
        guest = self.records.find_guest(guest_name)
        self.booking = Booking(guest)

        if not guest:
            print("Guest not found. Creating a new guest.")
            guest_id = input("Enter new guest ID: ")  #If the guest is not in the existing guest lost, create new user ID  
            guest = Guest(guest_id, guest_name)
            self.records.guest_list.append(guest)   #apped the new user Id to the guest list
        
        # Check-in and check-out dates
        check_in, check_out, length_of_stay = get_valid_dates()   #Get the check in, check_out dates and compute the length of stay
        
        # Capture booking date
        booking_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"Booking date: {booking_date}")

        choice = input("Do you want to book a Bundle (B) or proceed with normal booking (N)? ").strip().upper()
        #If the user wants to order a bundle 
        if choice == 'B':
            num_guests,apartment_name,apartment_price, apartment_sub_total, supplementary_items_cost,supplementary_items,original_cost, discount, final_total_cost, earned_reward= self.booking.process_bundle_booking(guest,length_of_stay)
        
        #If the user wants to continue with normal booking
        elif choice == 'N':
            num_guests,apartment_id,apartment_name, apartment_price,apartment_sub_total,supplementary_items_cost,supplementary_items,original_cost,discount, final_total_cost, earned_reward = self.booking.process_normal_booking(guest,length_of_stay)
        else:
            print("Invalid choice. Please select either 'B' for Bundle or 'N' for normal booking.")


    
        # Print the receipt after the order
        print("=" * 65)
        print(f"Guest name: {guest.name}")
        print(f"Number of guests: {num_guests}")  
        print(f"Apartment name: {apartment_name}")
        print(f"Apartment rate: ${apartment_price:.2f} (AUD)")
        print(f"Check-in date: {check_in.strftime('%d-%m-%Y %H:%M:%S')}")
        print(f"Check-out date: {check_out.strftime('%d-%m-%Y %H:%M:%S')}")
        print(f"Length of stay: {length_of_stay} nights")
        print(f"Booking date: {booking_date}")
        print(f"Sub-total: ${apartment_sub_total:.2f} (AUD)")


        
        if supplementary_items_cost > 0:
            print("\nSupplementary items")
            print(f"{'ID':<10} {'Name':<30} {'Quantity':<10} {'Unit Price $':<15} {'Cost $'}")
            
            # Dictionary to store unique supplementary items
            supplementary_summary = {}
            
            for product, quantity in supplementary_items:
                item_id = product.product_id  # Assuming product has an attribute product_id
                name = product.name            # Assuming product has an attribute name
                unit_price = product.price     # Assuming product has an attribute price
                cost = unit_price * quantity    # Calculate cost based on quantity
                # If the item has already been added, update its quantity and cost
                if item_id in supplementary_summary:
                    supplementary_summary[item_id]['quantity'] += quantity
                    supplementary_summary[item_id]['cost'] += cost
                else:
                    supplementary_summary[item_id] = {
                        'name': name,
                        'unit_price': unit_price,
                        'quantity': quantity,
                        'cost': cost
                    }
            for item_id, item_details in supplementary_summary.items():
                name = item_details['name']
                quantity = item_details['quantity']
                unit_price = item_details['unit_price']
                cost = item_details['cost']
                print(f"{item_id:<10} {name:<30} {quantity:<10} ${unit_price:<15.2f} ${cost:.2f}")
        
        print(f"\nSupplementary items sub-total: ${supplementary_items_cost:.2f} (AUD)")
        print("-" * 75)
        print(f"Total cost: ${original_cost:.2f} (AUD)")
        print(f"Reward points to redeem: {guest.reward} (points)")
        print(f"Discount based on points: ${discount} (AUD) ")
        print(f"Final total cost: ${final_total_cost:.2f} (AUD) ")
        print(f"Earned rewards:{earned_reward} (points) ")
        print("\nThank you for your booking!")
        print("We hope you will have an enjoyable stay.")
        print("=" * 65)

        # Update guest rewards
        guest.update_reward(earned_reward)
    
# Run the program
if __name__ == "__main__":
    operations = Operations()
    operations.display_menu()




#DESIGN PROCESS REFLECTION AND ANALYSIS


#Design Process Overview: 
#The design process began with a thorough understanding of the problem requirements in various level. This involved analyzing tasks the program needed, the inputs it would require and the expected output.
# Followed by drafting a rough algorithm to break down the tasks into manageable parts. 
# I then decided to use lists for handling collections of data where order mattered, dictionaries for key-value pair storage. 
# I followed a modular design approach - to create classes and functions that could handle specific tasks independently,  which will make code more readable, maintainable, easy to debug and test.
    
#Code Development:
# After finalising the design, I began by implementing the core components, focusing on the main function and primary logic. I developed code level wise starting with the PASS level meeting all requirements in that level and then continuing the other levels.
#I adopted an iterative approach, incrementally writing and testing each part to ensure correctness. 
#The code was continuously refined for optimization, readability, and robustness, including adding error-handling mechanisms. Once the basic components were built, I integrated them into a cohesive program, ensuring correct interactions.
#The final step involved rigorous testing and debugging to identify and fix any issues, ensuring the program's reliability across various scenarios. I added print statements to debug the program and track the flow of execution.

#The overall structure of the system is based on object-oriented design principles, with each class representing a distinct entity and its associated behavior. The design promotes modularity, scalability, and efficiency.
#There were 7 main classes defined which played a major role in the code
# Operations - handled main code of displaying menu operations and calling each function accordingly.
# Order - handles all order made by the guest
# Guest - handles all the guest information
# Records - handles loading data from files, stores and manages guest and product records
#Booking - handles all the bookings and all the major function are defined here.
#Bundle - fetches all the bundle data from the file and displays bundles
#Products - handles all the products that are purchased by guest 

# Overall Design Approach:
# Object-Oriented Design (OOD): The system follows OOD principles, with each class representing a specific entity (Guest, ApartmentUnit, Product, Booking) and its associated behavior. This promotes modularity, as each class can be updated independently without affecting others.
# Encapsulation: Each class encapsulates its data and behavior, keeping the logic self-contained and focused. For example, the Booking class encapsulates the logic of booking an apartment, while the Records class is solely responsible for managing guest and product records.
# Modular Methods: Each class defines methods that operate on its data, like calculate_total_cost in Booking and add_guest in Records. This keeps operations related to a particular entity within its own class, promoting clean code structure and ease of maintenance.
# Efficiency with Data Structures: The use of dictionaries in the Records class ensures efficient lookups, insertions, and updates. This is important as the system scales and needs to manage more guests, products, and bookings.
# Scalability and Flexibility: The design choices, such as encapsulating data and using modular methods, ensure that the system can easily grow. For example, adding new features like promotional offers, seasonal pricing, or guest preferences can be done without disrupting existing functionality.
# Error Handling and Data Integrity: Methods like add_guest and add_product include checks for duplicate entries, ensuring that the system maintains data integrity.

#Challenges:
# Managing Relationships Between Entities: One of the design challenges was ensuring that different entities (e.g., guests, apartment units, and bookings) could interact seamlessly. This was achieved by maintaining references to the relevant objects (e.g., the guest and apartment within the Booking class).
# Data Validation: It was important to ensure that all data entered into the system was valid. This required careful planning for methods that handle user inputs (e.g., adding a new guest or booking an apartment) to ensure that the system remains robust.