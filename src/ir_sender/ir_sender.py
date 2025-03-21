import ctypes
import time

class LogLevel:
    ErrorsOnly = 0
    Minimal = 2
    Normal = 5
    Verbose = 10

# This is the struct required by pigpio library.
# We store the individual pulses and their duration here. (In an array of these structs.)
class Pulses_struct(ctypes.Structure):
    _fields_ = [("gpioOn", ctypes.c_uint32),
                ("gpioOff", ctypes.c_uint32),
                ("usDelay", ctypes.c_uint32)]

# Since both NEC and RC-5 protocols use the same method for generating waveform,
# it can be put in a separate class and called from both protocol's classes.
class Wave_generator():
    def __init__(self, protocol, log_level = LogLevel.Minimal):
        self.protocol = protocol
        self.log_level = log_level
        MAX_PULSES = 12000 # from pigpio.h
        Pulses_array = Pulses_struct * MAX_PULSES
        self.pulses = Pulses_array()
        self.pulse_count = 0

    def __log(self, min_log_level, message):
        if min_log_level <= self.log_level:
            print(message)

    def add_pulse(self, gpioOn, gpioOff, usDelay):
        self.pulses[self.pulse_count].gpioOn = gpioOn
        self.pulses[self.pulse_count].gpioOff = gpioOff
        self.pulses[self.pulse_count].usDelay = usDelay
        self.pulse_count += 1

    # Pull the specified output pin low
    def zero(self, duration):
        self.__log(LogLevel.Verbose, "SPACE\t%s" % duration)
        self.add_pulse(0, 1 << self.protocol.master.gpio_pin, duration)

    # Protocol-agnostic square wave generator
    def one(self, duration):
        self.__log(LogLevel.Verbose, " MARK\t%s" % duration)
        period_time = 1000000.0 / self.protocol.frequency
        on_duration = int(round(period_time * self.protocol.duty_cycle))
        off_duration = int(round(period_time * (1.0 - self.protocol.duty_cycle)))
        total_periods = int(round(duration/period_time))
        total_pulses = total_periods * 2

        # Generate square wave on the specified output pin
        for i in range(total_pulses):
            if i % 2 == 0:
                self.add_pulse(1 << self.protocol.master.gpio_pin, 0, on_duration)
            else:
                self.add_pulse(0, 1 << self.protocol.master.gpio_pin, off_duration)

# NEC protocol class
class NEC():
    def __init__(self,
                master,
                log_level = LogLevel.Minimal,
                frequency=38000,
                duty_cycle=0.33,
                leading_pulse_duration=9000,
                leading_gap_duration=4500,
                one_pulse_duration = 562,
                one_gap_duration = 1686,
                zero_pulse_duration = 562,
                zero_gap_duration = 562,
                trailing_pulse_duration = 562,
                trailing_gap_duration = 0):
        self.master = master
        self.log_level = log_level
        self.wave_generator = Wave_generator(self, log_level)
        self.frequency = frequency # in Hz, 38000 per specification
        self.duty_cycle = duty_cycle # duty cycle of high state pulse
        # Durations of high pulse and low "gap".
        # The NEC protocol defines pulse and gap lengths, but we can never expect
        # that any given TV will follow the protocol specification.
        self.leading_pulse_duration = leading_pulse_duration # in microseconds, 9000 per specification
        self.leading_gap_duration = leading_gap_duration # in microseconds, 4500 per specification
        self.one_pulse_duration = one_pulse_duration # in microseconds, 562 per specification
        self.one_gap_duration = one_gap_duration # in microseconds, 1686 per specification
        self.zero_pulse_duration = zero_pulse_duration # in microseconds, 562 per specification
        self.zero_gap_duration = zero_gap_duration # in microseconds, 562 per specification
        self.trailing_pulse_duration = trailing_pulse_duration # trailing 562 microseconds pulse, some remotes send it, some don't
        self.trailing_gap_duration = trailing_gap_duration # trailing space
        self.__log(LogLevel.Minimal, "NEC protocol initialized")

    def __log(self, min_log_level, message):
        if min_log_level <= self.log_level:
            print(message)

    # Send AGC burst before transmission
    def send_agc(self):
        self.__log(LogLevel.Normal, "Sending AGC burst")
        self.wave_generator.one(self.leading_pulse_duration)
        self.wave_generator.zero(self.leading_gap_duration)

    # Trailing pulse is just a burst with the duration of standard pulse.
    def send_trailing_pulse(self):
        self.__log(LogLevel.Normal, "Sending trailing pulse")
        self.wave_generator.one(self.trailing_pulse_duration)
        if self.trailing_gap_duration > 0:
            self.wave_generator.zero(self.trailing_gap_duration)

    # This function is processing IR code. Leaves room for possible manipulation
    # of the code before processing it.
    def process_code(self, ircode):
        if (self.leading_pulse_duration > 0) or (self.leading_gap_duration > 0):
            self.send_agc()
        self.__log(LogLevel.Normal, "Sending data")
        for i in ircode:
            if i == "0":
                self.zero()
            elif i == "1":
                self.one()
            else:
                self.__log(LogLevel.ErrorsOnly, "ERROR! Non-binary digit!")
                return 1
        if self.trailing_pulse_duration > 0:
            self.send_trailing_pulse()
        return 0

    # Generate zero or one in NEC protocol
    # Zero is represented by a pulse and a gap of the same length
    def zero(self):
        self.__log(LogLevel.Verbose, "ZERO")
        self.wave_generator.one(self.zero_pulse_duration)
        self.wave_generator.zero(self.zero_gap_duration)

    # One is represented by a pulse and a gap three times longer than the pulse
    def one(self):
        self.__log(LogLevel.Verbose, "ONE")
        self.wave_generator.one(self.one_pulse_duration)
        self.wave_generator.zero(self.one_gap_duration)

# RC-5 protocol class
# Note: start bits are not implemented here due to inconsistency between manufacturers.
# Simply provide them with the rest of the IR code.
class RC5():
    def __init__(self,
                master,
                log_level = LogLevel.Minimal,
                frequency=36000,
                duty_cycle=0.33,
                one_duration=889,
                zero_duration=889):
        self.master = master
        self.log_level = log_level
        self.wave_generator = Wave_generator(self)
        self.frequency = frequency # in Hz, 36000 per specification
        self.duty_cycle = duty_cycle # duty cycle of high state pulse
        # Durations of high pulse and low "gap".
        # Technically, they both should be the same in the RC-5 protocol, but we can never expect
        # that any given TV will follow the protocol specification.
        self.one_duration = one_duration # in microseconds, 889 per specification
        self.zero_duration = zero_duration # in microseconds, 889 per specification
        self.__log(LogLevel.Minimal, "RC-5 protocol initialized")

    def __log(self, min_log_level, message):
        if min_log_level <= self.log_level:
            print(message)

    # This function is processing IR code. Leaves room for possible manipulation
    # of the code before processing it.
    def process_code(self, ircode):
        for i in ircode:
            if i == "0":
                self.zero()
            elif i == "1":
                self.one()
            else:
                self.__log(LogLevel.ErrorsOnly, "ERROR! Non-binary digit!")
                return 1
        return 0

    # Generate zero or one in RC-5 protocol
    # Zero is represented by pulse-then-low signal
    def zero(self):
        self.wave_generator.one(self.zero_duration)
        self.wave_generator.zero(self.zero_duration)

    # One is represented by low-then-pulse signal
    def one(self):
        self.wave_generator.zero(self.one_duration)
        self.wave_generator.one(self.one_duration)

# RAW IR ones and zeroes. Specify length for one and zero and simply bitbang the GPIO.
# The default values are valid for one tested remote which didn't fit in NEC or RC-5 specifications.
# It can also be used in case you don't want to bother with deciphering raw bytes from IR receiver:
# i.e. instead of trying to figure out the protocol, simply define bit lengths and send them all here.
class RAW():
    def __init__(self,
                master, 
                log_level = LogLevel.Minimal,
                frequency=36000,
                duty_cycle=0.33,
                one_duration=520,
                zero_duration=520):
        self.master = master
        self.log_level = log_level
        self.wave_generator = Wave_generator(self)
        self.frequency = frequency # in Hz
        self.duty_cycle = duty_cycle # duty cycle of high state pulse
        self.one_duration = one_duration # in microseconds
        self.zero_duration = zero_duration # in microseconds

    def __log(self, min_log_level, message):
        if min_log_level <= self.log_level:
            print(message)

    def process_code(self, ircode):
        for i in ircode:
            if i == "0":
                self.zero()
            elif i == "1":
                self.one()
            else:
                self.__log(LogLevel.ErrorsOnly, "ERROR! Non-binary digit!")
                return 1
        return 0

    # Generate raw zero or one.
    # Zero is represented by low (no signal) for a specified duration.
    def zero(self):
        self.wave_generator.zero(self.zero_duration)

    # One is represented by pulse for a specified duration.
    def one(self):
        self.wave_generator.one(self.one_duration)

class IrSender:
    def __init__(self, gpio_pin, protocol, protocol_config, log_level=LogLevel.Minimal):
        """
        Initializes the IR sender.
        
        Parameters:
            gpio_pin (int): The GPIO pin used for IR transmission.
            protocol (str): The IR protocol (e.g., "NEC", "RC-5", "RAW").
            protocol_config (dict): Configuration parameters for the chosen protocol.
            log_level (LogLevel): The verbosity level for logging.
        """
        self.log_level = log_level
        self.__log(LogLevel.Minimal, "Starting IR")
        self.__log(LogLevel.Normal, "Loading libpigpio.so")

        # Load the pigpio library
        try:
            self.pigpio = ctypes.CDLL('/usr/lib/libpigpio.so')
        except OSError as e:
            self.__log(LogLevel.ErrorsOnly, f"Failed to load libpigpio.so: {e}")
            raise RuntimeError("Failed to load libpigpio.so")
        
        self.__log(LogLevel.Normal, "Initializing pigpio")
        self.pigpio.gpioInitialise()

        # Set up the GPIO pin for output
        self.gpio_pin = gpio_pin
        self.__log(LogLevel.Normal, f"Configuring pin {self.gpio_pin} as output")
        PI_OUTPUT = 1  # Defined in pigpio.h
        self.pigpio.gpioSetMode(self.gpio_pin, PI_OUTPUT)

        # Initialize the IR protocol
        self.__log(LogLevel.Normal, "Initializing protocol")
        if protocol == "NEC":
            self.protocol = NEC(self, log_level, **protocol_config)
        elif protocol == "RC-5":
            self.protocol = RC5(self, log_level, **protocol_config)
        elif protocol == "RAW":
            self.protocol = RAW(self, log_level, **protocol_config)
        else:
            self.__log(LogLevel.ErrorsOnly, "Protocol not specified! Exiting...")
            raise ValueError("Protocol not specified!")
        
        self.__log(LogLevel.Minimal, "IR ready")

    def __log(self, min_log_level, message):
        """Logs messages based on the set log level."""
        if min_log_level <= self.log_level:
            print(message)

    def send_code(self, ircode, nb=1):
        """
        Sends the processed IR code to pigpio.
        
        Parameters:
            ircode (str): The binary IR code to send.
            nb (int): Number of times to send the code.
        """
        self.__log(LogLevel.Normal, f"Processing IR code: {' '.join([ircode[i:i+8] for i in range(0, len(ircode), 8)])}")
        
        for _ in range(nb):
            code = self.protocol.process_code(ircode)
            if code != 0:
                self.__log(LogLevel.ErrorsOnly, "Error in processing IR code!")
                return 1

        # Clear existing waveform
        if self.pigpio.gpioWaveClear() != 0:
            self.__log(LogLevel.ErrorsOnly, "Error in clearing wave!")
            return 1

        # Add wave to pigpio
        pulses = self.pigpio.gpioWaveAddGeneric(self.protocol.wave_generator.pulse_count, self.protocol.wave_generator.pulses)
        if pulses < 0:
            self.__log(LogLevel.ErrorsOnly, "Error in adding wave!")
            return 1

        # Create and send the wave
        wave_id = self.pigpio.gpioWaveCreate()
        if wave_id >= 0:
            self.__log(LogLevel.Normal, "Sending wave...")
            result = self.pigpio.gpioWaveTxSend(wave_id, 0)
            if result >= 0:
                self.__log(LogLevel.Normal, f"Success! (result: {result})")
            else:
                self.__log(LogLevel.ErrorsOnly, f"Error sending wave! (result: {result})")
                return 1
        else:
            self.__log(LogLevel.ErrorsOnly, f"Error creating wave: {wave_id}")
            return 1

        # Wait for transmission to complete
        while self.pigpio.gpioWaveTxBusy():
            time.sleep(0.1)

        self.__log(LogLevel.Normal, "Deleting wave")
        self.pigpio.gpioWaveDelete(wave_id)

        self.__log(LogLevel.Minimal, "Terminating pigpio")
        self.pigpio.gpioTerminate()

    def send_data(self, data, maxMask, mustInvert, nb=1):
        """
        Processes and sends raw data by converting it into an IR code.
        
        Parameters:
            data (list): The raw data to send.
            maxMask (int): The maximum mask value for bit extraction.
            mustInvert (bool): Whether to invert the data.
            nb (int): Number of times to send the data.
        """
        self.__log(LogLevel.Minimal, f"Sending {'inverted ' if mustInvert else ''}data:")
        self.__log(LogLevel.Minimal, (' '.join('{:x}'.format(d) for d in data)).upper())
        
        # Convert raw data to IR code
        code = []
        for i in range(len(data)):
            idx = i if mustInvert else (len(data) - i - 1)
            mask = 1
            while mask < maxMask and mask > 0:
                if mustInvert:
                    code.append('1' if data[idx] & mask else '0')
                else:
                    code.insert(0, '1' if data[idx] & mask else '0')
                mask <<= 1
        
        # Send the processed IR code
        self.send_code(''.join(code), nb)
