#!/usr/bin/env python3
"""
Simple Finance Bot Example
===========================

This bot demonstrates basic company financial management:
1. Company creation and basic setup
2. Financial reporting
3. Simple loan management
4. Interactive chat commands

Usage:
    python examples/finance_bot.py
"""

import time
import logging
import uuid
from pyttd import OpenTTDClient

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    """Simple financial management bot"""
    logger.info("Starting Finance Management Bot...")

    # Generate unique bot name
    unique_id = str(uuid.uuid4())[:8]

    # Create client
    client = OpenTTDClient(
        server="127.0.0.1",
        port=3979,
        player_name=f"FinanceBot_{unique_id}",
        company_name=f"FinanceCorp_{unique_id}",
    )

    def on_connected():
        logger.info("Connected to OpenTTD server!")

    def on_game_joined():
        logger.info("Successfully joined the game!")

        # Give the system time to stabilize
        time.sleep(3)

        # Announce our presence
        client.send_chat(f"{client.player_name} is online!")

        # Check if we have a company
        our_company = client.get_our_company()
        if our_company:
            logger.info(f"Company established successfully!")
            time.sleep(2)

            # Demonstrate basic financial features
            demonstrate_financial_features()
        else:
            logger.warning("No company detected")
            client.send_chat("No company detected - staying as spectator for now")

    def demonstrate_financial_features():
        """Demonstrate key financial features"""

        # 1. Get and report current finances
        client.send_chat("Let me analyze our company finances...")
        time.sleep(2)

        finances = client.get_company_finances()
        if finances:
            client.send_chat("FINANCIAL SUMMARY:")
            time.sleep(1)
            client.send_chat(f"Cash: £{finances['money']:,}")
            time.sleep(1)
            client.send_chat(f"Loan: £{finances['loan']:,}")
            time.sleep(1)
            client.send_chat(f"Net Worth: £{finances['net_worth']:,}")
            time.sleep(2)

            # 2. Demonstrate loan management
            current_loan = finances["loan"]
            if current_loan < 300000:  # If loan is reasonable, demonstrate increase
                client.send_chat("Demonstrating loan increase for expansion capital...")
                time.sleep(2)
                success = client.increase_loan(50000)
                if success:
                    client.send_chat("Successfully increased loan by £50,000!")
                else:
                    client.send_chat("Loan increase failed")

            elif current_loan > 100000:  # If loan is high, demonstrate decrease
                client.send_chat("Demonstrating loan payment to reduce interest...")
                time.sleep(2)
                success = client.decrease_loan(25000)
                if success:
                    client.send_chat("Successfully paid down £25,000 of loan!")
                else:
                    client.send_chat("Loan payment failed")

            time.sleep(3)

            # 3. Demonstrate company renaming
            client.send_chat("Demonstrating company rebranding...")
            time.sleep(1)
            new_name = f"Premium Transport Co. {unique_id[:4]}"
            success = client.rename_company(new_name)
            if success:
                client.send_chat(f"Company renamed to: {new_name}")
            else:
                client.send_chat("Company rename failed")

            time.sleep(2)
            client.send_chat("Financial management demo complete! Ask me about 'finances' anytime!")

        else:
            client.send_chat("Could not retrieve financial data")

    def on_chat(sender, message, _data):
        """Handle chat messages and provide financial info"""
        logger.info(f"{sender}: {message}")

        # Don't respond to our own messages
        if sender == client.player_name:
            return

        message_lower = message.lower()

        # Financial report command
        if any(word in message_lower for word in ["finances", "financial", "money", "report"]):
            finances = client.get_company_finances()
            if finances:
                client.send_chat(f"@{sender} CURRENT FINANCIAL STATUS:")
                time.sleep(0.5)
                client.send_chat(f"Cash: £{finances['money']:,}")
                time.sleep(0.5)
                client.send_chat(f"Loan: £{finances['loan']:,}")
                time.sleep(0.5)
                client.send_chat(f"Net Worth: £{finances['net_worth']:,}")
                time.sleep(0.5)

                # Calculate and show loan interest
                annual_interest = client.calculate_loan_interest()
                client.send_chat(f"Annual loan interest: £{annual_interest:,}")
            else:
                client.send_chat(f"@{sender} Could not retrieve financial data")

        # Company performance command
        elif any(word in message_lower for word in ["company", "performance", "stats"]):
            performance = client.get_company_performance()
            if performance:
                client.send_chat(f"@{sender} COMPANY PERFORMANCE:")
                time.sleep(0.5)
                client.send_chat(f"Company Value: £{performance['company_value']:,}")
                time.sleep(0.5)
                client.send_chat(f"Age: {performance['age_years']} years")
                time.sleep(0.5)
                client.send_chat(f"Profitable: {performance['is_profitable']}")
            else:
                client.send_chat(f"@{sender} Could not retrieve performance data")

        # Loan management commands
        elif "loan" in message_lower and "increase" in message_lower:
            if finances := client.get_company_finances():
                success = client.increase_loan(50000)
                if success:
                    client.send_chat(f"@{sender} Increased loan by £50,000!")
                else:
                    client.send_chat(f"@{sender} Loan increase failed")

        elif "loan" in message_lower and "decrease" in message_lower:
            if finances := client.get_company_finances():
                success = client.decrease_loan(25000)
                if success:
                    client.send_chat(f"@{sender} Paid down £25,000 of loan!")
                else:
                    client.send_chat(f"@{sender} Loan payment failed")

        # Help command
        elif any(word in message_lower for word in ["help", "commands"]):
            client.send_chat(f"@{sender} Available commands:")
            time.sleep(0.5)
            client.send_chat("'finances' - Get financial report")
            time.sleep(0.5)
            client.send_chat("'company' - Get company performance")
            time.sleep(0.5)
            client.send_chat("'loan increase/decrease' - Manage loans")

        # Greeting responses
        elif any(greeting in message_lower for greeting in ["hello", "hi", "hey"]):
            if client.player_name.lower() in message_lower:
                client.send_chat(
                    f"Hello {sender}! I'm your financial advisor. Type 'help' for commands!"
                )

    def on_error(error_msg):
        logger.error(f"Error: {error_msg}")
        if client.is_connected():
            client.send_chat(f"System error: {error_msg}")

    # Set up event handlers
    client.on("connected", on_connected)
    client.on("game_joined", on_game_joined)
    client.on("chat", on_chat)
    client.on("error", on_error)

    try:
        # Connect and run
        success = client.connect()
        if success:
            logger.info("Finance Bot is running...")
            logger.info("Try typing 'finances' or 'company' in chat!")

            # Keep running and respond to chat
            while client.is_connected():
                time.sleep(30)  # Send periodic status
                client.send_chat("Finance Bot is active! Type 'help' for available commands.")

        else:
            logger.error("Failed to connect to server")

    except KeyboardInterrupt:
        logger.info("Shutting down Finance Bot...")
        if client.is_connected():
            client.send_chat("Finance Bot signing off!")
            time.sleep(1)

    finally:
        client.disconnect()
        logger.info("Finance Bot shutdown complete")


if __name__ == "__main__":
    main()
