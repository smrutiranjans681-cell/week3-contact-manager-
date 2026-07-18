import json
import re
import csv
import os
from datetime import datetime

# File Configuration Constants
DATA_FILE = "contacts_data.json"
BACKUP_FILE = "contacts_data_backup.json"
EXPORT_FILE = "contacts_export.csv"


def validate_phone(phone: str) -> tuple[bool, str | None]:
    """
    Validates phone number format.
    Accepts international formats, strips out formatting, 
    and verifies if the digit length falls between 10 and 15 digits.
    """
    digits = re.sub(r'\D', '', phone)
    if 10 <= len(digits) <= 15:
        return True, digits
    return False, None


def validate_email(email: str) -> bool:
    """Validates email format using regex pattern."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def save_to_file(contacts: dict):
    """Saves the current contacts structure to a JSON file and handles backups."""
    try:
        # Create a backup of the previous file if it exists
        if os.path.exists(DATA_FILE):
            os.replace(DATA_FILE, BACKUP_FILE)
            
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(contacts, f, indent=4)
        print(f"✅ Contacts saved to {DATA_FILE}")
    except IOError as e:
        print(f"❌ Error saving contacts data: {e}")


def load_from_file() -> dict:
    """Loads contact structure from JSON. Recovers from backup if crash occurs."""
    if not os.path.exists(DATA_FILE):
        if os.path.exists(BACKUP_FILE):
            print("⚠️ Primary file missing. Restoring data from backup.")
            os.rename(BACKUP_FILE, DATA_FILE)
        else:
            print("✅ No existing contacts file found. Starting fresh.")
            return {}
            
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        print("❌ Error reading data file. Data might be corrupted.")
        return {}


def add_contact(contacts: dict) -> dict:
    """Collects inputs, validates parameters, and appends a contact to the memory."""
    print("\n--- ADD NEW CONTACT ---")
    
    while True:
        name = input("Enter contact name: ").strip()
        if name:
            if name in contacts:
                print(f"Contact '{name}' already exists!")
                choice = input("Do you want to update it instead? (y/n): ").lower()
                if choice == 'y':
                    return update_contact(contacts, name)
                return contacts
            break
        print("Name cannot be empty!")
    
    while True:
        phone = input("Enter phone number: ").strip()
        is_valid, cleaned_phone = validate_phone(phone)
        if is_valid:
            break
        print("Invalid phone number! Please enter 10-15 digits.")
        
    while True:
        email = input("Enter email (optional, press Enter to skip): ").strip()
        if not email or validate_email(email):
            break
        print("Invalid email format!")

    address = input("Enter address (optional): ").strip()
    
    print("Select Group (1: Friends, 2: Work, 3: Family, 4: Other)")
    group_choice = input("Enter choice (default 'Other'): ").strip()
    group_map = {"1": "Friends", "2": "Work", "3": "Family", "4": "Other"}
    group = group_map.get(group_choice, "Other")

    contacts[name] = {
        'phone': cleaned_phone,
        'email': email if email else None,
        'address': address if address else None,
        'group': group,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    print(f"✅ Contact '{name}' added successfully!")
    save_to_file(contacts)
    return contacts


def search_contacts(contacts: dict):
    """Executes partial query matching against either names or unique phone strings."""
    print("\n--- SEARCH CONTACTS ---")
    term = input("Enter name or phone number to search: ").strip().lower()
    
    if not term:
        print("Search term cannot be empty!")
        return

    results = {}
    for name, info in contacts.items():
        if term in name.lower() or term in info['phone']:
            results[name] = info

    if not results:
        print("🔍 No matching contacts found.")
        return

    print(f"\nFound {len(results)} contact(s):")
    print("-" * 50)
    for i, (name, info) in enumerate(results.items(), 1):
        print(f"{i}. 👤 {name}")
        print(f"   📞 Phone: {info['phone']}")
        if info['email']: print(f"   📧 Email: {info['email']}")
        if info['address']: print(f"   📍 Address: {info['address']}")
        print(f"   👥 Group: {info['group']}")
        print()


def update_contact(contacts: dict, target_name: str = None) -> dict:
    """Updates fields on an existing designated contact identifier key."""
    print("\n--- UPDATE CONTACT ---")
    if not target_name:
        target_name = input("Enter the full name of the contact to update: ").strip()
        
    if target_name not in contacts:
        print(f"❌ Contact '{target_name}' not found.")
        return contacts

    info = contacts[target_name]
    print(f"Updating details for '{target_name}'. Press Enter to retain existing values.")

    # Phone update
    new_phone = input(f"Phone [{info['phone']}]: ").strip()
    if new_phone:
        while True:
            is_valid, cleaned_phone = validate_phone(new_phone)
            if is_valid:
                info['phone'] = cleaned_phone
                break
            print("Invalid format. Update skipped or enter valid 10-15 digits.")
            new_phone = input(f"Phone [{info['phone']}]: ").strip()
            if not new_phone: break

    # Email update
    new_email = input(f"Email [{info['email'] or 'None'}]: ").strip()
    if new_email:
        while True:
            if validate_email(new_email):
                info['email'] = new_email
                break
            print("Invalid email format.")
            new_email = input(f"Email [{info['email'] or 'None'}]: ").strip()
            if not new_email: break

    # Address update
    new_address = input(f"Address [{info['address'] or 'None'}]: ").strip()
    if new_address:
        info['address'] = new_address

    # Group update
    print(f"Current Group: {info['group']}")
    print("Select New Group (1: Friends, 2: Work, 3: Family, 4: Other, Enter to skip)")
    group_choice = input("Choice: ").strip()
    group_map = {"1": "Friends", "2": "Work", "3": "Family", "4": "Other"}
    if group_choice in group_map:
        info['group'] = group_map[group_choice]

    info['updated_at'] = datetime.now().isoformat()
    contacts[target_name] = info
    
    print(f"✅ Contact '{target_name}' updated successfully!")
    save_to_file(contacts)
    return contacts


def delete_contact(contacts: dict) -> dict:
    """Removes a key entry element safely following verification."""
    print("\n--- DELETE CONTACT ---")
    name = input("Enter the full name of the contact to delete: ").strip()
    
    if name not in contacts:
        print(f"❌ Contact '{name}' not found.")
        return contacts

    confirm = input(f"⚠️ Are you sure you want to delete '{name}'? (y/n): ").lower()
    if confirm == 'y':
        del contacts[name]
        print(f"✅ Contact '{name}' deleted successfully!")
        save_to_file(contacts)
    else:
        print("Deletion canceled.")
    return contacts


def display_all(contacts: dict):
    """Iterates clean layouts across the collection structure layout fields."""
    print(f"\n--- ALL CONTACTS ({len(contacts)} total) ---")
    if not contacts:
        print("No contacts to display.")
        return

    print("=" * 60)
    for name, info in sorted(contacts.items()):
        print(f"👤 {name}")
        print(f"   📞 {info['phone']}")
        if info['email']: print(f"   📧 {info['email']}")
        if info['address']: print(f"   📍 {info['address']}")
        print(f"   👥 Group: {info['group']}")
        print("-" * 40)
    print("=" * 60)


def export_to_csv(contacts: dict):
    """Converts internal schema layout objects directly out into runtime flat CSV targets."""
    print("\n--- EXPORT TO CSV ---")
    if not contacts:
        print("❌ No contacts data available to export.")
        return

    try:
        with open(EXPORT_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Phone', 'Email', 'Address', 'Group', 'Created At', 'Updated At'])
            for name, info in contacts.items():
                writer.writerow([
                    name, 
                    info['phone'], 
                    info.get('email', ''), 
                    info.get('address', ''), 
                    info['group'], 
                    info['created_at'], 
                    info['updated_at']
                ])
        print(f"✅ Contacts successfully exported to {EXPORT_FILE}")
    except IOError as e:
        print(f"❌ Failed to export CSV file: {e}")


def view_statistics(contacts: dict):
    """Aggregates metrics and grouping splits dynamically."""
    print("\n--- CONTACT STATISTICS ---")
    total = len(contacts)
    print(f"Total Contacts: {total}")
    
    if total == 0:
        return

    groups = {}
    for info in contacts.values():
        g = info.get('group', 'Other')
        groups[g] = groups.get(g, 0) + 1

    print("\nContacts by Group:")
    for group, count in groups.items():
        print(f"  {group}: {count} contact(s)")


def main():
    """Application main runtime loop configuration menu."""
    contacts = load_from_file()
    
    while True:
        print("\n" + "=" * 50)
        print("      CONTACT MANAGEMENT SYSTEM")
        print("=" * 50)
        print("1. Add New Contact")
        print("2. Search Contact")
        print("3. Update Contact")
        print("4. Delete Contact")
        print("5. View All Contacts")
        print("6. Export to CSV")
        print("7. View Statistics")
        print("8. Exit")
        print("=" * 30)
        
        choice = input("Enter your choice (1-8): ").strip()
        
        if choice == '1':
            contacts = add_contact(contacts)
        elif choice == '2':
            search_contacts(contacts)
        elif choice == '3':
            contacts = update_contact(contacts)
        elif choice == '4':
            contacts = delete_contact(contacts)
        elif choice == '5':
            display_all(contacts)
        elif choice == '6':
            export_to_csv(contacts)
        elif choice == '7':
            view_statistics(contacts)
        elif choice == '8':
            save_to_file(contacts)
            print("\n==================================================")
            print("Thank you for using Contact Management System!")
            print("==================================================")
            break
        else:
            print("❌ Invalid entry! Please type a numeric value between 1 and 8.")


if __name__ == "__main__":
    main()
