import os

pit_username = os.getenv("REG_USERNAME")
pit_password = os.getenv("REG_PASSWORD")
pcr_token = os.getenv("PCR_AUTH_TOKEN", "public")
