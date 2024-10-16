import requests
import os
import csv
import random
import json
import vertexai
from vertexai.generative_models import GenerationConfig, GenerativeModel
import pandas as pd


model = 'openai/gpt-3.5-turbo-instruct'
# https://docs.edenai.co/reference/text_generation_create


def prompt_eden_ai(input):
    url = "https://api.edenai.run/v2/text/generation"

    token = ""
    payload = {
        "response_as_dict": True,
        "attributes_as_list": False,
        "show_base_64": True,
        "show_original_response": False,
        "temperature": 0,
        "max_tokens": 100,
        "providers": [model],
        "text": input
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f'Bearer {token}'
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.json()


def prompt_vertexai(input):
    vertexai.init(
        project="second-kite-438812-h1",
        location="asia-southeast1"
    )

    response_schema = {
        "type": "OBJECT",
        "properties": {
            "PII": {"type": "BOOLEAN"},
            "Health": {"type": "BOOLEAN"},
            "Credentials": {"type": "BOOLEAN"},
            "Private Communications": {"type": "BOOLEAN"},
            "Location": {"type": "BOOLEAN"},
            "Media": {"type": "BOOLEAN"},
            "Financial": {"type": "BOOLEAN"},
            "Customer": {"type": "BOOLEAN"},
            "Strategic": {"type": "BOOLEAN"},
            "Trade Secrets": {"type": "BOOLEAN"},
            "Intellectual Property": {"type": "BOOLEAN"},
            "Internal Documents": {"type": "BOOLEAN"},
            "System Configurations": {"type": "BOOLEAN"},
            "Source Code": {"type": "BOOLEAN"},
        },
        "required": [
            "Source Code",
            "System Configurations",
            "Internal Documents",
            "Intellectual Property",
            "Trade Secrets",
            "Strategic",
            "Customer",
            "Financial",
            "Media",
            "Location",
            "Private Communications",
            "Credentials",
            "Health",
            "PII",
        ],
    }

    model = GenerativeModel("gemini-1.5-pro-002")

    response = model.generate_content(
        input,
        generation_config=GenerationConfig(
            response_mime_type="application/json",
            response_schema=response_schema
        ),
    )

    return json.loads(response.text)


data = './outputs/'
no_list = os.listdir(data)
print(f'found files:{len(no_list)} with {no_list}')

outfile = open(os.path.join(data, 'lockbit3_datatypes.csv'), 'w')
writer = csv.writer(outfile)
writer.writerow(['ransom_group_no', 'categories'])

id_map = pd.read_csv(os.path.join(data, 'lockbit3.csv'))
ctr = 0
for n in no_list:
    file = os.path.join(data, str(n), 'filetree.txt')
    print(f'========================== processing {ctr}')
    while True:
        try:
            with open(file, 'rb') as f:
                lines = f.readlines()
                sample_lines = []
                if len(lines) < 100:
                    sample_lines = lines
                else:
                    sample_lines = random.sample(lines, 100)
                count = len(sample_lines)

                print(f'file {file} has {count}')

                prompt = f'''
                You are a cybersecurity analyst, tasked with categorizing files
                based on their potential risk in a ransomware attack.
                Your goal is to identify which types of sensitive data might have
                been compromised.

                For each filename provided, analyze its name and categorize it into
                the following categories.  A filename can belong to multiple
                categories.  Mark each applicable category as true. If a category
                doesn't apply, mark it as false.

                The categories are:
                PII (e.g., "passport_scan.pdf", "SSN_records.xlsx")
                Health (e.g., "patient_records.csv", "medical_history.docx")
                Credentials (e.g., "passwords.txt", "usernames_and_pins.csv")
                Private Communications (e.g., "emails_archive.pst", "private_messages.zip")
                Location (e.g., "gps_tracking.log", "travel_history.xlsx")
                Media (e.g., "family_photos.zip", "personal_videos.mov")
                Financial (e.g., "company_financials.xlsx", "revenue_projections.csv")
                Customer (e.g., "customer_database.sql", "client_list.csv")
                Strategic (e.g., "marketing_strategy.docx", "product_roadmap.pdf")
                Trade Secrets (e.g., "secret_formula.txt", "manufacturing_process.docx")
                Intellectual Property (e.g., "patent_application.pdf", "copyright_certificates.zip")
                Internal Documents (e.g., "contracts.zip", "legal_documents.docx")
                System Configurations (e.g., "network_diagram.png", "server_passwords.txt")
                Source Code (e.g., "website_code.zip", "app_source.tar.gz")

                Below are the filenames to interpret:
                {str(sample_lines)}
                '''
                result = prompt_vertexai(prompt)

                for k in result:
                    if result[k]:
                        writer.writerow(
                            [
                                id_map.iloc[int(n)]['post_title'],
                                k
                            ]
                        )
                        outfile.flush()

        except FileNotFoundError as e:
            print(f'skipping file {file} as not found')
            print(e)
            break
        except Exception as e:
            print(f'skipping file {file} from error')
            if '429' in str(e):
                import time
                print("sleeping for 60")
                time.sleep(60)
                continue

        break

    ctr += 1
