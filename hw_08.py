from collections import UserDict
import re
from datetime import datetime, date, timedelta
import pickle

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            return f"{e}"
        except ValueError as e:
            return f"{e}"
        except IndexError as e:
            return f"{e}"
        except Exception as e:
            return f"An error occurred: {str(e)}"
    return inner



class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    
class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")
    
class Name(Field):
    def __init__(self, value: str):
        super().__init__(value)

    def __str__(self):
        return f"Name: {self.value}"
		
class Phone(Field):
    def __init__(self, value = None):
        if not re.match(r'^\d{10}$', value):
            raise ValueError("Phone number must be 10 digits")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, birthday_value):
        self.birthday = Birthday(birthday_value)

    def add_phone(self, phone_value):
        phone = Phone(phone_value)
        self.phones.append(phone)

    def remove_phone(self, phone_value):
        for phone in self.phones:
            if phone.value == phone_value:
                self.phones.remove(phone)
                return
        raise ValueError ("Phone number not found.")

    def edit_phone(self, old_phone_value, new_phone_value):
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone_value:
                self.phones[i] = Phone(new_phone_value)
                return
        raise ValueError("Phone number not found.")
    
    def find_phone(self, phone_value):
        for phone in self.phones:
            if phone.value == phone_value:
                return phone
        return None

    def __str__(self):
            return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
        
class AddressBook(UserDict):
    
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name_value):
        return self.data.get(name_value)

    def delete(self, name_value):
        if name_value in self.data:
            del self.data[name_value]
        else:
            raise ValueError("Phone number not found.")
        
    def show_all(self):
        if self.data:
            return "\n".join([str(record) for record in self.data.values()])
        else:
            raise ValueError("No contacts found.")
        
    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()
        end_date = today + timedelta(days=days)
        
        def find_next_weekday(start_date, weekday):
            days_ahead = weekday - start_date.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return start_date + timedelta(days=days_ahead)
        
        def adjust_for_weekend(birthday):
            if birthday.weekday() >= 5:
                return find_next_weekday(birthday, 0)
            return birthday

        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                if today <= birthday_this_year.date() <= end_date:
                    adjusted_birthday = adjust_for_weekend(birthday_this_year.date())
                    upcoming_birthdays.append((record.name.value, adjusted_birthday))
        return upcoming_birthdays
    
    def save_data(book, filename="addressbook.pkl"):
        with open(filename, 'wb') as f:
            pickle.dump(book, f)

    def load_data(filename="addressbook.pkl"):
        try:
            with open(filename, "rb") as f:
                print("Address book loaded successfully!")
                return pickle.load(f)
        except FileNotFoundError:
            print("No existing address book found. Creating a new one.")
            return AddressBook() 

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message
   
@input_error
def change_contact(args, book: AddressBook):
    name, new_phone = args
    record = book.find(name)
    message = f"Contact {name} updated."
    if record is not None:
        record.phones = []
        record.add_phone(new_phone)
        return message
    else:
        raise KeyError("Contact not found.")

@input_error
def show_phone(args, book: AddressBook):
    return book.find(args[0])

@input_error
def show_all(book: AddressBook):
    return book.show_all()
    
@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record is None:
        raise KeyError("Contact not found.")
    record.add_birthday(birthday)
    return "Birthday added."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError("Contact not found.")
    return f"Birthday for {name}: {record.birthday}" if record.birthday else "Birthday not found for this contact."
    
@input_error
def birthdays(book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "Upcoming birthdays:\n" + "\n".join([f"{name}: {birthday.strftime('%d.%m.%Y')}" for name, birthday in upcoming_birthdays])
    return "No upcoming birthdays."
     
def parse_input(command):
    cmd, *args = command.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def main():
    print("Welcome to the assistant bot!")
    book = AddressBook.load_data("address_book.pkl")
    while True:
        user_input = input("Введіть команду: ").strip().lower()
        if not user_input:
            print("Please enter a command.")
            continue
        command, *args = parse_input(user_input)
        try:
            if command == "hello":
                print("How can I help you?")

            elif command == "add":
                print (add_contact(args, book))

            elif command == "change":
                print (change_contact(args, book))    

            elif command == "phone": 
                print(show_phone(args, book))

            elif command == "all":
                print (show_all(book))

            elif command == "add-birthday":
                print(add_birthday(args, book))

            elif command == "show-birthday":
                print(show_birthday(args, book))

            elif command == "birthdays":
                print(birthdays(book))

            elif command is None:  
                print("Please enter a command.")

            elif command in ["close", "exit"]:
                book.save_data("address_book.pkl")
                print("Address book saved successfully!")
                print("Good bye!")
                break
            else:
                print("Unknown command. Try again.")
        except ValueError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()