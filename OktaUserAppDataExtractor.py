# Import necessary libraries
import requests
import csv
import os
import time

# Function to get all users from Okta
def get_all_users(domain, okta_api_token):
    headers = {
        'Authorization': f'SSWS {okta_api_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    okta_url = f'https://{domain}.okta.com'
    url = f'{okta_url}/api/v1/users'
    all_users = []
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        users = response.json()
        all_users += users
        links = response.links
        url = links.get('next', {}).get('url')
    return all_users

# Function to get applications linked to a user in Okta
def get_user_apps(domain, okta_api_token, user_id, app_links):
    if user_id in app_links:
        return app_links[user_id]
    headers = {
        'Authorization': f'SSWS {okta_api_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    okta_url = f'https://{domain}.okta.com'
    url = f'{okta_url}/api/v1/users/{user_id}/appLinks?expand=app'
    app_names = []
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        app_links_data = response.json()
        for app_link in app_links_data:
            app = app_link['app']
            if app['status'] == 'ACTIVE':
                app_names.append(app['label'])
        links = response.links
        url = links.get('next', {}).get('url')
    app_links[user_id] = ', '.join(app_names)
    return app_links[user_id]

# Function to extract user data including linked applications
def extract_user_data(domain, okta_api_token, users, app_links):
    user_data = []
    for user in users:
        user_id = user.get('id', 'N/A')
        user_name = user.get('profile', {}).get('login', 'N/A')
        email = user.get('profile', {}).get('email', 'N/A')
        first_name = user.get('profile', {}).get('firstName', 'N/A')
        last_name = user.get('profile', {}).get('lastName', 'N/A')
        full_name = f"{first_name} {last_name}"
        apps = get_user_apps(domain, okta_api_token, user_id, app_links)
        user_data.append({'id': user_id, 'username': user_name, 'email': email, 'full_name': full_name, 'apps': apps})
    return user_data

# Function to extract data about application usage by users
def extract_app_user_data(domain, okta_api_token):
    headers = {
        'Authorization': f'SSWS {okta_api_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    url = f'https://{domain}.okta.com/api/v1/users?limit=200'
    all_users = []
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        users_data = response.json()
        all_users += users_data
        links = response.links
        url = links.get('next', {}).get('url')
    user_ids = [user['id'] for user in all_users]
    app_links_data = []
    batch_size = 50
    for i in range(0, len(user_ids), batch_size):
        batch_ids = user_ids[i:i+batch_size]
        app_links_url = f'https://{domain}.okta.com/api/v1/apps/links?expand=appUser&userIds={",".join(batch_ids)}'
        response = requests.get(app_links_url, headers=headers)
        response.raise_for_status()
        app_links_data += response.json()
    app_user_map = {}
    for app_link in app_links_data:
        app_name = app_link['app']['name']
        user_name = app_link['appUser']['profile']['login']
        if app_name not in app_user_map:
            app_user_map[app_name] = []
        app_user_map[app_name].append(user_name)
    app_user_data = []
    for app_name, user_names in app_user_map.items():
        user_names.sort()
        app_user_data.append((app_name, ", ".join(user_names)))
    return app_user_data

# Main execution
if __name__ == "__main__":
    # Read domain and okta_api_token from environment variables
    domain = os.environ['OKTA_DOMAIN']
    okta_api_token = os.environ['OKTA_API_TOKEN']
    start_time = time.time()
    users = get_all_users(domain, okta_api_token)
    app_user_data = extract_app_user_data(domain, okta_api_token)
    app_links = {}
    extracted_users = extract_user_data(domain, okta_api_token, users, app_links)
    with open('new_app_user_data.csv', 'w', newline='') as csvfile:
        fieldnames = ['app', 'users']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for app, users in app_user_data.items():
            writer.writerow({'app': app, 'users': ', '.join(users)})
    with open('new_user_data.csv', 'w', newline='') as csvfile:
        fieldnames = ['id', 'username', 'email', 'full_name', 'apps']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for user in extracted_users:
            writer.writerow(user)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds.")
