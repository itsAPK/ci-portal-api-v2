def process_role(role: str) -> str:
    if role == 'nan' or not role.strip():
        return 'employee'  # Default role
    return role.replace(" ", "_").lower()