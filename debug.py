import sys
import traceback
sys.path.append('.')
from backend.main import get_latest_result
from backend.database import SessionLocal
db = SessionLocal()
try:
    print(get_latest_result(db))
except Exception as e:
    traceback.print_exc()
