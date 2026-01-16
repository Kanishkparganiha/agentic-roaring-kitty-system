import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Base, Stock, Price, Fundamental, Score, Alert
from config import Settings
from sqlalchemy import create_engine, inspect

settings = Settings()
engine = create_engine(settings.database_url)
Base.metadata.create_all(engine)

print('Tables created successfully!')
tables = inspect(engine).get_table_names()
print(f'Tables: {tables}')
