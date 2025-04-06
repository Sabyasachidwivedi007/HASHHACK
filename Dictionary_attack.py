import bcrypt

# Get user input for the hashed password
hashed_password = input("Enter the hashed password: ").encode('utf-8')

# Open and read wordlist file
try:
    with open("wordlist.txt", "r") as file:
        words = file.read().splitlines()  # Read each line into a list
except FileNotFoundError:
    print("Error: wordlist.txt not found!")
    exit()

# Try to match hashed password with wordlist
for word in words:
    if bcrypt.checkpw(word.encode('utf-8'), hashed_password):
        print(f"Password found: {word}")
        break
else:
    print("Password not found in dictionary.")
