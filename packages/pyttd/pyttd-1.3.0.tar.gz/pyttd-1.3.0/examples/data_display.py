#!/usr/bin/env python3
"""
Data Display - Complete OpenTTD Game State Monitor

This example demonstrates how to retrieve and display all available
real-time game state data from an OpenTTD server.

Usage:
    python examples/data_display.py
"""

import time
import logging
import uuid

from pyttd import OpenTTDClient

# Set up clean logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    """Data display example"""
    logger.info("Starting Data Display Bot...")

    # Generate unique bot name
    unique_id = str(uuid.uuid4())[:8]

    # Create client
    client = OpenTTDClient(
        server="127.0.0.1",
        port=3979,
        player_name=f"DataBot_{unique_id}",
        company_name=f"DataCorp_{unique_id}",
    )

    def on_connected():
        logger.info("Connected to OpenTTD server!")

    def on_game_joined():
        logger.info("Successfully joined the game!")
        time.sleep(3)

        # Display comprehensive game data
        display_game_data()

    def display_game_data():
        """Display all available game data"""
        print("\n" + "=" * 80)
        print("OPENTTD GAME STATE DATA")
        print("=" * 80)

        # Game info
        game_info = client.get_game_info()
        if game_info:
            print(f"\nGAME INFORMATION:")
            print(f"  Current Year: {game_info.get('current_year', 'Unknown')}")
            print(f"  Start Year: {game_info.get('start_year', 'Unknown')}")
            print(
                f"  Companies: {game_info.get('companies', 0)}/{game_info.get('companies_max', 0)}"
            )
            print(f"  Clients: {game_info.get('clients', 0)}/{game_info.get('clients_max', 0)}")

        # Company data
        companies = client.get_companies()
        print(f"\nCOMPANIES ({len(companies)}):")
        for company_id, company in companies.items():
            print(f"  Company {company_id}: {company}")

        # Our company
        our_company = client.get_our_company()
        if our_company:
            print(f"\nOUR COMPANY:")
            print(our_company)

        # Economic status
        economy = client.get_economic_status()
        if economy:
            print(f"\nECONOMY:")
            print(f"  Interest Rate: {economy.get('interest_rate', 'Unknown')}%")

        print("\n" + "=" * 80)

    # Set up event handlers
    client.on("connected", on_connected)
    client.on("game_joined", on_game_joined)

    try:
        # Connect and run
        success = client.connect()
        if success:
            logger.info("Data Display Bot is running...")

            # Keep running and display data periodically
            while client.is_connected():
                time.sleep(60)
                if client.is_connected():
                    display_game_data()

        else:
            logger.error("Failed to connect to server")

    except KeyboardInterrupt:
        logger.info("Shutting down Data Display Bot...")

    finally:
        client.disconnect()
        logger.info("Data Display Bot shutdown complete")


if __name__ == "__main__":
    main()
