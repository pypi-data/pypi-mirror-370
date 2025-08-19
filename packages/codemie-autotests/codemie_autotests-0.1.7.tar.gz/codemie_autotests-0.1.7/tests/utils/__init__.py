import os

from dotenv import load_dotenv

load_dotenv()

api_domain = os.getenv("CODEMIE_API_DOMAIN")
verify_ssl = os.getenv("VERIFY_SSL", "").lower() == "true"
