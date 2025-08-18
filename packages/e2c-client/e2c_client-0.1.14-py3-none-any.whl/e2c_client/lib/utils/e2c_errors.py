E2C_ERRORS_ID = [
    0,
    5002,
    5003,
    5004,
    5005,
    5006,
    5007,
    5008,
    5009,
    5010,
    5011,
    5012,
    5013,
    5014,
    5015,
    5999,
]

E2C_ERROR_CODES = [
    "NO_ERROR",
    "TIMEOUT_ERROR",
    "REQUEST_ERROR",
    "MONUNPK_ERROR",
    "MANAGER_UNAVBLE",
    "ILLEGAL_MGRNAME",
    "CANDRV_ERROR",
    "CONUNPK_ERROR",
    "BADCHAN_ERROR",
    "CANWRT_ERROR",
    "CANREAD_ERROR",
    "FLUSHED_ERROR",
    "READ_PERM_DENIED",
    "WRITE_PERM_DENIED",
    "ACCESS_DENIED",
    "UNKNOWN_ERROR",
]

E2C_ERRORS_DESCRIPTION = [
    "No error",
    "CAN Bus Timeout",
    "Received request could not be parsed",
    "Unable to unpack monitor data",
    "Requested Manager Unavailable",
    "Request for an unknown Manager",
    "Low level can driver failure",
    "Error unpacking Control data structure",
    "Requested Channel unavailable for manager",
    "Error writing to the CAN bus",
    "Error reading from the CAN bus",
    "Operation was flushed by Server",
    "Permission to read from specified AmbManager Denied",
    "Permission to write to specified AmbManager Denied",
    "The AmbManager denied read/write access",
    "Otherwise undefined error condition",
]
E2C_ERRORS_DICT = {
    err_id: {"code": code, "description": desc}
    for err_id, code, desc in zip(
        E2C_ERRORS_ID, E2C_ERROR_CODES, E2C_ERRORS_DESCRIPTION
    )
}
