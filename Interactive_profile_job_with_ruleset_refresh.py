import requests
import json
import time

# Define the API URLs
login_url = 'http://<ENGINE_NAME>/masking/api/v5.1.33/login'
profile_jobs_url = 'http://<ENGINE_NAME>/masking/api/v5.1.33/profile-jobs?page_number=1'
execute_job_url = 'http://<ENGINE_NAME>/masking/api/v5.1.33/executions'
async_tasks_url = 'http://<ENGINE_NAME>/masking/api/v5.1.33/async-tasks/'

# Define the request headers
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

# Define the request body for the login with hardcoded credentials
login_data = {
    'username': 'USERNAME',
    'password': 'PASSWORD'
}

# Send a POST request to the login URL
login_response = requests.post(login_url, headers=headers, json=login_data)

# Extract the authorization token from the login response
auth_token = login_response.json().get('Authorization')

# Check if the authorization token is valid
if auth_token:
    print("Login successful!")
    print("Authorization Token:", auth_token)

    # Send a GET request to the profile jobs API
    profile_jobs_response = requests.get(profile_jobs_url, headers={'Authorization': auth_token}).json()

    # Check if the profile jobs response is valid
    if profile_jobs_response:
        print("Profile Jobs (profileJobId, jobName):")
        for job in profile_jobs_response['responseList']:
            print(job['profileJobId'], job['jobName'])

        # Add a line break after profile job selection
        print()

        # Add a note about the RuleSet refresh
        print("NOTE: A RuleSet refresh will run for the associated profile job before the profile job is triggered.")

        # Prompt the user to select a job by profileJobId
        selected_job_id = input("Enter the profileJobId to trigger: ")

        # Check if the selected job ID is valid
        selected_job = next((job for job in profile_jobs_response['responseList'] if job['profileJobId'] == int(selected_job_id)), None)
        if selected_job:
            # Extract the rulesetId from the selected job
            ruleset_id = selected_job['rulesetId']

            # Trigger ruleset refresh
            refresh_response = requests.put(f"http://uvo1gukczfceqn0kxdm.vm.cld.sr/masking/api/v5.1.33/database-rulesets/{ruleset_id}/refresh", headers={'Authorization': auth_token}, json={})

            # Monitor the ruleset refresh status
            async_task_id = refresh_response.json().get('asyncTaskId')
            while True:
                task_response = requests.get(f"{async_tasks_url}{async_task_id}", headers={'Authorization': auth_token}).json()
                task_status = task_response.get('status')
                start_time = task_response.get('startTime')
                print(f"Ruleset refresh status: {task_status}, startTime: {start_time}")
                if task_status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                    end_time = task_response.get('endTime')
                    print(f"Final ruleset refresh status: {task_status}, endTime: {end_time}")
                    break
                time.sleep(10)  # Wait for 10 seconds before checking the status again

            # Add a line break after ruleset refresh
            print()

            # Trigger the selected job
            print(f"Triggering job with profileJobId: {selected_job_id}")
            execute_response = requests.post(execute_job_url, headers={'Authorization': auth_token, 'Content-Type': 'application/json'}, json={'jobId': int(selected_job_id)})

            # Extract the executionId and print the required fields
            execution_info = execute_response.json()
            print("Job execution response:")
            print("executionId:", execution_info['executionId'])
            print("status:", execution_info['status'])
            print("startTime:", execution_info['startTime'])

            # Add a line break after the start time of the profile job trigger
            print()

            # Monitor the job status
            execution_id = execution_info['executionId']
            while True:
                monitor_response = requests.get(f"http://uvo1gukczfceqn0kxdm.vm.cld.sr/masking/api/v5.1.33/executions/{execution_id}", headers={'Authorization': auth_token}).json()
                job_status = monitor_response['status']
                print("Current job status:", job_status)
                if job_status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                    print("Final job status:", job_status)
                    break
                time.sleep(10)  # Wait for 10 seconds before checking the status again
        else:
            print(f"Error: No job found with the profileJobId '{selected_job_id}'")
    else:
        print("Failed to retrieve profile jobs. Please check the API endpoint and authorization token.")
else:
    print("Failed to obtain authorization token. Please check your credentials.")
