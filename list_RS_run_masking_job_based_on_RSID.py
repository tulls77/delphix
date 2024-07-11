###################################################################################################################
# Delphix Corp (2024)
# Author    : Aaron Tully
# Date      : July 2024
# Script    : list_RS_run_masking_job_based_onRSID.py
# Version   : v1
# Interactive Menu: Presents an interactive menu with three options.
# 1. Create Masking Job: Prompts the user for a ruleset ID to create a new masking job with the same name as the RuleSet.
# 2. List Existing Rulesets: Retrieves and displays a list of existing rulesets with their IDs and names.
# 3. Exit: Exits the script.

##################################################################################################################
import requests
import json

# Define the API URLs
# Replace <ENGINE_ENGINE_URL> with your actual values
login_url = 'http://<MASKING_ENGINE_URL>/masking/api/v5.1.33/login'
rulesets_url = 'http://<MASKING_ENGINE_URL>/masking/api/v5.1.33/database-rulesets?page_number=1'
create_masking_job_url = 'http://<MASKING_ENGINE_URL>/masking/api/v5.1.33/masking-jobs'
masking_jobs_url = 'http://<MASKING_ENGINE_URL>/masking/api/v5.1.33/masking-jobs?page_number=1'

# Define the request headers
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

# Define the request body for the login with hardcoded credentials
# Replace USERNAME, and PASSWORD with your actual values
login_data = {
    'username': 'USERNAME',
    'password': 'PASSWORD'
}

# Function to login and get the auth token
def login():
    response = requests.post(login_url, headers=headers, json=login_data)
    if response.status_code == 200:
        return response.json().get('Authorization')
    else:
        print("Login failed. Please check your credentials and API endpoint.")
        return None

# Function to fetch existing rulesets
def list_rulesets(auth_token):
    response = requests.get(rulesets_url, headers={'Authorization': auth_token})
    if response.status_code == 200:
        rulesets = response.json().get('responseList', [])
        print("Existing Rulesets (databaseRulesetId, rulesetName):")
        for ruleset in rulesets:
            print(ruleset['databaseRulesetId'], ruleset['rulesetName'])
        return rulesets
    else:
        print("Failed to retrieve rulesets.")
        return []

# Function to fetch existing masking jobs
def list_masking_jobs(auth_token):
    response = requests.get(masking_jobs_url, headers={'Authorization': auth_token})
    if response.status_code == 200:
        return response.json().get('responseList', [])
    else:
        print("Failed to retrieve masking jobs.")
        return []

# Function to create a masking job
def create_masking_job(auth_token, ruleset_id, ruleset_name):
    # Fetch existing masking jobs to check for duplicates
    existing_jobs = list_masking_jobs(auth_token)
    if any(job['jobName'] == ruleset_name for job in existing_jobs):
        print(f"Failed to create masking job. '{ruleset_name}' already exists")
        return

    job_data = {
        "jobName": ruleset_name,
        "rulesetId": ruleset_id,
        "jobDescription": "",
        "feedbackSize": 100000,
        "onTheFlyMasking": False,
        "databaseMaskingOptions": {
            "batchUpdate": True,
            "commitSize": 20000,
            "dropConstraints": True,
            "prescript": {
                "name": "",
                "contents": ""
            },
            "postscript": {
                "name": "",
                "contents": ""
            }
        }
    }
    response = requests.post(create_masking_job_url, headers={'Authorization': auth_token, 'Content-Type': 'application/json'}, json=job_data)
    if response.status_code == 200:
        job_response = response.json()
        print("\nMasking Job Details:")
        print("maskingJobId:", job_response['maskingJobId'])
        print("jobName:", job_response['jobName'])
        print("rulesetId:", job_response['rulesetId'])
        print("Masking job created successfully!")
    else:
        print("Failed to create masking job.")

# Main interactive menu
def main():
    auth_token = login()
    if not auth_token:
        return

    while True:
        print("\nOptions:")
        print("1. Create Masking Job")
        print("2. List Existing Rulesets")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            rulesets = list_rulesets(auth_token)
            ruleset_id = int(input("\nEnter the rulesetId to create a masking job: "))
            selected_ruleset = next((r for r in rulesets if r['databaseRulesetId'] == ruleset_id), None)
            if selected_ruleset:
                create_masking_job(auth_token, ruleset_id, selected_ruleset['rulesetName'])
            else:
                print("Rule set ID does not exist. Failed to create masking job.")
        elif choice == '2':
            list_rulesets(auth_token)
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
