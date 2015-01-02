from datetime import datetime
from pony.orm import *

db = Database("sqlite", "database.sqlite", create_db=True)

class Receiver(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    mac_addr = Required(str)
    recordings = Set("Recording")
    x = Required(float)
    y = Required(float)
    z = Required(float)

class Recording(db.Entity):
    id = PrimaryKey(int, auto=True)
    receiver = Required(Receiver)
    rssi = Required(int)
    data = Optional(str, nullable=True)
    transmitter = Required("Transmitter")
    time = Required(datetime)

class Transmitter(db.Entity):
    id = PrimaryKey(int, auto=True)
    mac_addr = Required(str)
    name = Optional(str)
    positions = Set("CalculatedPosition")
    recordings = Set(Recording)

class CalculatedPosition(db.Entity):
    _table_ = "Position"
    id = PrimaryKey(int, auto=True)
    time = Required(datetime)
    transmitter = Required(Transmitter)
    uncertainty = Required(float)
    x = Required(float)
    y = Required(float)
    z = Required(float)

sql_debug(False)
db.generate_mapping(create_tables=True)