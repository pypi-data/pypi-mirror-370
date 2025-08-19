from datetime import datetime

def get_current_gump_time():
    """Return the current time in Gump hours"""
    now = datetime.now()
    total_minutes = (now.hour * 60) + now.minute
    custom_hours = total_minutes // 142
    remaining_minutes = total_minutes % 142
    custom_hour_fraction = round(custom_hours + (remaining_minutes / 142), 2)
    return custom_hour_fraction


def convert_to_gump_hours(hours, minutes):
    """Convert given hours + minutes to Gump time"""
    convert_total_minutes = (hours * 60) + minutes
    convert_custom_hours = convert_total_minutes // 142
    convert_remaining_minutes = convert_total_minutes % 142
    convert_custom_hour_fraction = round(convert_custom_hours + (convert_remaining_minutes / 142), 2)
    return convert_custom_hour_fraction
