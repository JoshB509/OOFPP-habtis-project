#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Install Requriements
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


# In[2]:


#Set up the database if it does not already exist

#Define the database name
database_name = "habit_tracker.db"

#establish connection to SQLite
con = sqlite3.connect(database_name)
cur = con.cursor()

#Check if table already exists, if not, create it
cur.execute("""CREATE TABLE IF NOT EXISTS habits(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    frequency TEXT,
    start_date DATE,
    streak INTEGER,
    longest_streak INTEGER,
    reminder_time TEXT,
    last_update_date DATE
)""")


con.commit()


# In[3]:


#### Create the class Habit - all actions are methods of this class
class Habit:
    def __init__(self, database_name):
        self.database_name = database_name

        #This method checks for any habits that have not been updated that are due today and prints them.
    def get_todays_reminders(self):
        con = sqlite3.connect(self.database_name)
        cur = con.cursor()
        
        #Fetch habits that need updating today along with their reminder times
        today_str = datetime.now().date().strftime("%Y-%m-%d")
        cur.execute("SELECT name, reminder_time FROM habits WHERE date(last_update_date) < ? OR last_update_date IS NULL", (today_str,))
        reminders = cur.fetchall()

        con.close()
        return reminders
   
        #This method walks the user through a CLI to collect the data that will be used to create a new habit
    def add_new_habit(self):
        #Prompt user for habit name
        name = input("Enter the name of your new habit: ")

        #Promt user for categories selection
        categories = ['Health', 'Education', 'Fitness', 'Personal Development', 'Professional Skills', 'Hobby']
        print("Select the category of your new habit:")
        
        #Print the categories on screen with a nnumber
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category}")
        
        #Call a method that prompts the user for a number input and checks if it is a valid input, if so it stores it
        category_number = self.get_user_selection(len(categories))
        category = categories[category_number - 1]

        #Promt user for frequency selection
        frequencies = ['Daily', 'Weekly']
        print("Select the frequency of your new habit:")
        
        #Print the frequency options on screen
        for i, frequency in enumerate(frequencies, 1):
            print(f"{i}. {frequency}")
        
         #Call a method that prompts the user for a number input and checks if it is a valid input, if so it stores it
        frequency_number = self.get_user_selection(len(frequencies))
        frequency = frequencies[frequency_number - 1]

        #Promt user for reminder time selection by calling a method
        reminder_time = self.get_valid_time("Enter a reminder time for your new habit (HH:MM): ")

        #Define other details that are default and don't need user input
        start_date = datetime.now().date()
        streak = 0
        longest_streak = 0
        last_update_date = datetime.now().date()

        #Pass all captured data to a method that pushes habit to the database
        self.insert_habit(name, category, frequency, start_date, streak, longest_streak, reminder_time, last_update_date)

        #this method will prompt user to make an input then validate that input
    def get_user_selection(self, options_count):
        while True:
            try:
                selection = int(input("Enter your choice (number): "))
                if 1 <= selection <= options_count:
                    return selection
                else:
                    print(f"Please enter a number between 1 and {options_count}.")
            except ValueError:
                print("Invalid input. Please enter a number.")
                
        #this method will prompt user to make an input then validate that input
    def get_valid_time(self, prompt):
        while True:
            time_str = input(prompt)
            try:
                valid_time = datetime.strptime(time_str, "%H:%M").time()
                return valid_time.strftime("%H:%M")
            except ValueError:
                print("Invalid time format. Please use HH:MM format.")

        #this takes the data collected from the Add_new_habit method and pushes it to the data base
    def insert_habit(self, name, category, frequency, start_date, streak, longest_streak, reminder_time, last_update_date):
        
        #Connect to the database
        con = sqlite3.connect(self.database_name)
        cur = con.cursor()

        #Insert new habit
        cur.execute("""INSERT INTO habits (name, category, frequency, start_date, streak, longest_streak, reminder_time, last_update_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", 
                    (name, category, frequency, start_date, streak, longest_streak, reminder_time, last_update_date))

        #commit changes and close connection
        con.commit()
        con.close()
        print(f"New habit '{name}' added successfully.")

        #this method updates the streak. it gets all habits, asks the user which to update then pushes an update to the database
    def update_streak(self):
        
        #Connect to the database
        con = sqlite3.connect(self.database_name)
        cur = con.cursor()

        #Fetch and display all habits with their IDs
        cur.execute("SELECT id, name FROM habits")
        habits = cur.fetchall()
        
        #if not habits found, print error message
        if not habits:
            print("No habits found.")
            con.close()
            return
       
        #print the habits
        for habit in habits:
            print(f"{habit[0]}. {habit[1]}")
        
        #Ask the user to select a habit to update
        habit_id = input("Enter the number of the habit you want to update: ")
        try:
            habit_id = int(habit_id)
            selected_habit = next((habit for habit in habits if habit[0] == habit_id), None)
            if not selected_habit:
                raise ValueError("Invalid habit selected.")
        except ValueError as e:
            print("Invalid input. Please enter a valid habit number.")
            con.close()
            return
        
        #Get the selected habit's last update date and current streak
        cur.execute("""SELECT last_update_date, streak, longest_streak FROM habits WHERE id = ?""", (habit_id,))
        habit_data = cur.fetchone()
        
        #grab the streak information from the database, check what is returned is not empty, and grab the last update date in the right format
        if habit_data:
            last_update_date, current_streak, longest_streak = habit_data
            last_update_date = datetime.strptime(last_update_date, '%Y-%m-%d').date() if last_update_date else None
            today = datetime.now().date()
            
            #If the streak was updated on time, then update it else reset
            if last_update_date and (today - last_update_date).days == 1:
                new_streak = current_streak + 1
            else:
                new_streak = 1  #Reset streak if more than a day has passed or if never updated

            #Update the longest streak if the new streak is longer
            longest_streak = max(new_streak, longest_streak)
            
            #Update the habit in the database
            cur.execute("""UPDATE habits SET streak = ?, longest_streak = ?, last_update_date = ? WHERE id = ?""",
                        (new_streak, longest_streak, today, habit_id))
            con.commit()
            print(f"Habit '{selected_habit[1]}' updated. New streak: {new_streak}, Longest streak: {longest_streak}.")
        else:
            print("Habit not found.")
    
        con.close()

        #This prints all habit data from the database, this method is called as part of the analytics method
    def print_all_habits(self):
        #Connect to the database
        con = sqlite3.connect(self.database_name)
        cur = con.cursor()

        #Fetch all rows from the habits table
        cur.execute("SELECT * FROM habits")
        habits = cur.fetchall()

        #Check if there are any habits to display, if so run a loop to print all the data
        if habits:
            print(f"{'ID':<3} {'Name':<20} {'Category':<15} {'Frequency':<10} {'Start Date':<10} "
                  f"{'Streak':<6} {'Longest Streak':<13} {'Reminder Time':<12} {'Last Update Date':<15}")
            print("-" * 105)  #Print a divider line
            for habit in habits:
                habit = [str(item) if item is not None else 'N/A' for item in habit]  #Convert None to 'N/A' so more easily human readable
                print(f"{habit[0]:<3} {habit[1]:<20} {habit[2]:<15} {habit[3]:<10} {habit[4]:<10} "
                      f"{habit[5]:<6} {habit[6]:<13} {habit[7]:<12} {habit[8]:<15}")
        else:
            print("No habits found.")
            
        con.close()

        #this method will return the longest active streak. It is called as part of the analytics fundtion
    def get_detailed_current_longest_streak(self):
        con = sqlite3.connect(self.database_name)
        cur = con.cursor()
        
        #Query to find the maximum current streak and the habits that have this streak incase multiple habits have the same streak
        cur.execute("""SELECT name, category, streak FROM habits WHERE streak = (SELECT MAX(streak) FROM habits)""")
        habits_with_max_streak = cur.fetchall()

        #a loop that prints each habit with the streak
        if habits_with_max_streak:
            print("Habits with the current longest streak:")
            for habit in habits_with_max_streak:
                print(f"Name: {habit[0]}, Category: {habit[1]}, Current Streak: {habit[2]}")
        else:
            print("No habits found or no streaks have been started.")
            cur = con.cursor()

        #this method will return the longest streak ever achieved. It is called as part of the analytics fundtion
    def get_detailed_historical_longest_streak(self):
        con = sqlite3.connect(self.database_name)
        cur = con.cursor()
        
        #Query to find the maximum historical longest streak and the habits that have this streak
        cur.execute("""SELECT name, category, longest_streak FROM habits WHERE longest_streak = (SELECT MAX(longest_streak) FROM habits)""")
        habits_with_max_longest_streak = cur.fetchall()

        #a loop that prints each habit with the streak
        if habits_with_max_longest_streak:
            print("Habits with the historical longest streak:")
            for habit in habits_with_max_longest_streak:
                print(f"Name: {habit[0]}, Category: {habit[1]}, Longest Streak: {habit[2]}")
        else:
            print("No habits found or no streaks have been recorded.")
        
        #this method creates a graph to display the habits by category, this is called as part of the analytics function
    def plot_habits_by_category(self):
        
        con = sqlite3.connect(self.database_name)
        cur = con.cursor()

        #Fetch categories and counts of all habits
        cur.execute("SELECT category, COUNT(*) FROM habits GROUP BY category")
        habits_data = cur.fetchall()

        #close the connection
        con.close()

        #Unpack the data into two lists for plotting
        if habits_data:
            categories, counts = zip(*habits_data)

            #Create a bar graph using mat plot lib
            plt.figure(figsize=(10, 6))
            plt.bar(categories, counts, color='skyblue')
            plt.xlabel('Category')
            plt.ylabel('Number of Habits')
            plt.title('Habits by Category')
            plt.xticks(rotation=45)
            plt.tight_layout()  #Adjust layout to make room for the rotated x-axis labels
            
            #Show the plot
            plt.show()
        else:
            print("No habits found to plot.")
        
        #This method will call all the relevant methods for the analytics functions
    def show_analytics(self):
        print("\n--- Analytics Overview ---")
        self.get_detailed_current_longest_streak()
        self.get_detailed_historical_longest_streak()
        self.plot_habits_by_category()
        self.print_all_habits()  
 
        #This method walks the user through a CLI tutorial. It explains each step and simulates it
    def tutorial(self):
        print("Welcome to the Habit Tracker Tutorial!\n")
        
        #Introduction to the Habit Tracker
        print("Introduction to the Habit Tracker:")
        print("The Habit Tracker is a tool designed to help you build and maintain positive habits. "
              "By allowing you to set, track, and analyze your daily and weekly habits, "
              "the tracker serves as a personal accountability partner. Whether your goals "
              "are related to fitness, learning, mindfulness, or any other area of personal growth, "
              "tracking your progress helps increase motivation, reinforces consistency, and "
              "provides insightful analytics on your journey towards self-improvement.\n")
        
        print("In this tutorial, we'll walk you through the key features of the Habit Tracker, including:")
        print("- How to add new habits.")
        print("- How to update your habit progress.")
        print("- Viewing analytics to understand your habit patterns.")
        print("- And more tips to get the most out of your habit tracking experience.\n")

        print("\nAdding a New Habit:")
        print("Let's walk through the process of adding a new habit to your tracker. "
              "For this example, we'll add a habit called 'Morning Jog', categorized under 'Fitness', "
              "that you plan to do daily at 07:00 AM.\n")
        
        #Walk the user through creating the 'Morning Jog' habit. Each variable prompts the user to make the correct input
        name = self.prompt_user_input("Enter the name of your new habit (example: Morning Jog): ", "Morning Jog")
        category = self.prompt_user_input("Enter the category of your new habit (example: Fitness): ", "Fitness")
        frequency = self.prompt_user_input("Enter the frequency of your new habit (example: Daily): ", "Daily")
        reminder_time = self.prompt_user_input("Enter a reminder time for your new habit (example: 07:00 AM): ", "07:00 AM")

        #Add the user input to the database as well as a second example 
        self.insert_habit(name, category, frequency, datetime.now().date(), 0, 0, reminder_time, datetime.now().date())
        self.insert_habit("Learn Python with IU", "Professional Skills", "Weekly", datetime.now().date(), 0, 0, reminder_time, datetime.now().date())
            
        #Explain to the user they just made a habit and the next steps they will now do
        print(f"\nGreat! You've just added the following habit to your tracker:")
        print(f"Name: {name}, Category: {category}, Frequency: {frequency}, Reminder Time: {reminder_time}\n")
        print("I've also added an additional habit to showcase the analytics with the following details:")
        print("Name: Learn Pythong with IU, Category: Personal Development, Frequency: Weekly, Streak:0")
        print("Now let's move on to updating your habit progress and exploring analytics...")

        print("\nUpdating a Habit:")
        print("Now that you've added your a habit, let's simulate marking it as completed for today.")
        print("[1] Morning Jog")
        print("[2] Learn Python with IU")
        
        #Ask the user to select the correct habit, and validate their input
        user_input = input("When updating a habit, you will see the list of habits (like above) for your selection, in this example, type '2'")
        while user_input != "2":
            print("When updating a habit, you will see the list of habits for your selection, in this example, type '2'")
            user_input = input("Please type in '2' and press Enter: ")

        #Push their selection to the database. This is a simulation so I can just hard-code the values
        con = sqlite3.connect(database_name)
        cur = con.cursor()
        update_sql = """
        UPDATE habits
        SET streak = 1, longest_streak = 1, last_update_date = ?
        WHERE name = 'Learn Python with IU'
        """
        cur.execute(update_sql, (datetime.now().date(),))

        #Commit the changes to the database
        con.commit()
       
        print("Habit 'Learn Python with IU' updated successfully.")

        #Close the database connection
        con.close()      
        
        #print the next steps of the tutorial
        print("Finally, the Analytics function will give you details to help you succeed")
        print("It will tell you the currect highest streak, the longest historical streak, a graphical view of habits by category as well as all details of all habits")
        print("The tutorial will end now, thank you for taking it. Come back any time if there is still something you want to learn. Below are you analytics")
        
        #Call the analytics method
        self.show_analytics()
        
        con = sqlite3.connect(database_name)
        cur = con.cursor()

        #SQL to delete the bottom two rows based on the highest IDs. This deletes the simulated habits from the DB. It picks the bottom two rows incase the user already has habits in the DB
        delete_sql = """
        DELETE FROM habits
        WHERE id IN (
            SELECT id FROM habits
            ORDER BY id DESC
            LIMIT 2
        )
        """
        cur.execute(delete_sql)

        con.commit()

        print(f"{cur.rowcount} rows deleted successfully.")

        con.close()
        
        #this method validates the user input. This action is performed many times so it is more efficient to make it a method
    def prompt_user_input(self, prompt_text, expected_answer):
        user_input = input(prompt_text)
        while user_input.lower() != expected_answer.lower():
            print(f"Oops! It looks like you entered '{user_input}' which doesn't match the expected '{expected_answer}'. Let's try that again.")
            user_input = input(prompt_text)
        return user_input
  
        #Method to show the CLI menu to the user
    def show_menu(self):
        print("\nMain Menu:")
        print("1. Add Habit")
        print("2. Update Habit")
        print("3. Analytics")
        print("4. Tutorial")
        print("5. Exit")

#this executes on start up. It sets the inital parameters, then opens the CLI and calls the methods as requested
def main():
    
    #define parameters
    database_name = "habit_tracker.db"
    habit_tracker = Habit(database_name)

    print("Welcome to the Habit Tracker CLI!")
  
    #Show today's reminders by calling the method
    reminders = habit_tracker.get_todays_reminders()
    if reminders:
        print("\nHabits to update today:")
        for name, time in reminders:
            print(f"- {name} (Reminder set for {time})")
    else:
        print("No habits need updating today.")

    while True:
        
        #call the show menu method and get the user input then call the requested method. This is the main loop of the CLI
        habit_tracker.show_menu()
        choice = input("Enter your choice: ")
        
        if choice == "1":
            habit_tracker.add_new_habit()
        elif choice == "2":
            habit_tracker.update_streak()
        elif choice == "3":
            habit_tracker.show_analytics()
        elif choice == "4":
            habit_tracker.tutorial()
        elif choice == "5":
            print("Exiting the Habit Tracker CLI. Have a great day!")
            break
        else:
            print("Invalid choice, please select a valid option.")

if __name__ == "__main__":
    main()



# In[ ]:





# In[ ]:




