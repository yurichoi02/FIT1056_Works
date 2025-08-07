# FIT1056
# Week 2 Applied Exercises
# Sequences

# The following lists are defined for you:

months = ["January", "February", "March", "April", "May", "June", "July", 
          "August", "September", "October", "November", "December"]

days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", 
                "Saturday", "Sunday"]

# Based on calendar year 2024
num_days_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

### Indexing
# Exercise 1a: Use indexing to retrieve the current calendar month 
# and assign this to a variable.

current_month_index = 7
current_month_name = months[current_month_index]


# Exercise 1b: Use indexing to retrieve the total number of days in
# the current calendar month, and assign this to (another) variable.

num_days_in_current_month = num_days_in_month[current_month_index]

### Slicing
# Exercise 2a: Retrieve the first 6 months of the calendar year.

first_six_months = months[0:6]

# Exercise 2b: Retrieve the weekends of a calendar week.

weekend_days = days_of_week[::6]

### Concatenation and Repetition
# Exercise 3a: Using concatenation and slicing, obtain a list of
# each day of the week for the next 7 days, starting from tomorrow.
# For example, if today is Thursday, the list should be:
# ["Friday", "Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]

next_7_days = days_of_week[:]

# Exercise 3b: Using repetition, obtain a list of each day of the week
# for the next 21 days, starting from tomorrow.
# You may use any obtained values from previous exercise parts (Hint: 3a).

next_21_days = days_of_week * 3

### Functions involving sequences
# Exercise 4a: Verify that we have correctly identified 12 months in the 
# "months" list and 7 days in the "days_of_week" list.

def verify_list_elements(list_to_check, expected_count, description):
    """
    Checks if a list contains the correct number of elements and prints the result.

    Args:
        list_to_check: The list to be verified.
        expected_count: The integer number of elements the list should have.
        description: A string describing the list for the printout.
    """
    actual_count = len(list_to_check)

    if actual_count == expected_count:
        print(f"SUCCESS: The '{description}' list is valid.")
        print(f"(Expected: {expected_count}, Found: {actual_count})")
    else:
        print(f"FAILURE: The '{description}' list is invalid.")
        print(f"(Expected: {expected_count}, Found: {actual_count})")
    print("-" * 50) # Separator

# Exercise 4b: Verify that the list obtained in Exercise 3a contains 
# exactly 7 elements, and the list obtained in Exercise 3b contains 
# exactly 21 elements.

print("---Verifying List Integrity---")
verify_list_elements(months, 12, "Months of the Year")
verify_list_elements(num_days_in_month, 12, "Days in each Month")
verify_list_elements(days_of_week, 7, "Days of the Week")
print ('\n')

### Methods involving sequences
# Exercise 5a: Using the given variable below, obtain the index of the 
# current month in the "months" list. Do NOT use the index defined in Exercise 1.
cur_month_str = "August"  # change it to "August" if your Applied class falls on Thursday or Friday this week

print(f"The index of the current month is {current_month_index}")
print ('\n')

# Exercise 5b: Using the given variable above (cur_month_str), return a
# string with the current month in all uppercase
# e.g. "JULY"
print(str(cur_month_str).upper())
print ('\n')

# Exercise 5c: Using the list of names defined below, create a name 
# and add this name to the list.
names = ["Adam", "Beth", "Charlie", "Daisy", "Eve"]

new_name = "Lily"
names.append(new_name)
print(names)
print ('\n')

### Splitting and Joining Strings
# Exercise 6: Print a proper sentence that tells the reader what the days
# of a calendar week are. Remember to include space(s), comma(s) and 
# full stop(s) where necessary.
# (Optional challenge to include "and" before the last item)
sentence_start = "The months of a calendar year are "
months = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

if len(months) > 1:
    sentence = sentence_start + ", ".join(months[:-1]) + " and " + months[-1] + "."
else:
    sentence = sentence_start + months[0] + "."

print(sentence)
print ('\n')

sentence_start = "The days of a calendar week are "
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", 
                "Saturday", "Sunday"]

if len(days) > 1:
    sentence = sentence_start + ", ".join(days[:-1]) + " and " + days[-1] + "."
else:
    sentence = sentence_start + days[0] + "."

print(sentence)