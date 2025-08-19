import os
import json

from mu_invenio_cli.states.state import State


class NotSelectedState:
    def __init__(self, context):
        self.context = context

    def has_access_to_draft(self, record_id):
        return True

    def handle(self):
        self.clear_state()

        print("\nPlease create a draft or select an existing one.")
        while True:
            print("\nOptions:")
            print("  1. Create a new draft from JSON file")
            print("  2. Set draft by id")
            print("  3. Back to configuration")
            print("  9. Help")
            print("  0. Exit")

            choice = input("Select option: ").strip()
            if choice == '1':
                file_path = input("Enter path to JSON file: ").strip()
                if not os.path.isfile(file_path):
                    print("File does not exist.")
                    continue
                try:
                    with open(file_path, 'r') as f:
                        body = json.load(f)
                    print("File loaded successfully.")
                except Exception as e:
                    print(f"Failed to load JSON: \n     {e}")
            elif choice == '2':
                record_id = input("Enter record id: ").strip()
                if self.has_access_to_draft(record_id):
                    self.context.selected_id = record_id
                    print(f"Selected id set to: {record_id}")
                    self.context.last_state = State.NOT_SELECTED
                    self.context.state = State.SELECTED
                    break
                else:
                    print("Access denied or invalid id.")
            elif choice == '3':
                self.context.last_state = State.NOT_SELECTED
                self.context.state = State.CONFIGURATION
                print("Returning to configuration state.")
                break
            elif choice == '9':
                self.context.last_state = State.NOT_SELECTED
                self.context.state = State.HELP
                break
            elif choice == '0':
                exit(0)
            else:
                print("Invalid option. Please try again.")

    def clear_state(self):
        self.context.selected_id = None
        self.context.json_body = None
        self.context.selected_data = None
