import abc

class CarparkSensorListener(abc.ABC):

    @abc.abstractmethod
    def incoming_car(self, license_plate):
        pass

    @abc.abstractmethod
    def outgoing_car(self, license_plate):
        pass

    @abc.abstractmethod
    def temperature_reading(self, reading):
        pass


class CarparkDataProvider(abc.ABC):
    
    @property
    @abc.abstractmethod
    def available_spaces(self):
        pass

    @property
    @abc.abstractmethod
    def temperature(self):
        pass 

    @property
    @abc.abstractmethod
    def current_time(self):
        pass
