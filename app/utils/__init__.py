def process_role(role: str) -> str:
    if role == 'nan' or not role.strip():
        return 'employee'  # Default role
    return role.replace(" ", "_").lower()

def get_initials(input_string: str) -> str:
    # Check if the input string has no spaces and no hyphens
    if " " not in input_string and "-" not in input_string:
        return input_string.upper()  # Return as it is if no spaces or hyphens

    # Split the string into words, including hyphenated parts as separate words
    words = input_string.replace("-", " ").strip().split()
    # Get the first letter of each word and join them
    initials = ''.join(word[0] for word in words if word)
    return initials.upper()  # Return in uppercase
