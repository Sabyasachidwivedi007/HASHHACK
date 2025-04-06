import bcrypt

# Ask user for a password
password = input("Enter a password to hash: ").encode('utf-8')

# Generate a salted hash
hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

print("Hashed Password: {hashed_password.decode()}")
