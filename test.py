import json
from datetime import datetime

with open("version.json", "w") as f:
    data = {
        "last_updated": str(datetime.now()),
    }
    json.dump(data, f)
