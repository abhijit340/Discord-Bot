import pytz
from datetime import datetime

local_timezone = datetime.now(pytz.timezone('UTC')).astimezone().tzinfo
print(local_timezone)
