#
# Copyright (C) 2025 Masaryk University
#
# MU-INVENIO-CLI is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Configuration state for the MU Invenio CLI application.
This state handles the required configuration of the CLI application.
"""

import configparser
import os

from .base_state import BaseState
from .state import State

CONFIG_FILE = 'config.cfg'
REQUIRED_KEYS = ['BASE_API_URL', 'API_TOKEN', 'MODEL']


class ConfigurationState(BaseState):
    def __init__(self, context):
        super().__init__(context)
        self.config_parser = configparser.ConfigParser()
        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            self.config_parser.read(CONFIG_FILE)
            if 'DEFAULT' in self.config_parser:
                for key in REQUIRED_KEYS:
                    self.context.config[key] = self.config_parser['DEFAULT'].get(key)
        else:
            for key in REQUIRED_KEYS:
                self.context.config[key] = None

    def save_config(self):
        self.config_parser['DEFAULT'] = {k: v or '' for k, v in self.context.config.items()}
        with open(CONFIG_FILE, 'w') as configfile:
            self.config_parser.write(configfile)

    def is_config_complete(self):
        return all(self.context.config.get(k) for k in REQUIRED_KEYS)

    def show_config(self):
        print("\nCurrent configuration:")
        for key in REQUIRED_KEYS:
            value = self.context.config.get(key)
            print(f"  {key}: {value if value else '[NOT SET]'}")
        if self.is_config_complete():
            print("\n✅ Configuration is complete.")
        else:
            print("\n❌ Configuration is incomplete. Please set all values.")

    def handle(self):
        self.context.last_state = State.CONFIGURATION

        while True:
            self.show_config()
            print("\nOptions:")
            for idx, key in enumerate(REQUIRED_KEYS, 1):
                print(f"  {idx}. Set {key}")
            if self.is_config_complete():
                print(f"  {len(REQUIRED_KEYS) + 1}. Continue")
            print("  9. Help")
            print("  0. Exit")

            choice = input("Select option: ").strip()
            if choice == '0':
                exit(0)
            elif choice in map(str, range(1, len(REQUIRED_KEYS) + 1)):
                key = REQUIRED_KEYS[int(choice) - 1]
                value = input(f"Enter value for {key}: ").strip()
                self.context.config[key] = value
                self.save_config()
            elif self.is_config_complete() and choice == str(len(REQUIRED_KEYS) + 1):
                self.save_config()
                self.context.state = State.NOT_SELECTED
                print("Configuration complete.")
                break
            elif choice == '9':
                self.context.state = State.HELP
                break
            else:
                print("Invalid option.")
