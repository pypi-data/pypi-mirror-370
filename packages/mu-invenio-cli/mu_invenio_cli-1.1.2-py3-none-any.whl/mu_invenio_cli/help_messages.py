#
# Copyright (C) 2025 Masaryk University
#
# MU-INVENIO-CLI is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
"""Help messages for the MU Invenio CLI application."""

def help_config_state():
    print("\nConfiguration Help:")
    print(f"BASE_API_URL - The base URL for the API. Example: https://dar.elter-ri.eu/api")
    print(f"API_TOKEN - The API token for the API. This token can be generated in the Profile Application sections in the DAR")
    print(f"MODEL - The model to use for the API. Example: datasets/external-datasets")