###################################################################################################################
# Delphix Corp (2024)
# Author    : Aaron Tully
# Date      : July 2024
# Script    : list_RS_create_maskingJob_multi_optionv2.py
# Version 1 : Base script to list rulesets and create masking jobs for the selected RuleSet
# Version 2 : Sort the menu options and add multiple job selection
# Version 3 : Add the ability to list and run masking jobs with status
# Interactive Menu: Presents an interactive menu with three options.
# 1. List Existing Rulesets: Retrieves and displays a list of existing rulesets with their IDs and names.
# 2. List existing connectors
# 3. List existing masking jobs by name and Job ID
# 4. Create Masking Job: Prompts the user for a ruleset ID to create a new masking job with the same name as the RuleSet.
# 5. Create a masking job
# 6. Run a masking job
# 7. Check job execution status 
# 8. Exit: Exits the script
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
connectors_url = 'http://uvo1h6cwkmhoeckc9am.vm.cld.sr/masking/api/v5.1.35/database-connectors?page_number=1'
database_ruleset_url = 'http://uvo1h6cwkmhoeckc9am.vm.cld.sr/masking/api/v5.1.35/database-rulesets'

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
        print(f"Status Code: {response.status_code}, Response: {response.text}")
        return None

def fetch_rulesets(auth_token):
    response = requests.get(rulesets_url, headers={'Authorization': auth_token})
    if response.status_code == 200:
        return response.json().get('responseList', [])
    else:
        print("Failed to retrieve rulesets.")
        print(f"Status Code: {response.status_code}, Response: {response.text}")
        return []

def list_masking_jobs(auth_token):
    response = requests.get(masking_jobs_url, headers={'Authorization': auth_token})
    if response.status_code == 200:
        return response.json().get('responseList', [])
    else:
        print("Failed to retrieve masking jobs.")
        print(f"Status Code: {response.status_code}, Response: {response.text}")
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
        print("maskingJobId:", job_response.get('maskingJobId', 'Unknown'))
        print("jobName:", job_response.get('jobName', 'Unknown'))
        print("rulesetId:", job_response.get('rulesetId', 'Unknown'))
        print("Masking job created successfully!")
    else:
        print("Failed to create masking job.")
        print(f"Status Code: {response.status_code}, Response: {response.text}")

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
        print(f"Status Code: {response.status_code}, Response: {response.text}")
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
        print(f"Status Code: {response.status_code}, Response: {response.text}")
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
        print(f"Response: {response.text}")
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

def parse_job_ids(input_str):
    job_ids = []
    for part in input_str.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            job_ids.extend(range(start, end + 1))
        else:
            job_ids.append(int(part.strip()))
    return job_ids

def fetch_connectors(auth_token):
    response = requests.get(connectors_url, headers={'Authorization': auth_token})
    if response.status_code == 200:
        return response.json().get('responseList', [])
    else:
        print("Failed to retrieve connectors.")
        print(f"Status Code: {response.status_code}, Response: {response.text}")
        return []

def create_database_ruleset(auth_token, connector_id, ruleset_name):
    ruleset_data = {
        "rulesetName": ruleset_name,
        "databaseConnectorId": connector_id
    }
    response = requests.post(database_ruleset_url, headers={'Authorization': auth_token, 'Content-Type': 'application/json'}, json=ruleset_data)
    if response.status_code == 200:
        ruleset_response = response.json()
        print("\nDatabase Ruleset Details:")
        if 'databaseRulesetId' in ruleset_response and 'rulesetName' in ruleset_response and 'databaseConnectorId' in ruleset_response:
            print("databaseRulesetId:", ruleset_response['databaseRulesetId'])
            print("rulesetName:", ruleset_response['rulesetName'])
            print("databaseConnectorId:", ruleset_response['databaseConnectorId'])
        else:
            print("Database ruleset created but missing expected keys.")
            print("Debug Info: Response JSON:", ruleset_response)
    else:
        print("Failed to create database ruleset.")
        print(f"Status Code: {response.status_code}, Response: {response.text}")

def main():
    auth_token = login()
    if not auth_token:
        return
    
    while True:
        print("\nInteractive Masking Menu")
        print("1. List existing rulesets")
        print("2. List existing connectors")
        print("3. List existing masking jobs")
        print("4. Create a new database ruleset")
        print("5. Create a masking job")
        print("6. Run a masking job")
        print("7. Check job execution status")
        print("8. Exit")
        
        choice = input("Enter your choice: ")

        if choice == '1':
            rulesets = fetch_rulesets(auth_token)
            print("\nExisting Rulesets:")
            print(f"{'Ruleset ID':<15}{'Ruleset Name':<30}")
            print("="*45)
            for ruleset in rulesets:
                ruleset_id = ruleset.get('databaseRulesetId', 'Unknown')
                ruleset_name = ruleset.get('rulesetName', 'Unknown')
                print(f"{ruleset_id:<15}{ruleset_name:<30}")

        elif choice == '2':
            connectors = fetch_connectors(auth_token)
            print("\nExisting Connectors:")
            print(f"{'Connector ID':<15}{'Connector Name':<30}")
            print("="*45)
            for connector in connectors:
                connector_id = connector.get('databaseConnectorId', 'Unknown')
                connector_name = connector.get('connectorName', 'Unknown')
                print(f"{connector_id:<15}{connector_name:<30}")

        elif choice == '3':
            masking_jobs = list_masking_jobs(auth_token)
            print("\nExisting Masking Jobs:")
            print(f"{'Job ID':<10}{'Job Name':<30}")
            print("="*40)
            for job in masking_jobs:
                job_id = job.get('maskingJobId', 'Unknown')
                job_name = job.get('jobName', 'Unknown')
                print(f"{job_id:<10}{job_name:<30}")

        elif choice == '4':
            try:
                connector_id = int(input("Enter the connector ID for the new ruleset: "))
                ruleset_name = input("Enter the name for the new ruleset: ")
                create_database_ruleset(auth_token, connector_id, ruleset_name)
            except ValueError:
                print("Invalid input. Please enter a numeric connector ID.")

        elif choice == '5':
            try:
                ruleset_id = int(input("Enter the ruleset ID: "))
                ruleset_name = input("Enter the name for the masking job: ")
                create_masking_job(auth_token, ruleset_id, ruleset_name)
            except ValueError:
                print("Invalid input. Please enter a numeric ruleset ID.")

        elif choice == '6':
            try:
                job_id = int(input("Enter the job ID: "))
                execution_id = run_masking_job(auth_token, job_id)
                if execution_id:
                    print(f"Masking job {job_id} started with execution ID {execution_id}.")
                else:
                    print(f"Failed to start masking job {job_id}.")
            except ValueError:
                print("Invalid input. Please enter a numeric job ID.")

        elif choice == '7':
            execution_ids_str = input("Enter execution IDs (comma-separated or range, e.g., 1-3): ")
            execution_ids = parse_job_ids(execution_ids_str)
            check_multiple_execution_statuses(auth_token, execution_ids)

        elif choice == '8':
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
