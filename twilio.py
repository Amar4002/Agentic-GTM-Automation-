from twilio.rest import Client
import re

class TwilioWhatsAppClient:
    def __init__(self, account_sid, auth_token, from_number):
        if not all([account_sid, auth_token, from_number]):
            raise ValueError("Twilio credentials missing")
        
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number

    def _normalize(self, phone: str):
        """
        Convert a phone number to WhatsApp E.164 format.
        Removes non-digits and adds 'whatsapp:+'
        """
        digits = re.sub(r"\D", "", phone)
        return f"whatsapp:+{digits}"

    def send_whatsapp(self, to: str, body: str):
        """
        Sends a WhatsApp message via Twilio.
        Returns the Twilio message object.
        """
        to_norm = self._normalize(to)
        message = self.client.messages.create(
            from_=self.from_number,
            body=body,
            to=to_norm
        )
        return message
