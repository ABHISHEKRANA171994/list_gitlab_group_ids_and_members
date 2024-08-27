import requests
import concurrent.futures
import csv
import os

# Fetch GitLab Personal Access Token from environment variables
GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')

# Base URL for GitLab API
GITLAB_API_URL = 'https://gitlab.com/api/v4'

# Function to get all groups in the organization
def get_groups():
    groups = []
    page = 1
    per_page = 100

    while True:
        url = f'{GITLAB_API_URL}/groups?per_page={per_page}&page={page}'
        headers = {'PRIVATE-TOKEN': GITLAB_TOKEN}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get groups: {response.status_code}, {response.text}")

        group_data = response.json()
        if not group_data:
            break

        groups.extend(group_data)
        page += 1

    return groups

# Function to get all members of a group
def get_group_members(group_id):
    members = []
    page = 1
    per_page = 100

    while True:
        url = f'{GITLAB_API_URL}/groups/{group_id}/members?per_page={per_page}&page={page}'
        headers = {'PRIVATE-TOKEN': GITLAB_TOKEN}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get members for group {group_id}: {response.status_code}, {response.text}")

        member_data = response.json()
        if not member_data:
            break

        members.extend(member_data)
        page += 1

    return members

# Wrapper function to process each group
def process_group(group):
    group_id = group['id']
    group_name = group['name']
    members = get_group_members(group_id)
    
    results = []
    for member in members:
        results.append({
            'Group ID': group_id,
            'Group Name': group_name,
            'Member ID': member['id'],
            'Username': member['username'],
            'Name': member['name']
        })

    return results

# Main script
def main():
    # Get all groups in the organization
    groups = get_groups()

    # File to save the results
    output_file = 'list_gitlab_group_ids_and_members.csv'

    # Use ThreadPoolExecutor to process groups concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        all_results = list(executor.map(process_group, groups))

    # Flatten the list of results
    flattened_results = [item for sublist in all_results for item in sublist]

    # Save the results to a CSV file
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Group ID', 'Group Name', 'Member ID', 'Username', 'Name'])
        writer.writeheader()
        writer.writerows(flattened_results)

    print(f"Data has been saved to {output_file}")

if __name__ == '__main__':
    main()
