from decouple import config
from dotenv import load_dotenv

load_dotenv(override=True)

### Develop Settings
DEBUG = config("DEBUG", default=False, cast=bool)

### Database Settings
DATABASE_USERNAME = config("DATABASE_USERNAME", default="", cast=str)
DATABASE_PASSWORD = config("DATABASE_PASSWORD", default="", cast=str)
DATABASE_PORT = config("DATABASE_PORT", default=5432, cast=int)
DATABASE_NAME = config("DATABASE_NAME", default="", cast=str)
SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@localhost:{DATABASE_PORT}/{DATABASE_NAME}"
