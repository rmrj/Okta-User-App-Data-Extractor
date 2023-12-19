# Okta-User-App-Data-Extractor
# Okta User and Application Data Extraction Tool

## Overview
This tool is designed to interact with the Okta API to retrieve and organize user and application data. It can be used to extract comprehensive details about users and the applications they have access to.

## Features
- Retrieve all users from an Okta domain.
- Extract applications linked to each user.
- Compile and save user and application data into CSV files.

## Requirements
- Python 3.x
- `requests` library

## Setup
1. Install required Python libraries:
   ```bash
   pip install requests
## Set your Okta domain and API token as environment variables:
export OKTA_DOMAIN='your_okta_domain'
export OKTA_API_TOKEN='your_api_token'
