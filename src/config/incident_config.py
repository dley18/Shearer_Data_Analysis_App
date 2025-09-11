"""Incident configurations."""

INCIDENT_TYPE = {
    "event": "J_INCIDENT_EVENT",
    "warning": "J_INCIDENT_WARNING",
    "alarm": "J_INCIDENT_ALARM",
}

INCIDENT_STATE = {
    "one_shot": "J_INCIDENT_ONE_SHOT",
    "set": "J_INCIDENT_SET",
    "clear": "J_INCIDENT_CLEAR",
}

INCIDENT_ARGUMENTS = {
    "d": "longValue",
    "s": "stringTidxValue",
    "f": "realValue",
}

INCIDENT_COLORS = {
    "clear": "#77797d",
    "event": "#05e81b",
    "warning": "#e88605",
    "alarm": "#e80505",
    "black_text": "#000000",
}
