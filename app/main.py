import requests
import reverse_geocoder
import pycountry
import logging

from time import sleep
from .db_handler import ISS_DBHandler
from datetime import datetime
from .logger_setup import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def get_iss_position() -> dict:
    response = requests.get("http://api.open-notify.org/iss-now.json")

    obj = response.json()

    return {
        "timestamp": obj["timestamp"],
        "latitude": obj["iss_position"]["latitude"],
        "longitude": obj["iss_position"]["longitude"],
    }


def get_country_from_coordinates(latitude: float, longitude: float) -> str:
    coordinates = (latitude, longitude)
    result = reverse_geocoder.search(coordinates)
    return result[0]["cc"] if result else "Error"


def iss_visit() -> None:
    db_handler = ISS_DBHandler()

    # Get current position
    position = get_iss_position()
    current_country_code = get_country_from_coordinates(
        float(position["latitude"]), float(position["longitude"])
    )

    country = pycountry.countries.get(alpha_2=current_country_code)
    country_name = country.name if country else current_country_code

    last_country = db_handler.get_last_country()

    # Only record a visit if the country has changed
    if country_name != last_country and current_country_code != "Error":
        db_handler.record_visit(
            country_name,
            float(position["latitude"]),
            float(position["longitude"]),
            position["timestamp"],
        )
        db_handler.update_last_country(country_name)
        logger.info(f"🚀 New country visit recorded: {country_name}")

    logger.info(
        f"🛰️  ISS Position: {position['latitude']}, {position['longitude']} at timestamp {position['timestamp']}"
    )
    logger.info(f"🌍 Current country: {country_name}")

    if country_name != last_country:
        logger.info("✅ Country change detected! New visit recorded.")
    else:
        logger.info(f"📍 Still over the same country: {country_name}")

    # Display visit statistics
    logger.info("📊 Visit Statistics:")
    stats = db_handler.get_visit_stats()
    for country_code, visit_count, first_visit, last_visit in stats[:10]:  # Top 10
        first_date = datetime.fromtimestamp(first_visit).strftime("%Y-%m-%d %H:%M")
        last_date = datetime.fromtimestamp(last_visit).strftime("%Y-%m-%d %H:%M")
        logger.info(
            f"  {country_code}: {visit_count} visits (First: {first_date}, Last: {last_date})"
        )


def continuous_tracking(interval_seconds: int = 5):
    """
    Continuously track ISS position and log country visits.

    Args:
        interval_seconds: How often to check the ISS position (default: 5 seconds)
    """
    logger.info(
        f"🚀 Starting continuous ISS tracking (checking every {interval_seconds} seconds)"
    )
    logger.info("Press Ctrl+C to stop")

    try:
        while True:
            try:
                iss_visit()
            except Exception as e:
                logger.error(f"❌ Error tracking ISS: {e}")

            # Wait for the specified interval
            sleep(interval_seconds)

    except KeyboardInterrupt:
        logger.info("🛑 Tracking stopped by user")


if __name__ == "__main__":
    continuous_tracking(interval_seconds=5)
