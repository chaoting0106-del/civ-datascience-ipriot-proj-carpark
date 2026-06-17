import time
import threading
import tkinter as tk
from typing import Iterable
from interfaces import CarparkSensorListener
from interfaces import CarparkDataProvider
from carpark import CarparkManager


# ------------------------------------------------------------------------------------#
# You don't need to understand how to implement this class.                           #
# ------------------------------------------------------------------------------------#


class WindowedDisplay:
    """Displays values for a given set of fields as a simple GUI window. Use .show() to display the window; use .update() to update the values displayed.
    """

    DISPLAY_INIT = '– – –'
    SEP = ':'  # field name separator

    def __init__(self, root, title: str, display_fields: Iterable[str]):
        """Creates a Windowed (tkinter) display to replace sense_hat display. To show the display (blocking) call .show() on the returned object.

        Parameters
        ----------
        title : str
            The title of the window (usually the name of your carpark from the config)
        display_fields : Iterable
            An iterable (usually a list) of field names for the UI. Updates to values must be presented in a dictionary with these values as keys.
        """
        self.window = tk.Toplevel(root)
        self.window.title(f'{title} Car Parking System')
        self.window.geometry('800x400')
        self.window.resizable(False, False)
        self.window.configure(bg="#000000")
        self.window.master.configure(bg="#000000")
        self.display_fields = display_fields


        self.gui_elements = {}
        for i, field in enumerate(self.display_fields):

            # create the elements
            self.gui_elements[f'lbl_field_{i}'] = tk.Label(
                self.window, text=field+self.SEP, font=('Arial', 50), fg="#FFFFFF" ,bg="#000000")
            self.gui_elements[f'lbl_value_{i}'] = tk.Label(
                self.window, text=self.DISPLAY_INIT, font=('Arial', 50), fg="#FFFFFF" ,bg="#000000")

            # position the elements
            self.gui_elements[f'lbl_field_{i}'].grid(
                row=i, column=0, sticky=tk.E, padx=5, pady=5)
            self.gui_elements[f'lbl_value_{i}'].grid(
                row=i, column=2, sticky=tk.W, padx=10)

    def show(self):
        """Display the GUI. Blocking call."""
#        self.window.mainloop()

    def update(self, updated_values: dict):
        """Update the values displayed in the GUI. Expects a dictionary with keys matching the field names passed to the constructor."""
        for field in self.gui_elements:
            if field.startswith('lbl_field'):
                field_value = field.replace('field', 'value')
                self.gui_elements[field_value].configure(
                    text=updated_values[self.gui_elements[field].cget('text').rstrip(self.SEP)])
        self.window.update()


# STUDENT IMPLEMENTATION STARTS HERE #

class CarParkDisplay:
    """Provides an instant, event-driven display of the car park status."""
    fields = ['Available bays', 'Temperature', 'At']

    def __init__(self,root):
        self.window = WindowedDisplay(root,
            'Moondalup City', CarParkDisplay.fields)
        updater = threading.Thread(target=self.check_updates)
        updater.daemon = True
        updater.start()
        self.window.show()
        self._provider=None
    
    @property
    def data_provider(self):
        return self._provider
    
    @data_provider.setter
    def data_provider(self, provider):
        if isinstance(provider, CarparkDataProvider):
            self._provider = provider
            # Register this display with your manager for instant push notifications
            if hasattr(provider, 'register_observer'):
                provider.register_observer(self)
            self.update_display()

    def update_display(self):
        if not hasattr(self, '_provider') or self._provider is None:
            return

        field_values = dict(zip(CarParkDisplay.fields, [
            f'{self._provider.available_spaces:03d}',
            f'{float(self._provider.temperature):04.1f}℃',
            time.strftime("%H:%M:%S", self._provider.current_time)
        ]))
        self.window.update(field_values)

    def check_updates(self):
        while True:
            if hasattr(self, 'update_event'):
                self.update_event.wait()
                self.update_event.clear()
                self.update_display()
            else:
                time.sleep(1)


class CarDetectorWindow:
    """Provides interactive control panel options representing entry/exit hardware simulation."""
    def __init__(self, root):
        self.root = root
        self.root.title("Car Detector Control Panel")
        self.root.configure(bg="#000000")

        self.btn_incoming_car = tk.Button(
            self.root, text='🚘 Incoming Car', font=('Arial', 50), cursor='right_side',
            fg="#FFFFFF", bg="#000000", command=self.incoming_car)
        self.btn_incoming_car.grid(padx=10, pady=5, row=0, columnspan=2)
        
        self.btn_outgoing_car = tk.Button(
            self.root, text='Outgoing Car 🚗', font=('Arial', 50), cursor='bottom_left_corner',
            fg="#FFFFFF", bg="#000000", command=self.outgoing_car)
        self.btn_outgoing_car.grid(padx=10, pady=5, row=1, columnspan=2)
        
        self.listeners = list()
        
        self.temp_label = tk.Label(
            self.root, text="Temperature", font=('Arial', 20), fg="#FFFFFF", bg="#000000"
        )
        self.temp_label.grid(padx=10, pady=5, column=0, row=2)
        
        self.temp_var = tk.StringVar()
        self.temp_var.trace_add("write", self._on_temperature_typing)
        
        self.temp_box = tk.Entry(
            self.root, font=('Arial', 20), textvariable=self.temp_var
        )
        self.temp_box.grid(padx=10, pady=5, column=1, row=2)

        self.plate_label = tk.Label(
            self.root, text="License Plate", font=('Arial', 20), fg="#FFFFFF", bg="#000000"
        )
        self.plate_label.grid(padx=10, pady=5, column=0, row=3)
        
        self.plate_var = tk.StringVar()
        self.plate_box = tk.Entry(
            self.root, font=('Arial', 20), textvariable=self.plate_var
        )
        self.plate_box.grid(padx=10, pady=5, column=1, row=3)
    
    @property
    def current_license(self):
        return self.plate_var.get()

    def add_listener(self, listener):
        if isinstance(listener, CarparkSensorListener):
            self.listeners.append(listener)

    def incoming_car(self):
#        print("Car goes in")
        for listener in self.listeners:
            listener.incoming_car(self.current_license)

    def outgoing_car(self):
#        print("Car goes out")
        for listener in self.listeners:
            listener.outgoing_car(self.current_license)

    def _on_temperature_typing(self, *args):
        """Catches and handles incomplete typing or empty input states cleanly."""
        try:
            val = self.temp_var.get()
            if val:
                self.temperature_changed(float(val))
        except ValueError:
            pass

    def temperature_changed(self, temp):
        for listener in self.listeners:
            listener.temperature_reading(temp)


if __name__ == '__main__':
    root = tk.Tk()

    m = CarparkManager()

    display=CarParkDisplay(root)
    display.data_provider= m

    detector=CarDetectorWindow(root)
    detector.add_listener(m)

    root.mainloop()
