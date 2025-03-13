import requests
import json
import argparse

# Default settings
API_TOKEN = ""
USER_EMAIL = ""
USER_ID = ""


def make_request(url,method,data=None):
    """Helper function to make GET and PUT requests to the PagerDuty API."""
    
    headers = {
    "Accept": "application/vnd.pagerduty+json;version=2",
    "Authorization": f"Token token={API_TOKEN}",
    "Content-Type": "application/json",
    "From": USER_EMAIL}
 
    if method == "GET":
        response = requests.get(url=url, headers=headers)
    elif method == "PUT":
        response = requests.put(url=url, headers=headers, data=data)
    if response.status_code > 299:
        print(f"Error: {response.status_code} - {response.reason}")
        return False
    return response.json()


def get_incidents(user):
    """Get all incidents assigned to user in the triggered or acknowledged state."""
    more = True
    incidents = []
    offset = 0
    limit = 100
    while more is True:
        url = f"https://api.pagerduty.com/incidents?user_ids[]={user}&limit={limit}&offset={offset}"
        r = make_request(url=url,method="GET")
        if r:
            for incident in r["incidents"]:
                print(f"getting incident: {incident['id']}")
                incidents.append(incident)
            more = r["more"]
            offset += limit
        else:
            return False
    print(f"Found {len(incidents)} incident(s)")
    return incidents


def resolve_incidents(incidents):
    """Resolve incidents one at a time."""
    print(f"Resolving {len(incidents)} incident(s)")
    for incident in incidents:
        url = f"https://api.pagerduty.com/incidents/{incident['id']}"
        payload = json.dumps({"incident": {"type": "incident",
                                           "status": "resolved"}})
        r = make_request(url=url,method="PUT",data=payload)
        if not r:
            return False
        print(f"Incident {incident['id']} resolved")
    return True


def get_arguments():
    """Get arguments from command line and update global variables."""
    global API_TOKEN, USER_ID, USER_EMAIL
    parser = argparse.ArgumentParser(description="Resolve all incidents assigned to a user")
    parser.add_argument("--token", "-t", default=API_TOKEN, help="API Token")
    parser.add_argument("--user", "-u", default=USER_ID, help="User ID")
    parser.add_argument("--email", "-e", default=USER_EMAIL, help="Resolving User Email")
    args = parser.parse_args()
    API_TOKEN = args.token
    USER_ID = args.user
    USER_EMAIL = args.email


def main():
    get_arguments()
    incidents = get_incidents(USER_ID)
    if incidents:
        resolve_incidents(incidents)


if __name__ == "__main__":
    main()