"""Module to encode soil power sensor protobuf messages

Encoding a response can be performed with

    encode_response()

Each type of measurement has a corresponding encoding function as follows:

    PowerMeasurement -> encode_power_measurement()
    Teros12Measurement -> encode_teros12_measurement()
"""

from .soil_power_sensor_pb2 import (
    Measurement,
    Response,
    UserConfiguration,
    EnabledSensor,
    Uploadmethod,
)


def encode_response(success: bool = True) -> bytes:
    """Encodes a Response message

    The response indicates there was a successful upload, otherwise indicates an
    error.

    Args:
        success: Specifies whether to encode a success or failure.

    Returns:
        Byte string of response message.
    """

    # format response
    response = Response()
    if success:
        response.resp = Response.ResponseType.SUCCESS
    else:
        response.resp = Response.ResponseType.ERROR

    # return encode message
    return response.SerializeToString()


def encode_power_measurement(
    ts: int, cell_id: int, logger_id: int, voltage: float, current: float
) -> bytes:
    """Encodes a PowerMeasurement within the Measurement message

    Args:
        ts: Timestamp in unix epochs
        cell_id: Cell Id from Dirtviz
        logger_id: Logger Id from Dirtviz
        voltage: Voltage in V (Volts)
        current: Current in A (Amps)

    Returns:
        Serialized Power measurement
    """

    meas = Measurement()

    # metadata
    meas.meta.ts = ts
    meas.meta.cell_id = cell_id
    meas.meta.logger_id = logger_id

    # power
    meas.power.voltage = voltage
    meas.power.current = current

    return meas.SerializeToString()


def encode_teros12_measurement(
    ts: int,
    cell_id: int,
    logger_id: int,
    vwc_raw: float,
    vwc_adj: float,
    temp: float,
    ec: int,
) -> bytes:
    """Encodes a Teros12Measurment within the Measurement message

    Args:
        ts: Timestamp in unix epochs
        cell_id: Cell Id from Dirtviz
        logger_id: Logger Id from Dirtviz
        vwc_raw: Raw volumetric water content from Teros12
        vwc_adj: Volumetric water content from Teros12 with calibration applied
        temp: Temperature in C
        ec: Electrical conductivity

    Returns:
        Serialized Teros12 measurement
    """

    meas = Measurement()

    # metadata
    meas.meta.ts = ts
    meas.meta.cell_id = cell_id
    meas.meta.logger_id = logger_id

    # teros12
    meas.teros12.vwc_raw = vwc_raw
    meas.teros12.vwc_adj = vwc_adj
    meas.teros12.temp = temp
    meas.teros12.ec = ec

    return meas.SerializeToString()


def encode_phytos31_measurement(
    ts: int, cell_id: int, logger_id: int, voltage: float, leaf_wetness: float
) -> bytes:
    """Encodes a Phytos31Measurement within the Measurement message

    Args:
        ts: Timestamp in unix epochs
        cell_id: Cell Id from Dirtviz
        logger_id: Logger Id from Dirtviz
        voltage: Raw voltage reading
        leaf_wetness: Calibrated leaf wetness

    Returns:
        Serialized Phytos31 measurement
    """

    meas = Measurement()

    # metadata
    meas.meta.ts = ts
    meas.meta.cell_id = cell_id
    meas.meta.logger_id = logger_id

    # phytos31
    meas.phytos31.voltage = voltage
    meas.phytos31.leaf_wetness = leaf_wetness
    return meas.SerializeToString()

    return meas.SerializeToString()


def encode_bme280_measurement(
    ts: int,
    cell_id: int,
    logger_id: int,
    pressure: int,
    temperature: int,
    humidity: int,
):
    """Encodes a BME280Measurement within the Measurement message

    The following raw values correspond to the following SI units

    *Raw*

    pressure: 98473
    temperature: 2275
    humidity: 43600

    *SI Units*

    pressure: 9847.3 hPa
    temperature: 22.75 C
    humidity: 43.600 %

    Args:
        ts: Timestamp in unix epochs
        cell_id: Cell Id from Dirtviz
        logger_id: Logger Id from Dirtviz
        pressure: Ambient pressure
        temperature: Ambient temperature
        humidity: Relative humidity

    Returns:
        Serialized BME280 Measurement
    """

    meas = Measurement()

    # metadata
    meas.meta.ts = ts
    meas.meta.cell_id = cell_id
    meas.meta.logger_id = logger_id

    # bme280
    meas.bme280.pressure = pressure
    meas.bme280.temperature = temperature
    meas.bme280.humidity = humidity

    return meas.SerializeToString()


def encode_teros21_measurement(
    ts: int,
    logger_id: int,
    cell_id: int,
    matric_pot: float,
    temp: float,
) -> bytes:

    meas = Measurement()

    # metadata
    meas.meta.ts = ts
    meas.meta.cell_id = cell_id
    meas.meta.logger_id = logger_id

    meas.teros21.matric_pot = matric_pot
    meas.teros21.temp = temp

    return meas.SerializeToString()


def encode_user_configuration(
    logger_id: int,
    cell_id: int,
    Upload_method: str,
    Upload_interval: int,
    Enabled_sensors: list,
    Voltage_Slope: float,
    Voltage_Offset: float,
    Current_Slope: float,
    Current_Offset: float,
    WiFi_SSID: str,
    WiFi_Password: str,
    API_Endpoint_URL: str,
    API_Endpoint_Port: int,
) -> bytes:
    """Encodes a UserConfiguration message

    Args:
        logger_id: ID of the logger.
        cell_id: ID of the cell.
        Upload_method: indicates whether LoRa or WiFi is used
        Upload_interval: upload time in seconds
        Enabled_sensors: used sensors
        Voltage_Slope: Calibration slope for voltage.
        Voltage_Offset: Calibration offset for voltage.
        Current_Slope: Calibration slope for current.
        Current_Offset: Calibration offset for current.
        WiFi_SSID: WiFi SSID.
        WiFi_Password: WiFi password.
        API_Endpoint_URL
        API_Endpoint_Port

    Returns:
        Serialized UserConfiguration message
    """

    user_config = UserConfiguration()

    user_config.logger_id = logger_id
    user_config.cell_id = cell_id
    user_config.Upload_method = Upload_method
    user_config.Upload_interval = Upload_interval
    # Convert Upload_method to enum
    if Upload_method.lower() == "lora":
        user_config.Upload_method = Uploadmethod.LoRa
    elif Upload_method.lower() == "wifi":
        user_config.Upload_method = Uploadmethod.WiFi
    else:
        raise ValueError("Invalid Upload_method: must be 'LoRa' or 'WiFi'")

    # Check for duplicates in Enabled_sensors
    seen_sensors = set()
    for sensor in Enabled_sensors:
        if sensor in seen_sensors:
            raise ValueError(f"Duplicate sensor found: {sensor}")
        seen_sensors.add(sensor)

        # Append to enabled_sensors based on the enum mapping
        if sensor.lower() == "voltage":
            user_config.enabled_sensors.append(EnabledSensor.Voltage)
        elif sensor.lower() == "current":
            user_config.enabled_sensors.append(EnabledSensor.Current)
        elif sensor.lower() == "teros12":
            user_config.enabled_sensors.append(EnabledSensor.Teros12)
        elif sensor.lower() == "teros21":
            user_config.enabled_sensors.append(EnabledSensor.Teros21)
        elif sensor.lower() == "bme280":
            user_config.enabled_sensors.append(EnabledSensor.BME280)
        else:
            raise ValueError(f"Invalid EnabledSensor: {sensor}")
    user_config.Voltage_Slope = Voltage_Slope
    user_config.Voltage_Offset = Voltage_Offset
    user_config.Current_Slope = Current_Slope
    user_config.Current_Offset = Current_Offset
    user_config.WiFi_SSID = WiFi_SSID
    user_config.WiFi_Password = WiFi_Password
    user_config.API_Endpoint_URL = API_Endpoint_URL
    user_config.API_Endpoint_Port = API_Endpoint_Port

    return user_config.SerializeToString()
