#!/usr/bin/env python3
"""
Company Manager Bot Example
============================

This bot demonstrates company management features:
1. Creating and managing companies
2. Financial operations (loans, money transfers)
3. Company customization (names, colors)
4. Performance tracking and reporting
5. Economic analysis and decision making

Usage:
    python examples/manager_bot.py
"""

import time
import logging
import uuid
from pyttd import OpenTTDClient
from pyttd.commands import CommandBuilder

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class CompanyManagerBot:
    """Advanced company management bot"""

    def __init__(self, server="127.0.0.1", port=3979):
        self.unique_id = str(uuid.uuid4())[:8]
        self.client = OpenTTDClient(
            server=server,
            port=port,
            player_name=f"ManagerBot_{self.unique_id}",
            company_name=f"MegaCorp_{self.unique_id}",
        )
        self.management_actions_performed = 0
        self.financial_reports = []

    def setup_event_handlers(self):
        """Set up event handlers"""
        self.client.on("connected", self.on_connected)
        self.client.on("game_joined", self.on_game_joined)
        self.client.on("chat", self.on_chat)
        self.client.on("error", self.on_error)

    def on_connected(self):
        logger.info("Connected to OpenTTD server!")

    def on_game_joined(self):
        logger.info("Successfully joined the game!")

        # Give the system time to stabilize
        time.sleep(3)

        # Announce our presence
        self.client.send_chat(f"{self.client.player_name} reporting for duty!")

        # Check if we have a company
        our_company = self.client.get_our_company()
        if our_company:
            logger.info(f"Successfully created company!")
            self.perform_company_setup()
        else:
            logger.warning("No company detected - staying as spectator for now")

    def perform_company_setup(self):
        """Perform initial company setup and branding"""
        logger.info("Starting company setup and branding...")

        time.sleep(2)
        self.client.send_chat("Customizing our company branding...")

        # 1. Rename company to something more professional
        professional_name = f"TransportTech Solutions {self.unique_id[:4]}"
        success = self.client.rename_company(professional_name)
        if success:
            self.client.send_chat(f"📝 Company renamed to: {professional_name}")
        time.sleep(3)  # Longer delay between operations

        # 2. Set a professional president name
        president_name = f"CEO {self.unique_id[:4]}"
        success = self.client.rename_president(president_name)
        if success:
            self.client.send_chat(f"New CEO appointed: {president_name}")
        time.sleep(3)  # Longer delay between operations

        # 3. Set company colors (blue scheme)
        success = self.client.set_company_colour(scheme=0, primary=True, colour=1)  # Blue
        if success:
            self.client.send_chat("Company livery updated to professional blue scheme!")
        time.sleep(3)  # Longer delay between operations

        # 4. Analyze initial finances
        self.analyze_and_report_finances()

        # 5. Optimize loan structure
        time.sleep(2)
        self.optimize_loan_structure()

    def analyze_and_report_finances(self):
        """Analyze and report company financial status"""
        logger.info("Analyzing company finances...")

        finances = self.client.get_company_finances()
        performance = self.client.get_company_performance()
        economic_status = self.client.get_economic_status()

        if not finances:
            logger.warning("Could not retrieve financial data")
            return

        # Store financial report
        report = {
            "timestamp": time.time(),
            "finances": finances,
            "performance": performance,
            "economic_status": economic_status,
        }
        self.financial_reports.append(report)

        # Send financial summary to chat
        self.client.send_chat("FINANCIAL REPORT:")
        time.sleep(0.5)
        self.client.send_chat(f"Cash: £{finances['money']:,}")
        time.sleep(0.5)
        self.client.send_chat(f"Loan: £{finances['loan']:,}")
        time.sleep(0.5)
        self.client.send_chat(f"Net Worth: £{finances['net_worth']:,}")
        time.sleep(0.5)

        # Calculate and report loan interest
        annual_interest = self.client.calculate_loan_interest()
        self.client.send_chat(f"Annual loan interest: £{annual_interest:,}")
        time.sleep(0.5)

        # Report debt ratio
        debt_ratio = finances.get("debt_ratio", 0)
        if debt_ratio > 0.5:
            self.client.send_chat(f"High debt ratio: {debt_ratio:.1%} - consider reducing loan")
        else:
            self.client.send_chat(f"Healthy debt ratio: {debt_ratio:.1%}")

        logger.info(f"Financial analysis complete - Net worth: £{finances['net_worth']:,}")

    def optimize_loan_structure(self):
        """Optimize company loan based on current finances"""
        logger.info("Optimizing loan structure...")

        finances = self.client.get_company_finances()
        if not finances:
            return

        money = finances["money"]
        loan = finances["loan"]
        max_loan = finances.get("max_loan", 500000)  # Default max loan
        available_credit = finances.get("available_credit", max_loan - loan)

        self.client.send_chat("Analyzing optimal loan structure...")
        time.sleep(1)

        # Strategy: If we have too much cash, pay down some loan
        # If we need more working capital, consider increasing loan

        if money > 300000 and loan > 50000:
            # We have excess cash, pay down some loan to reduce interest
            paydown_amount = min(100000, money - 200000, loan)  # Keep 200k cash buffer
            if paydown_amount > 0:
                success = self.client.decrease_loan(paydown_amount)
                if success:
                    self.client.send_chat(
                        f"Paying down £{paydown_amount:,} of loan to reduce interest costs"
                    )
                    time.sleep(1)

        elif money < 100000 and available_credit > 50000:
            # We're low on cash, consider taking more loan for working capital
            loan_increase = min(100000, available_credit)
            success = self.client.increase_loan(loan_increase)
            if success:
                self.client.send_chat(f"Increased loan by £{loan_increase:,} for working capital")
                time.sleep(1)

        # Re-analyze after changes
        time.sleep(2)
        new_finances = self.client.get_company_finances()
        if new_finances and new_finances != finances:
            self.client.send_chat("Loan optimization complete! New financial position:")
            time.sleep(0.5)
            self.client.send_chat(f"New cash position: £{new_finances['money']:,}")

    def demonstrate_money_transfer(self):
        """Demonstrate money transfer capabilities"""
        # Check if there are other companies to transfer to
        companies = self.client.get_companies()
        other_companies = [
            cid for cid in companies.keys() if cid != int(self.client.game_state.company_id)
        ]

        if other_companies and len(other_companies) > 0:
            target_company = other_companies[0]
            transfer_amount = 25000

            finances = self.client.get_company_finances()
            if finances and finances["money"] > transfer_amount * 2:
                self.client.send_chat(f"Demonstrating corporate partnership...")
                time.sleep(1)

                success = self.client.give_money(transfer_amount, target_company)
                if success:
                    self.client.send_chat(
                        f"Transferred £{transfer_amount:,} to Company {target_company} as goodwill gesture!"
                    )
        else:
            self.client.send_chat("No other companies available for money transfer demonstration")

    def on_chat(self, sender, message, _data):
        """Handle chat messages and respond to commands"""
        logger.info(f"{sender}: {message}")

        # Don't respond to our own messages
        if sender == self.client.player_name:
            return

        message_lower = message.lower()

        # Respond to financial inquiries
        if any(word in message_lower for word in ["money", "finances", "financial", "report"]):
            self.client.send_chat(f"@{sender} Here's our latest financial snapshot:")
            time.sleep(0.5)
            self.analyze_and_report_finances()

        # Respond to company information requests
        elif any(word in message_lower for word in ["company", "performance", "stats"]):
            performance = self.client.get_company_performance()
            if performance:
                self.client.send_chat(f"@{sender} Company Performance Report:")
                time.sleep(0.5)
                self.client.send_chat(f"Company Value: £{performance['company_value']:,}")
                time.sleep(0.5)
                self.client.send_chat(f"Performance Rating: {performance['performance_rating']}")

        # Respond to greetings
        elif (
            any(greeting in message_lower for greeting in ["hello", "hi", "hey"])
            and self.client.player_name.lower() in message_lower
        ):
            responses = [
                f"Hello {sender}! I'm an automated company manager",
                f"Greetings {sender}! Currently managing our transport empire",
                f"Hi {sender}! Ask me about our company finances anytime!",
            ]
            import random

            response = random.choice(responses)
            self.client.send_chat(response)

    def on_error(self, error_msg):
        logger.error(f"Error: {error_msg}")
        if self.client.is_connected():
            self.client.send_chat(f"⚠️ System alert: {error_msg}")

    def run_periodic_management(self):
        """Run periodic management tasks"""
        logger.info("Starting periodic management cycle...")

        while self.client.is_connected():
            try:
                time.sleep(60)  # Wait 60 seconds between management cycles

                self.management_actions_performed += 1

                # Every cycle: Update financial analysis
                self.analyze_and_report_finances()

                # Every 3rd cycle: Demonstrate advanced features
                if self.management_actions_performed % 3 == 0:
                    self.client.send_chat("Performing company management tasks...")
                    time.sleep(1)

                    # Demonstrate money transfer (if applicable)
                    self.demonstrate_money_transfer()

                    # Re-optimize loan structure
                    time.sleep(2)
                    self.optimize_loan_structure()

                # Every 5th cycle: Company performance summary
                if self.management_actions_performed % 5 == 0:
                    performance = self.client.get_company_performance()
                    if performance:
                        self.client.send_chat("PERFORMANCE MILESTONE REACHED!")
                        time.sleep(0.5)
                        self.client.send_chat(
                            f"Management cycles completed: {self.management_actions_performed}"
                        )
                        time.sleep(0.5)
                        self.client.send_chat(f"Company age: {performance['age_years']} years")
                        time.sleep(0.5)
                        self.client.send_chat(f"Current net worth: £{performance['net_worth']:,}")

                # Status update
                status_msg = f"Management Cycle #{self.management_actions_performed} complete - All systems operational!"
                self.client.send_chat(status_msg)
                logger.info(f"Completed management cycle #{self.management_actions_performed}")

            except Exception as e:
                logger.error(f"Error in management cycle: {e}")
                if self.client.is_connected():
                    self.client.send_chat(f"Management system error: {e}")

    def run(self):
        """Start the company manager bot"""
        logger.info("Starting Company Manager Bot...")

        self.setup_event_handlers()

        try:
            success = self.client.connect()
            if success:
                logger.info("Company Manager Bot is now running...")
                logger.info("Type 'finances' or 'company' in chat to get reports!")

                # Run periodic management tasks
                self.run_periodic_management()
            else:
                logger.error("Failed to connect to server")

        except KeyboardInterrupt:
            logger.info("Shutting down Company Manager Bot...")
            if self.client.is_connected():
                self.client.send_chat("Company Manager Bot signing off.")
                time.sleep(1)

        finally:
            self.client.disconnect()
            logger.info("Company Manager Bot shutdown complete")

            # Print final summary
            if self.financial_reports:
                logger.info(f"Generated {len(self.financial_reports)} financial reports")
                logger.info(f"Completed {self.management_actions_performed} management cycles")


def main():
    """Main entry point"""
    bot = CompanyManagerBot()
    bot.run()


if __name__ == "__main__":
    main()
