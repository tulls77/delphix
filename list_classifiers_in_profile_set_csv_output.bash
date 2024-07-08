#!/bin/bash

#
##################################################################################################################
# Delphix Corp (2024)
# Author    : Aaron Tully
# Date      : 2014.22.04
# Script    : list_classifiers_in_profile_set_csv_output.sh
# Version   : v1
##################################################################################################################

# Define the API URLs
login_url='http://uvo1gukczfceqn0kxdm.vm.cld.sr/masking/api/v5.1.33/login'
profile_sets_url='http://uvo1gukczfceqn0kxdm.vm.cld.sr/masking/api/v5.1.33/profile-sets'
classifiers_url='http://uvo1gukczfceqn0kxdm.vm.cld.sr/masking/api/v5.1.33/classifiers'

# Define the request headers
headers=(
  '-H' 'accept: application/json'
  '-H' 'Content-Type: application/json'
)

# Define the request body for the login
request_body='{
  "username": "admin",
  "password": "Delphix_123!"
}'

# Send a POST request to the login URL with the headers and request body
login_response=$(curl -s -X POST "$login_url" "${headers[@]}" -d "$request_body")

# Extract the authorization token from the login response using jq
auth_token=$(echo "$login_response" | jq -r '.Authorization')

# Check if the authorization token is valid
if [ "$auth_token" != "null" ] && [ -n "$auth_token" ]; then
    echo "Authorization Token: $auth_token"

    # Use the authorization token to send a GET request to the profile sets API
    profile_sets_response=$(curl -s -X GET "$profile_sets_url" -H "accept: application/json" -H "Authorization: $auth_token")

    # Extract classifier IDs from the profile set
    # Add the profile set name in the quotes profileSetName == ""
    classifier_ids=$(echo "$profile_sets_response" | jq -r '.responseList[] | select(.profileSetName == "CMC_Profile_set_v1") | .classifierIds')

    # If classifier IDs were found
    if [ -n "$classifier_ids" ]; then
        # Fetch the classifiers using the authorization token
        classifiers_response=$(curl -s -X GET "$classifiers_url" -H "accept: application/json" -H "Authorization: $auth_token")

        # Print headers for the output
        echo "ClassifierId,ClassifierName,profileSetName"

        # Use jq to filter classifiers based on the classifier IDs from the profile set
        # Add the profile set name to the end of the below line 
        echo "$classifiers_response" | sed 's/\\//g' | jq -r --argjson ids "$classifier_ids" '.responseList[] | select(.classifierId as $id | $ids[] == $id) | "\(.classifierId),\(.classifierName),CMC_Profile_set_v1"'
    else
        echo "Error: No classifiers found in the 'ASDD Standard' profile set"
    fi
else
    echo "Error: Authorization token not found in the response"
fi
