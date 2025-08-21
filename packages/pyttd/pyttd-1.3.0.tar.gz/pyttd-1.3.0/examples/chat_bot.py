#!/usr/bin/env python3
"""
Simple OpenTTD Bot Example
==========================

This bot demonstrates:
1. Connecting to an OpenTTD server
2. Creating a new company
3. Sending chat messages
4. Basic interaction

Usage:
    python examples/chat_bot.py
"""

import time
import logging
import uuid
from pyttd import OpenTTDClient

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    """Simple bot that joins, creates a company, and chats"""
    logger.info("Starting Simple OpenTTD Chat Bot...")

    # Generate unique bot name
    unique_id = str(uuid.uuid4())[:8]

    # Create client
    client = OpenTTDClient(
        server="127.0.0.1",
        port=3979,
        player_name=f"ChatBot_{unique_id}",
        company_name=f"ChatCorp_{unique_id}",
    )

    def on_connected():
        logger.info("Connected to OpenTTD server!")

    def on_game_joined():
        logger.info("Successfully joined the game!")

        # Give the system a moment to process everything
        time.sleep(2)

        # Send initial greeting
        greeting = f"Hello everyone! I'm {client.player_name}, a Python-powered OpenTTD bot!"
        client.send_chat(greeting)
        logger.info(f"Sent greeting: {greeting}")

        # Check our company status
        our_company = client.get_our_company()
        if our_company:
            # We have a company - celebrate!
            time.sleep(1)
            celebration = f"I've established {client.company_name} and I'm ready to build!"
            client.send_chat(celebration)
            logger.info(f"Sent celebration: {celebration}")

            time.sleep(1)
            motivation = "Let's build some amazing railways together!"
            client.send_chat(motivation)
            logger.info(f"Sent motivation: {motivation}")

            # Show off our starting money
            time.sleep(1)
            money = (
                getattr(our_company, "money", 500000) if hasattr(our_company, "money") else 500000
            )
            money_msg = f"Starting budget: £{money:,}"
            client.send_chat(money_msg)
            logger.info(f"Sent money status: {money_msg}")

        else:
            # Still spectating
            spectator_msg = "I'm currently spectating, but I'll create a company soon!"
            client.send_chat(spectator_msg)
            logger.info(f"Sent spectator message: {spectator_msg}")

    def on_chat(sender, message, _data):
        """Respond to chat messages"""
        logger.info(f"{sender}: {message}")

        # Respond if someone mentions us
        if client.player_name.lower() in message.lower():
            response = f"@{sender} Thanks for mentioning me! I'm a Python bot created to demonstrate OpenTTD automation! 🐍"
            client.send_chat(response)
            logger.info(f"Replied to {sender}: {response}")

        # Respond to greetings
        elif any(greeting in message.lower() for greeting in ["hello", "hi", "hey"]):
            if sender != client.player_name:  # Don't respond to ourselves
                response = f"Hello {sender}! Great to see you in the game!"
                client.send_chat(response)
                logger.info(f"Greeted {sender}: {response}")

    def on_error(error_msg):
        logger.error(f"Error: {error_msg}")

        # Send error message to chat if connected
        if client.is_connected():
            error_chat = f"Oops, I encountered an error: {error_msg}"
            client.send_chat(error_chat)

    # Set up event handlers
    client.on("connected", on_connected)
    client.on("game_joined", on_game_joined)
    client.on("chat", on_chat)
    client.on("error", on_error)

    try:
        # Connect and run
        success = client.connect()
        if success:
            logger.info("Bot is now running... Press Ctrl+C to stop")

            # Send periodic status updates
            message_count = 0
            while client.is_connected():
                time.sleep(30)  # Wait 30 seconds
                message_count += 1

                # Send a periodic status message
                status_msg = f"Status update #{message_count}: Still running strong!"
                client.send_chat(status_msg)
                logger.info(f"Sent status update: {status_msg}")

        else:
            logger.error("Failed to connect to server")

    except KeyboardInterrupt:
        logger.info("Shutting down bot...")
        if client.is_connected():
            goodbye_msg = f"{client.player_name} signing off!"
            client.send_chat(goodbye_msg)
            logger.info(f"Sent goodbye: {goodbye_msg}")
            time.sleep(1)  # Give time for message to send

    finally:
        client.disconnect()
        logger.info("Disconnected from server")
        logger.info("Simple OpenTTD Chat Bot shutdown complete")


if __name__ == "__main__":
    main()
