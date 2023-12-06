from sys import exit # Import Exit Code
import json # Import Json Utils
from supabase import create_client, Client # Import Supabase
import bcrypt

try:
    with open('config.json') as config_file:
        config = json.load(config_file)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading configuration file. Make sure the file exists and contains valid JSON: {e}")
    exit()

url = config['supabase']['url']
key = config['supabase']['key']

supabase = create_client(url, key)

tabelname = "test" # Table to use
forbiddensearch = config['supabase']['searchhide'] # Hidden Persons
response = None
loggedin = False


def search(): # Search Function
    criteria = input("Search Last Name, First Name, or City? (Last, First, City) >>> ").capitalize() # Input Column to search
    if criteria not in ["Last", "First", "City"]: # Check Input
        print("Error: Invalid search criteria. Please enter Last, First, or City.")
        return

    value = input(f"Enter {criteria} >>> ") # Ask Search Criteria

    try:
        response = supabase.table(tabelname).select('id', 'first', 'last', 'city', 'notes').eq(criteria.lower(), value).neq(forbiddensearch, True).execute() # DB Search Call
    except Exception as e:
        print(f"Error executing search: {e}")
        return       

    if response.data:
        print("Search Results:")
        for row in response.data:
            print(row)
    else:
        print("No matching records found.")

def create(): # Create Function
    firstname = input("Enter First Name >>> ") 
    lastname = input("Enter Last Name >>> ")
    city = input("Enter City >>> ")
    # Create Inputs

    try:
        response, count = supabase.table(tabelname).insert({"first": firstname, "last": lastname, "city": city}).execute() # DB Create Call
    except Exception as e:
        print(f"Error creating a new record: {e}")
        return
  
    try:
        if response and response[1] and isinstance(response[1], list):
            data = response[1]
            if data:
                print("Record successfully added:")
                for row in data:
                    print(row)
            else:
                print("Failed to add the record.")
        else:
            print("Unexpected response format.")
    except (IndexError, ValueError) as e:
        print(f"Error processing response: {e}")
        return
        
    print(f"{count} rows inserted.") # Print Inserted rows

def login():
    print("Login:")
    lastname = input("Your Last Name >>>")
    id = input("Your ID >>>")

    try:
        response = supabase.table(tabelname).select('pass').eq('last', lastname).eq('id', id).execute() # DB Search Call
        hased = response.data[0]['pass']
    except Exception as e:
        print(f"Error with Last Name or ID: {e}") 
    if hased == '-':
        salt = bcrypt.gensalt()

        print("You have no Password! \n")
        newpass = input('Enter New Password >>>')
        password = bcrypt.hashpw(newpass.encode('utf-8'), salt)
        response, count = supabase.table(tabelname).update({'pass': password}).eq('last', lastname).execute()
        print("Password Updatet!")
    else:
        password = input("Enter Password >>>")
        bcrypt.checkpw(password, hased)
        




def main(): # Main CLI Function
    login()
    while True:
        action = input("Enter 'Search', 'Create', or 'Quit' to exit >>> ").capitalize() # Input what to do
        
        if action == "Search": # Check if Search
            search()
        elif action == "Create": #Check if Create
            create()
        elif action == "Quit": # Check if Quit
            print(" \n \nExiting the program. Goodbye!")
            exit() # Quit
        else: # Invalid Entry Check
            print("Error: Invalid action. Please enter Search, Create, or Quit.") 

if __name__ == "__main__": 
    main()