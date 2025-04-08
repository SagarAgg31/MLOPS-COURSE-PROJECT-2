import os
from dotenv import load_dotenv

load_dotenv()  # this loads from your .env

# optional, but safe: sets the env var explicitly
credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if credentials is not None:
	os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials
else:
	raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")
