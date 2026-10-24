from datetime import datetime, timedelta

import dateutil.parser
import pytz


class BaseModel(object):
    def __init__(self, **kwargs):
        self.param_defaults = {}

    @classmethod
    def json_transforms(cls, json_data):
        pass

    @classmethod
    def new_from_json_dict(cls, data, **kwargs):
        json_data = data.copy()
        if kwargs:
            for key, val in kwargs.items():
                json_data[key] = val

        cls.json_transforms(json_data)

        c = cls(**json_data)
        c._json = data
        return c


class ServerStatus(BaseModel):
    """Server Info and Status

    Server side status, default settings and capabilities

    Attributes:
        status (string): Server status
        version (string): Server version
        name (string): Server name
        apiEnabled (boolean): If the API is enabled
    """

    def __init__(self, **kwargs):
        self.param_defaults = {
            "status": None,
            "version": None,
            "name": None,
            "apiEnabled": None,
            "settings": None,
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))


class SGV(BaseModel):
    """Sensor Glucose Value

    Represents a single glucose measurement and direction at a specific time.

    Attributes:
        sgv (int): Glucose measurement value in mg/dl.
        sgv_mmol (int): Glucose measurement value in mmol/L.
        delta (float): Delta between current and previous value.
        date (datetime): The time of the measurementpa
        direction (string): One of ['DoubleUp', 'SingleUp', 'FortyFiveUp', 'Flat', 'FortyFiveDown', 'SingleDown', 'DoubleDown']
        device (string): the source of the measurement.  For example, 'share2', if pulled from Dexcom Share servers
    """

    def __init__(self, **kwargs):
        self.param_defaults = {
            "sgv": None,
            "sgv_mmol": None,
            "delta": None,
            "delta_mmol": None,
            "date": None,
            "direction": None,
            "device": None,
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))
        self.sgv_mmol = self.mgdlTommolL(self.sgv)
        self.delta_mmol = self.mgdlTommolL(self.delta)

    @classmethod
    def json_transforms(cls, json_data):
        if json_data.get("dateString"):
            json_data["date"] = dateutil.parser.parse(json_data["dateString"])
    
    def mgdlTommolL(self, mgdl):
        return round(mgdl / 18, 1)


class Treatment(BaseModel):
    """Nightscout Treatment

    Represents an entry in the Nightscout treatments store, such as boluses, carb entries,
    temp basals, etc. Many of the following attributes will be set to None, depending on
    the type of entry.

    Attributes:
        eventType (string): The event type. Examples: ['Temp Basal', 'Correction Bolus', 'Meal Bolus', 'BG Check']
        timestamp (datetime): The time of the treatment
        insulin (float): The amount of insulin delivered
        programmed (float): The amount of insulin programmed. May differ from insulin if the pump was suspended before delivery was finished.
        carbs (int): Amount of carbohydrates in grams consumed
        rate (float): Rate of insulin delivery for a temp basal, in U/hr.
        duration (int): Duration in minutes for a temp basal.
        enteredBy (string): The person who gave the treatment if entered in Care Portal, or the device that fetched the treatment from the pump.
        glucose (int): Glucose value for a BG check, in mg/dl.
        notes (string): Free text note attached to the treatment.
        insulinInjections (string): JSON-encoded list of the insulin injections recorded for this treatment, as sent by the uploader (for example '[{"insulin": "Humalog", "units": 5}]'). It is kept as the raw string and not parsed.
    """

    def __init__(self, **kwargs):
        self.param_defaults = {
            "temp": None,
            "enteredBy": None,
            "eventType": None,
            "glucose": None,
            "glucoseType": None,
            "units": None,
            "device": None,
            "created_at": None,
            "timestamp": None,
            "absolute": None,
            "rate": None,
            "duration": None,
            "carbs": None,
            "insulin": None,
            "unabsorbed": None,
            "suspended": None,
            "type": None,
            "programmed": None,
            "foodType": None,
            "absorptionTime": None,
            "notes": None,
            "insulinInjections": None,
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return "%s %s" % (self.timestamp, self.eventType)

    @classmethod
    def json_transforms(cls, json_data):
        timestamp = json_data.get("timestamp")
        if timestamp:
            if type(timestamp) == int:
                json_data["timestamp"] = datetime.fromtimestamp(
                    timestamp / 1000.0, pytz.utc
                )
            else:
                json_data["timestamp"] = dateutil.parser.parse(timestamp)
        if json_data.get("created_at"):
            json_data["created_at"] = dateutil.parser.parse(json_data["created_at"])


class ScheduleEntry(BaseModel):
    """ScheduleEntry

    Represents a change point in one of the schedules on a Nightscout profile.

    Attributes:
        offset (timedelta): The start offset of the entry
        value (float): The value of the entry.
    """

    def __init__(self, offset, value):
        self.offset = offset
        self.value = value

    @classmethod
    def new_from_json_dict(cls, data):
        seconds_offset = data.get("timeAsSeconds")
        if seconds_offset is None:
            hours, minutes = data.get("time").split(":")
            seconds_offset = int(hours) * 60 * 60 + int(minutes) * 60
        offset_in_seconds = int(seconds_offset)
        return cls(timedelta(seconds=offset_in_seconds), float(data["value"]))


class AbsoluteScheduleEntry(BaseModel):
    def __init__(self, start_date, value):
        self.start_date = start_date
        self.value = value

    def __repr__(self):
        return "%s = %s" % (self.start_date, self.value)


class Schedule(object):
    """Schedule

    Represents a schedule on a Nightscout profile.

    """

    def __init__(self, entries, timezone):
        self.entries = entries
        self.entries.sort(key=lambda e: e.offset)
        self.timezone = timezone

    # Expects a localized timestamp here
    def value_at_date(self, local_date):
        """Get scheduled value at given date

        Args:
            local_date: The datetime of interest.

        Returns:
            The value of the schedule at the given time.

        """
        offset = local_date - local_date.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        return [e.value for e in self.entries if e.offset <= offset][-1]

    def between(self, start_date, end_date):
        """Returns entries between given dates as AbsoluteScheduleEntry objects

        Times passed in should be timezone aware.  Times returned will have a tzinfo
        matching the schedule timezone.

        Args:
            start_date: The start datetime of the period to retrieve entries for.
            end_date: The end datetime of the period to retrieve entries for.

        Returns:
            An array of AbsoluteScheduleEntry objects.

        """
        if start_date > end_date:
            return []

        start_date = start_date.astimezone(self.timezone)
        end_date = end_date.astimezone(self.timezone)

        reference_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        start_offset = start_date - reference_date
        end_offset = start_offset + (end_date - start_date)
        if end_offset > timedelta(days=1):
            boundary_date = start_date + (timedelta(days=1) - start_offset)
            return self.between(start_date, boundary_date) + self.between(
                boundary_date, end_date
            )

        start_index = 0
        end_index = len(self.entries)

        for index, item in enumerate(self.entries):
            if start_offset >= item.offset:
                start_index = index
            if end_offset < item.offset:
                end_index = index
                break

        return [
            AbsoluteScheduleEntry(reference_date + entry.offset, entry.value)
            for entry in self.entries[start_index:end_index]
        ]

    @classmethod
    def new_from_json_array(cls, data, timezone):
        entries = [ScheduleEntry.new_from_json_dict(d) for d in data]
        return cls(entries, timezone)


class Profile(BaseModel):
    """Profile

    Represents a Nightscout profile.

    Attributes:
        dia (float): The duration of insulin action, in hours.
        carb_ratio (Schedule): A schedule of carb ratios, which are in grams/U.
        sens (Schedule): A schedule of insulin sensitivity values, which are in mg/dl/U.
        timezone (timezone): The timezone of the schedule.
        basal (Schedule): A schedule of basal rates, which are in U/hr.
        target_low (Schedule): A schedule the low end of the target range, in mg/dl.
        target_high (Schedule): A schedule the high end of the target range, in mg/dl.
    """

    def __init__(self, **kwargs):
        self.param_defaults = {
            "dia": None,
            "carb_ratio": None,
            "carbs_hr": None,
            "delay": None,
            "sens": None,
            "timezone": None,
            "basal": None,
            "target_low": None,
            "target_high": None,
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    @classmethod
    def json_transforms(cls, json_data):
        timezone = None
        if json_data.get("timezone"):
            timezone = pytz.timezone(json_data.get("timezone"))
            json_data["timezone"] = timezone
        if json_data.get("carbratio"):
            json_data["carbratio"] = Schedule.new_from_json_array(
                json_data.get("carbratio"), timezone
            )
        if json_data.get("sens"):
            json_data["sens"] = Schedule.new_from_json_array(
                json_data.get("sens"), timezone
            )
        if json_data.get("target_low"):
            json_data["target_low"] = Schedule.new_from_json_array(
                json_data.get("target_low"), timezone
            )
        if json_data.get("target_high"):
            json_data["target_high"] = Schedule.new_from_json_array(
                json_data.get("target_high"), timezone
            )
        if json_data.get("basal"):
            json_data["basal"] = Schedule.new_from_json_array(
                json_data.get("basal"), timezone
            )
        if json_data.get("dia"):
            json_data["dia"] = float(json_data["dia"])


class ProfileDefinition(BaseModel):
    """ProfileDefinition

    Represents a Nightscout profile definition, which can have multiple named profiles.

    Attributes:
        startDate (datetime): The time these profiles start at.
    """

    def __init__(self, **kwargs):
        self.param_defaults = {
            "defaultProfile": None,
            "store": None,
            "startDate": None,
            "created_at": None,
            "units": None,
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def get_default_profile(self):
        return self.store[self.defaultProfile]

    @classmethod
    def json_transforms(cls, json_data):
        if json_data.get("startDate"):
            json_data["startDate"] = dateutil.parser.parse(json_data["startDate"])
        if json_data.get("created_at"):
            json_data["created_at"] = dateutil.parser.parse(json_data["created_at"])
        if json_data.get("store"):
            store = {}
            for profile_name in json_data["store"]:
                store[profile_name] = Profile.new_from_json_dict(
                    json_data["store"][profile_name]
                )
            json_data["store"] = store


class ProfileDefinitionSet(object):
    """ProfileDefinitionSet

    Represents a set of Nightscout profile definitions, each covering a range of time
    from its start time, to the start time of the next profile definition, or until
    now if there are no newer profile defitions.

    """

    def __init__(self, profile_definitions):
        self.profile_definitions = profile_definitions
        self.profile_definitions.sort(key=lambda d: d.startDate)

    def get_profile_definition_active_at(self, date):
        """Get the profile definition active at a given datetime

        Args:
            date: The profile definition containing this time will be returned.

        Returns:
            A ProfileDefinition object valid for the specified time.

        """
        return [d for d in self.profile_definitions if d.startDate <= date][-1]

    @classmethod
    def new_from_json_array(cls, data):
        defs = [ProfileDefinition.new_from_json_dict(d) for d in data]
        return cls(defs)


class DeviceStatus(BaseModel):
    """DeviceStatus

    Represents a Device on Nightscout. For example a MiaoMiao reader.

    Attributes:
        device (string): Device type and hostname for example openaps://hostname.
        created_at (datetime): Created date.
        openaps (string): OpenAPS devicestatus record.
        loop (string): Loop devicestatus record.
        pump (PumpDevice): Pump device.
        uploader (UploaderBattery): Uploader device's battery.
        xdripjs (XDripJs): xDripJS device.
    """

    def __init__(self, **kwargs):
        self.param_defaults = {
            "device": None,
            "created_at": None,
            "openaps": None,
            "loop": None,
            "pump": None,
            "uploader": None,
            "xdripjs": None,
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    @classmethod
    def json_transforms(cls, json_data):
        if json_data.get("created_at"):
            json_data["created_at"] = dateutil.parser.parse(json_data["created_at"])
        if json_data.get("pump"):
            json_data["pump"] = PumpDevice.new_from_json_dict(json_data["pump"])
        if json_data.get("uploader"):
            json_data["uploader"] = UploaderBattery.new_from_json_dict(
                json_data["uploader"]
            )
        if json_data.get("xdripjs"):
            json_data["xdripjs"] = XDripJs.new_from_json_dict(json_data["xdripjs"])


class XDripJs(BaseModel):
    """XDripJs

    Represents a xDrip-js source.

    Attributes:
        state (int): CGM Sensor Session State Code
        stateString (string): CGM Sensor Session State String
        stateStringShort (string): CGM Sensor Session State Short String
        txId (string): CGM Transmitter ID
        txStatus (float): CGM Transmitter Status
        txStatusString (string): CGM Transmitter Status String
        txStatusStringShort (string): CGM Transmitter Status Short String
        txActivation (int): CGM Transmitter Activation Milliseconds After Epoch
        mode (string): Mode xdrip-js Application Operationg: expired, not expired, etc.
        timestamp (int): Last Update Milliseconds After Epoch
        rssi (int): Receive Signal Strength of Transmitter
        unfiltered (int): Most Recent Raw Unfiltered Glucose
        filtered (int): Most Recent Raw Filtered Glucose
        noise (int): Calculated Noise Value - 1=Clean, 2=Light, 3=Medium, 4=Heavy
        noiseString (float): Noise Value String
        slope (float): Calibration Slope Value
        intercept (int): Calibration Intercept Value
        calType (string): Algorithm Used to Calculate Calibration Values
        lastCalibrationDate (int): Most Recent Calibration Milliseconds After Epoch
        sessionStart (int): Sensor Session Start Milliseconds After Epoch
        batteryTimestamp (int): Most Recent Batter Status Read Milliseconds After Epoch
        voltagea (float): Voltage of Battery A
        voltageb (float): Voltage of Battery B
        temperature (float): Transmitter Temperature
        resistance (float): Sensor Resistance
    """

    def __init__(self, **kwargs):
        self.param_defaults = {
            "state": None,
            "stateString": None,
            "stateStringShort": None,
            "txId": None,
            "txStatus": None,
            "txStatusString": None,
            "txStatusStringShort": None,
            "txActivation": None,
            "mode": None,
            "timestamp": None,
            "rssi": None,
            "unfiltered": None,
            "filtered": None,
            "noise": None,
            "noiseString": None,
            "slope": None,
            "intercept": None,
            "calType": None,
            "lastCalibrationDate": None,
            "sessionStart": None,
            "batteryTimestamp": None,
            "voltagea": None,
            "voltageb": None,
            "temperature": None,
            "resistance": None,
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))


class UploaderBattery(BaseModel):
    """UploaderBattery

    Represents a Uploader device's battery on Nightscout.

    Attributes:
        batteryVoltage (float): Battery Voltage.
        battery (int): Battery percentage.
        type (string): Uploader type.
    """

    def __init__(self, **kwargs):
        self.param_defaults = {
            "batteryVoltage": None,
            "battery": None,
            "type": None,
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))


class PumpDevice(BaseModel):
    """PumpDevice

    Represents a Pump device on Nightscout.

    Attributes:
        clock (datetime): Clock datetime.
        battery (PumpBattery): Pump battery details.
        reservoir (float): Amount of insulin remaining in pump reservoir.
        status (PumpStatus): Pump status details.
    """

    def __init__(self, **kwargs):
        self.param_defaults = {
            "clock": None,
            "battery": None,
            "reservoir": None,
            "status": None,
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    @classmethod
    def json_transforms(cls, json_data):
        if json_data.get("clock"):
            json_data["clock"] = dateutil.parser.parse(json_data["clock"])
        if json_data.get("battery"):
            json_data["battery"] = PumpBattery.new_from_json_dict(json_data["battery"])
        if json_data.get("status"):
            json_data["status"] = PumpStatus.new_from_json_dict(json_data["status"])


class PumpBattery(BaseModel):
    """PumpBattery

    Represents the Pump's battery on Nightscout.

    Attributes:
        status (string): Pump Battery Status String. For example "normal".
        voltage (float): Pump Battery Voltage Level.
    """

    def __init__(self, **kwargs):
        self.param_defaults = {
            "clock": None,
            "battery": None,
            "reservoir": None,
            "status": None,
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))


class PumpStatus(BaseModel):
    """PumpStatus

    Represents a Pump device status on Nightscout.

    Attributes:
        status (string): Pump Status String.
        bolusing (boolean): Is Pump Bolusing.
        suspended (boolean): Is Pump Suspended.
        timestamp (datetime): Date time of entry.
    """

    def __init__(self, **kwargs):
        self.param_defaults = {
            "clock": None,
            "battery": None,
            "reservoir": None,
            "status": None,
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    @classmethod
    def json_transforms(cls, json_data):
        timestamp = json_data.get("timestamp")
        if timestamp:
            if type(timestamp) == int:
                json_data["timestamp"] = datetime.fromtimestamp(
                    timestamp / 1000.0, pytz.utc
                )
            else:
                json_data["timestamp"] = dateutil.parser.parse(timestamp)
