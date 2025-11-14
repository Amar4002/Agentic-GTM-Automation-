from pathlib import Path
import argparse
import pandas as pd
from datetime import datetime
import time
import os
from dotenv import load_dotenv

from llm.gemini_client import GeminiClient

from messaging.twilio_client import TwilioWhatsAppClient
from utils.logging_utils import CSVLogger

load_dotenv()

DEFAULT_LOG = "output_log.csv" 


def parse_args():
    p = argparse.ArgumentParser(description="Agentic GTM Automation (Gemini + Twilio)")

    p.add_argument("--crm-path", type=Path, required=True, help="sample_30_leads.csv")
    
    p.add_argument("--log-path", type=Path, default=Path(DEFAULT_LOG), help="")
    
    p.add_argument("--days-threshold", type=int, default=3, help="Follow-up threshold in days")
    
    p.add_argument("--dry-run", action="store_true", help="Don’t send messages; log only")
    
    return p.parse_args()


def prepare_df(path: Path):
    df = pd.read_csv(path)


    df["LastContactDate"] = pd.to_datetime(df["LastContactDate"], errors="coerce")
    return df


def main():
    args = parse_args()

    if not args.crm_path.exists():
        raise FileNotFoundError(f"CRM file not found: {args.crm_path}")

    df = prepare_df(args.crm_path)
    today = datetime.utcnow().date()

    # Instantiate clients
    llm_key = os.getenv("api key ")
    llm = GeminiClient(api_key=llm_key)

    twilio_account = os.getenv("Account_SID")
    twilio_token = os.getenv("Auth_Token")
    twilio_from = os.getenv("Whatsapp_from")

    whatsapp_client = TwilioWhatsAppClient(
        account_sid=twilio_account,
        auth_token=twilio_token,
        from_number=twilio_from
    )

    logger = CSVLogger(args.log_path)

    for _, row in df.iterrows():
        name = row.get("Name")
        phone = str(row.get("Phone"))
        last_msg = row.get("LastMessage", "")
        last_contact = row.get("LastContactDate")

        if pd.isna(last_contact):
            print(f"[WARN] Skipping {name}: last contact date invalid")
            continue

        days_since = (today - last_contact.date()).days

        # Skip if recently contacted
        if days_since <= args.days_threshold:
            print(f"[SKIP] {name}: contacted {days_since} day(s) ago")
            logger.log({
                "Name": name,
                "Phone": phone,
                "Channel": "WhatsApp",
                "Decision": "Skip",
                "ProviderMessageSid": "",
                "ProviderStatus": "Skipped",
                "LLMPrompt": "",
                "LLMOutput": "",
                "Timestamp": datetime.utcnow().isoformat()
            })
            continue

        # LLM PROMPT (must remain visible)
        prompt = (
            f"You are a short professional sales follow-up assistant. "
            f"Create a concise WhatsApp follow-up message (<= 160 chars).\n\n"
            f"Name: {name}\n"
            f"LastMessage: {last_msg}\n"
            f"DaysSince: {days_since}\n\n"
            f"Reply with only the message text (no explanations)."
        )

        # Generate message with Gemini
        try:
            llm_output = llm.generate(prompt)
            message_text = llm_output.strip()
        except Exception as e:
            print(f"[ERROR] Gemini failed for {name}: {e}")
            message_text = f"Hi {name}, following up on our last chat. Are you available this week?"

        print(f"[INFO] LLM message for {name}: {message_text}")

        # Dry-run mode
        if args.dry_run:
            provider_response = {"sid": "dryrun", "status": "dry_run"}
        else:
            # Try sending with retries
            provider_response = {"sid": "", "status": "failed"}
            for attempt in range(1, 4):  # 3 attempts
                try:
                    resp = whatsapp_client.send_whatsapp(
                        to=phone,
                        body=message_text
                    )
                    provider_response = {"sid": resp.sid, "status": resp.status}
                    print(f"[SENT] to {name}: SID={resp.sid}")
                    break
                except Exception as e:
                    print(f"[WARN] Attempt {attempt} failed for {name}: {e}")
                    time.sleep(attempt * 2)

        # Log result
        logger.log({
            "Name": name,
            "Phone": phone,
            "Channel": "WhatsApp",
            "Decision": "Follow-up",
            "ProviderMessageSid": provider_response.get("sid", ""),
            "ProviderStatus": provider_response.get("status", ""),
            "LLMPrompt": prompt,
            "LLMOutput": message_text,
            "Timestamp": datetime.utcnow().isoformat()
        })


if __name__ == "__main__":
    main()
