
"""Password generation utilities for the Franklin admin system.

This module provides deterministic password generation based on
user names or existing passwords using a seeded random generator.
"""

import random

def generate_password(password: str) -> str:
    """Generate a new password from an existing password.
    
    Users are issued the first of 100 passwords and can then generate 
    new passwords from their current password using deterministic seeding.
    
    Parameters
    ----------
    password : str
        Current password to generate new password from.
        
    Returns
    -------
    str
        New generated password (8 characters, ASCII 35-90).
        
    Notes
    -----
    The function uses a deterministic seed based on the input password
    combined with a fixed string, ensuring reproducible password generation.
    Password characters are in the ASCII range 35-90 which includes
    symbols, digits, and uppercase letters.
    """
    random.seed(f'{password} - franklin rules!', version=2)
    return ''.join([chr(random.randint(35, 90)) for _ in range(8)])

# def generate_passwords(user_name):
#     """
#     Generate 100 passwords for a user, starting with a new password based 
#     on the user's name.
#     """

#     passwords = []
#     random.seed(f'{user_name} - franklin rules!', version=2)
#     passwords = [new_password(user_name)]
#     for i in range(99):
#         passwords.append(new_password(passwords[-1]))
#     return passwords

# # I should store the current password for each user


# # a user can unlock the password generation module