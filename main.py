from collections import UserDict
from functools import wraps
from datetime import datetime, timedelta
import pickle
from abc import ABC, abstractmethod

class UserInterface(ABC):
    @abstractmethod
    def display_message(self, message):
        pass
    
    @abstractmethod
    def get_user_input(self, inp):
        pass

    @abstractmethod
    def help(self):
        pass

class ConsoleInterface(UserInterface):
    def display_message(self, message):
        print(message)
    
    def get_user_input(self, inp):
        return input(inp)
    
    def help(self):
        return print("""add
change
phone
all
add-birthday
show-birthday
birthdays
help
exit, close""")

class Field:
    def __init__ (self, value):
        self.value = value
    
    def __str__ (self):
        return str(self.value)

class Name (Field):
    def __init__(self, value):
        super().__init__(value)
        if not value:
            raise ValueError("Name cannot be empty!")

class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be 10 digits.")

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)
        def __str__(self):
            return self.value

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    
    def __str__(self):
        phones_str = '; '.join(str(phone) for phone in self.phones)
        return f"Contact name: {self.name.value}, phones: {phones_str}"
    
    def add_phone(self, phone):
        self.phones.append(Phone(phone))
    
    def remove_phone(self, phone):
        self.phones = [phon for phon in self.phones if phon.value != phone]
    
    def edit_phone(self, old_phone, new_phone):
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError(f"Phone number {old_phone} not found!")
    
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None
    
    def add_birthday(self, birthday):
        if not self.birthday:
            self.birthday = Birthday(birthday)
        else:
            raise ValueError("Birthday alreadu set.")
    
    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = datetime.now()
        next_birthday = self.birthday.value.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days


class AddressBook(UserDict):
    def __init__(self):
        super().__init__()
    
    def __str__(self):
        return '\n'.join(str(record) for record in self.data.values())
    
    def add_record(self, record):
        self.data[record.name.value] = record
    
    def find(self, name):
        return self.data.get(name, None)
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]
    
    def find_by_phone(self, phone):
        for record in self.data.values():
            for p in record.phones:
                if p.value == phone:
                    return record
        return None
    
    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.now().date()

        for record in self.data.values():  # Використовуємо self.data.values(), щоб ітерувати через контакти
            if record.birthday:
                birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                next_birthday = birthday_date.replace(year=today.year)
                if next_birthday < today:
                    next_birthday = next_birthday.replace(year=today.year + 1)

                days_to_birthday = (next_birthday - today).days
                if days_to_birthday <= 7:
                    greeting_day = self._adjust_for_weekend(next_birthday)
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "birthday": greeting_day.strftime("%d.%m.%Y")
                    })
        return upcoming_birthdays


    @staticmethod
    def _adjust_for_weekend(date):
        weekday = date.weekday()
        if weekday == 5:
            return date + timedelta(days = 2)
        elif weekday == 6:
            return date + timedelta(days = 1)
        return date


def input_error(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return(func(*args, *kwargs))
        except ValueError:
            return "Error: Give me name and phone please."
        except KeyError:
            return "Error: Contact not found."
        except IndexError:
            return "Error: Insufficient arguments provided."
    return inner

@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book):
    name, phone = args
    record = book.find(name)
    if record:
        record.add_phone(phone)
        return f"Phone '{phone}' added to contact '{name}' successfully."
    else:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return f"Contact '{name}' added successfully with phone '{phone}'."

@input_error
def change_contact (args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        return f"Error: Contact with name '{name}' not found."
    try:
        record.edit_phone(old_phone, new_phone)
        return f"Contacts '{name}' updates successfully."
    except ValueError as e:
        return str(e)

@input_error
def show_phone (args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        return f"Error: Contact with name '{name}' not found."
    return f"Phones for {name}: {', '.join(str(phone) for phone in record.phones)}"

@input_error
def show_all (book):
    if not book.data:
        return "No contacts found."
    return str(book)

@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if not record:
        return f"Error: Contact with name '{name}' not found."
    try:
        record.add_birthday(birthday)
        return f"Birthday for '{name}' added successfully."
    except ValueError as e:
        return str(e)

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        return f"Contact with name '{name}' not found."
    if not record.birthday:
        return f"Contact '{name}' has no birthday set."
    return f"Contact '{name}' has birthday on {record.birthday}"

@input_error
def birthdays(book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays in the next 7 days."
    result = []
    for entry in upcoming:
        result.append(f"{entry['name']}: {entry['birthday']}")
    return "\n".join(result)

def save_data(book, filename = "addressbook.pkl"):
    with open(filename, 'wb') as f:
        pickle.dump(book,f)

def load_data(filename = "addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main(book, us):
    us.display_message("Welcome to the assistant bot")
    while True:
        user_input = us.get_user_input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            us.display_message("Good bye!")
            save_data(book)
            break

        elif command == "hello":
            us.display_message("How can I help you?")
        
        elif command == "add":
            us.display_message(add_contact(args, book))
            save_data(book)

        elif command == "change":
            us.display_message(change_contact(args, book))
            save_data(book)
        
        elif command == "phone":
            us.display_message(show_phone(args, book))

        elif command == "all":
            us.display_message(show_all(book))
        
        elif command == "add-birthday":
            us.display_message(add_birthday(args, book))
            save_data(book)
        
        elif command == "show-birthday":
            us.display_message(show_birthday(args, book))
        
        elif command == "birthdays":
            us.display_message(birthdays(book))
        
        elif command == "help":
            us.help()
        
        else:
            us.display_message("Invalid command")

if __name__ == "__main__":
    book = load_data()
    us = ConsoleInterface()
    main(book, us)