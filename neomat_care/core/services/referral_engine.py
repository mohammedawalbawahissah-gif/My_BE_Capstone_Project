from core.models import HealthFacility, Transport
from .distance import haversine_distance

CRITICAL_SIGNS = ["seizure", "unconscious", "cardiac arrest"]
HIGH_SIGNS = ["bleeding", "prolonged_labour", "fetal_distress"]

def determine_priority(danger_signs):
    for sign in danger_signs:
        if sign in CRITICAL_SIGNS:
            return "CRITICAL"
        if sign in HIGH_SIGNS:
            return "HIGH"
    return "MODERATE"


def find_best_facility(case, latitude, longitude):

    facilities = HealthFacility.objects.all()
    capable = []

    for facility in facilities:
        if facility.capacity <= 0:
            continue

        distance = haversine_distance(latitude, longitude,
                                      facility.latitude, facility.longitude)

        capable.append((facility, distance))

    capable.sort(key=lambda x: x[1])
    return capable[0] if capable else None


def find_transport(latitude, longitude):
    transports = Transport.objects.filter(status="available")
    options = []

    for t in transports:
        dist = haversine_distance(latitude, longitude,
                                  t.current_latitude, t.current_longitude)
        options.append((t, dist))

    options.sort(key=lambda x: x[1])
    return options[0] if options else None


def generate_referral(case, latitude, longitude):

    priority = determine_priority(case.danger_signs)

    facility = find_best_facility(case, latitude, longitude)
    transport = find_transport(latitude, longitude)

    return {
        "priority": priority,
        "facility": facility,
        "transport": transport
    }
