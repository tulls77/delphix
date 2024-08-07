###################################################################################################################
# Delphix Corp (2024)
# Author    : Aaron Tully
# Date      : July 2024
# Script    : list_RS_create_maskingJob_multi_optionv2.py
# Version 1 : Base script to list rulesets and create masking jobs for the selected RuleSet
# Version 2 : Sort the menu options and add multiple job selection
# Version 3 : Add the ability to list anr run masking jobs with status
# Interactive Menu: Presents an interactive menu with three options.
# 1. List Existing Rulesets: Retrieves and displays a list of existing rulesets with their IDs and names.
# 2. Create Masking Job: Prompts the user for a ruleset ID to create a new masking job with the same name as the RuleSet.
# 3. Exit: Exits the script.
##################################################################################################################

import requests
import json
from datetime import datetime

# Define the API URLs and headers
login_url = 'http://uvo1h6cwkmhoeckc9am.vm.cld.sr/masking/api/v5.1.33/login'
rulesets_url = 'http://uvo1h6cwkmhoeckc9am.vm.cld.sr/masking/api/v5.1.33/database-rulesets?page_number=1'
create_masking_job_url = 'http://uvo1h6cwkmhoeckc9am.vm.cld.sr/masking/api/v5.1.33/masking-jobs'
masking_jobs_url = 'http://uvo1h6cwkmhoeckc9am.vm.cld.sr/masking/api/v5.1.33/masking-jobs?page_number=1'
run_masking_job_url = 'http://uvo1h6cwkmhoeckc9am.vm.cld.sr/masking/api/v5.1.35/executions'
execution_status_url = 'http://uvo1h6cwkmhoeckc9am.vm.cld.sr/masking/api/v5.1.35/executions/'
job_details_url = 'http://uvo1h6cwkmhoeckc9am.vm.cld.sr/masking/api/v5.1.35/masking-jobs/'

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

login_data = {
    'username': 'admin',
    'password': 'Delphix_123!'
}

def login():
    response = requests.post(login_url, headers=headers, json=login_data)
    if response.status_code == 200:
        return response.json().get('Authorization')
    else:
        print("Login failed. Please check your credentials and API endpoint.")
        return None

def fetch_rulesets(auth_token):
    response = requests.get(rulesets_url, headers={'Authorization': auth_token})
    if response.status_code == 200:
        return response.json().get('responseList', [])
    else:
        print("Failed to retrieve rulesets.")
        return []

def list_masking_jobs(auth_token):
    response = requests.get(masking_jobs_url, headers={'Authorization': auth_token})
    if response.status_code == 200:
        return response.json().get('responseList', [])
    else:
        print("Failed to retrieve masking jobs.")
        return []

def create_masking_job(auth_token, ruleset_id, ruleset_name):
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

def run_masking_job(auth_token, job_id):
    job_data = {
        "jobId": job_id
    }
    response = requests.post(run_masking_job_url, headers={'Authorization': auth_token, 'Content-Type': 'application/json'}, json=job_data)
    if response.status_code == 200:
        execution_id = response.json().get('executionId')
        return execution_id
    else:
        print(f"Failed to execute masking job {job_id}.")
        return None

def fetch_job_details(auth_token, job_id):
    response = requests.get(f"{job_details_url}{job_id}", headers={'Authorization': auth_token})
    if response.status_code == 200:
        job_details = response.json()
        return {
            "jobId": job_id,
            "jobName": job_details.get('jobName', 'Unknown')
        }
    else:
        print(f"Failed to retrieve details for Job ID {job_id}.")
        return {
            "jobId": job_id,
            "jobName": 'Unknown'
        }

def format_datetime(dt_str):
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return 'Unknown'

def check_execution_status(auth_token, execution_id):
    response = requests.get(f"{execution_status_url}{execution_id}", headers={'Authorization': auth_token})
    if response.status_code == 200:
        execution_details = response.json()
        job_id = execution_details.get('jobId')
        job_details = fetch_job_details(auth_token, job_id)
        return {
            "executionId": execution_id,
            "jobId": job_details["jobId"],
            "jobName": job_details["jobName"],
            "status": execution_details.get('status', 'Unknown'),
            "rowsMasked": execution_details.get('rowsMasked', 'Unknown'),
            "startTime": format_datetime(execution_details.get('startTime', 'Unknown')),
            "endTime": format_datetime(execution_details.get('endTime', 'Unknown'))
        }
    else:
        print(f"Failed to retrieve status for Execution ID {execution_id}. Response Code: {response.status_code}")
        return None

def check_multiple_execution_statuses(auth_token, execution_ids):
    statuses = [check_execution_status(auth_token, execution_id) for execution_id in execution_ids]
    
    # Print header
    print("\nJob Execution Status:")
    print(f"{'Execution ID':<15}{'Job ID':<10}{'Job Name':<20}{'Status':<10}{'Rows Masked':<12}{'Start Time':<20}{'End Time':<20}")
    print("="*120)
    
    # Print details
    for status in statuses:
        if status:
            print(f"{status['executionId']:<15}{status['jobId']:<10}{status['jobName']:<20}{status['status']:<10}{status['rowsMasked']:<12}{status['startTime']:<20}{status['endTime']:<20}")

def parse_ruleset_ids(input_str):
    ruleset_ids = []
    for part in input_str.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            ruleset_ids.extend(range(start, end + 1))
        else:
            ruleset_ids.append(int(part.strip()))
    return ruleset_ids

def parse_job_ids(input_str):
    job_ids = []
    for part in input_str.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            job_ids.extend(range(start, end + 1))
        else:
            job_ids.append(int(part.strip()))
    return job_ids

def main():
    auth_token = login()
    if not auth_token:
        return

    while True:
        print("\nSelect an option:")
        print("1. List existing rulesets")
        print("2. Create masking jobs based on RulesetID")
        print("3. List existing masking jobs")
        print("4. Run masking job(s)")
        print("5. Check status of masking job(s)")
        print("6. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            rulesets = fetch_rulesets(auth_token)
            print("Existing Rulesets:")
            print(f"{'Database Ruleset ID':<20}{'Ruleset Name':<30}")
            print("="*50)
            for ruleset in rulesets:
                print(f"{ruleset['databaseRulesetId']:<20}{ruleset['rulesetName']:<30}")
        elif choice == '2':
            rulesets = fetch_rulesets(auth_token)  # Fetch rulesets but don't print
            ruleset_ids_input = input("\nEnter the rulesetIds to create masking jobs (comma-separated for multiple, hyphen for range): ")
            ruleset_ids = parse_ruleset_ids(ruleset_ids_input)
            for ruleset_id in ruleset_ids:
                selected_ruleset = next((r for r in rulesets if r['databaseRulesetId'] == ruleset_id), None)
                if selected_ruleset:
                    create_masking_job(auth_token, ruleset_id, selected_ruleset['rulesetName'])
                else:
                    print(f"Rule set ID {ruleset_id} does not exist. Failed to create masking job.")
        elif choice == '3':
            jobs = list_masking_jobs(auth_token)
            print("Existing Masking Jobs:")
            print(f"{'Masking Job ID':<20}{'Job Name':<30}")
            print("="*50)
            for job in jobs:
                print(f"{job['maskingJobId']:<20}{job['jobName']:<30}")
        elif choice == '4':
            job_ids_input = input("\nEnter the jobIds to run (comma-separated for multiple, hyphen for range): ")
            job_ids = parse_job_ids(job_ids_input)
            for job_id in job_ids:
                execution_id = run_masking_job(auth_token, job_id)
                if execution_id:
                    print(f"Masking job {job_id} executed successfully! Execution ID: {execution_id}")
        elif choice == '5':
            execution_ids_input = input("\nEnter the executionIds to check status (comma-separated for multiple, hyphen for range): ")
            execution_ids = parse_job_ids(execution_ids_input)  # Reusing parse_job_ids for simplicity
            check_multiple_execution_statuses(auth_token, execution_ids)
        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
