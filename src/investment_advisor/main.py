import os
import sys

from .crew import InvestmentAdvisorCrew
from .services.whatsapp_sender import (
    WhatsAppDeliveryError,
    format_report_for_whatsapp,
    send_whatsapp_message,
)

def run():
    inputs = {
        'query': 'What is the company you want to analyze?',
        'company_stock': 'AMZN',
    }
    return InvestmentAdvisorCrew().crew().kickoff(inputs=inputs)

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'query': 'What is last years revenue',
        'company_stock': 'AMZN',
    }
    try:
        InvestmentAdvisorCrew().crew().train(n_iterations=int(sys.argv[1]), inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")
    
if __name__ == "__main__":
    print("## Welcome to AI Investment Advisor")
    print('-------------------------------')
    result = run()
    print("\n\n########################")
    print("## Here is the Report")
    print("########################\n")
    print(result)

    try:
        message = format_report_for_whatsapp(result)
        send_whatsapp_message(message)
        print("\n[WhatsApp] Report delivered successfully.")
    except WhatsAppDeliveryError as err:
        print(f"\n[WhatsApp] Delivery skipped: {err}")
    except Exception as err:
        print(f"\n[WhatsApp] Unexpected error: {err}")
