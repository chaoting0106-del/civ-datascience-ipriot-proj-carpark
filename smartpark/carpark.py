import time
import json
import datetime
from interfaces import CarparkSensorListener, CarparkDataProvider
from config_parser import parse_config

class CarparkManager(CarparkSensorListener, CarparkDataProvider):
    """Manages carpark status updates, reads configurations, logs events, 
     and instantly notifies displays of state changes.
    """
    CONFIG_FILE = "samples_and_snippets/config.json"
    LOG_FILE = "carpark_log.txt"

    def __init__(self):
        # Read file and setup layout from your configurations
        self.config = parse_config("samples_and_snippets/config.json")
        self.total_bays = int(self.config.get("total-spaces", 192))
        self.name = self.config.get("name", "raf-park-international")
        self._temperature = 10.0
        self.current_cars = {}  # {license_plate: Car}
        self.historical_log = []
        self.observers = []

    def register_observer(self, observer):
        """Allows display instances to register themselves for status updates."""
        if observer not in self.observers:
            self.observers.append(observer)

    def _notify_observers(self):
        for observer in self.observers:
            if hasattr(observer, 'update_display'):
                observer.update_display()

    def _write_log(self, message: str):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", datetime.datetime.now().timetuple())
        log_entry = f"[{timestamp}] {message}\n"
    
        print(log_entry.strip())  # Prints to your terminal window
    
        # Write to the file:
        with open(CarparkManager.LOG_FILE, "a") as file:
            file.write(log_entry)

    @property
    def available_spaces(self) -> int:
     return self.total_bays - len(self.current_cars)

    @property
    def temperature(self) -> float:
        return float(self._temperature)
    
    @temperature.setter
    def temperature(self, value):
        if -10 <= value <= 50:
            self._temperature = value


    @property
    def current_time(self):
        return datetime.datetime.now().timetuple()

    def incoming_car(self, license_plate: str):
        """Processes vehicle arrivals, builds sessions, and updates."""

        if not license_plate:
            self._write_log("WARNING: Unknown plate for incoming car.")
            return
        
        if license_plate in self.current_cars:
            self._write_log(f"Attention : [{license_plate}] is already inside carpark.")
            return  
        
        if any(past_car.license_plate == license_plate for past_car in self.historical_log):
            self._write_log(f"Attention : [{license_plate}] has already used this car park today.")
            return 

        new_car = Car(license_plate)
        self.current_cars[license_plate] = new_car
        
        self._write_log(f"Car Entered: Car [{license_plate}] | Spaces: {self.available_spaces}")
        self._notify_observers()

    def outgoing_car(self, license_plate: str):
        """Processes departures, logs durations, and frees up parking allocations."""

        if not license_plate:
            self._write_log("WARNING: Unknown plate for outgoing car")
            return

        if license_plate not in self.current_cars:
            self._write_log(f"WARNING: the vehicle [{license_plate}] tried exiting without entry log.")
            return

        exiting_car = self.current_cars.pop(license_plate)
        exiting_car.record_exit()
        self.historical_log.append(exiting_car)

        self._write_log(f"Car Departed: License [{license_plate}]  | Spaces Remaining: {self.available_spaces}")
        self._notify_observers()

    def temperature_reading(self, reading: float):
        """Processes temperature sensor inputs instantly using your setter."""
        self.temperature = reading
        self._write_log(f"Temperature : The system changed to {reading:.1f}°C")
        self._notify_observers()


class Car:
    def __init__(self, plate: str):
        self.license_plate = plate
        self.raw_entry_time = datetime.datetime.now()
        self.entry_time = self.raw_entry_time.timetuple()
        self.exit_time = None

    def record_exit(self):
        raw_exit = datetime.datetime.now()
        self.exit_time = raw_exit.timetuple()

    def __str__(self):
        entry_str = time.strftime("%H:%M:%S", self.entry_time)
        exit_str = time.strftime("%H:%M:%S", self.exit_time) if self.exit_time else "Still Parked"
        return f"Car[{self.license_plate}] Entered: {entry_str} | Exited: {exit_str}"
