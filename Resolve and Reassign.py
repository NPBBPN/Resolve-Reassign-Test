import requests
import json
import argparse

# Default settings
API_TOKEN = ""
USER_EMAIL = ""
USER_ID = ""
REASSIGN_USER_ID = ""  # New user to reassign high-urgency incidents


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

#NB: This is making use of getting ALL incidents assigned to the specified user
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
                print(f"getting incident: {incident['id']} - Urgency: {incident['urgency']}")
                incidents.append(incident)
            more = r["more"]
            offset += limit
        else:
            return False

    print(f"Found {len(incidents)} incident(s)")
    return incidents

#This I changed around slightly in order to specify this is resolving a single incident, and reassigning others - hence the chance from "resolve_incidents" to "resolve_incident" and clarifying the incident_id
def resolve_incident(incident_id):
    """Resolve a single incident."""
    url = f"https://api.pagerduty.com/incidents/{incident_id}"
    payload = json.dumps({"incident": {"type": "incident", "status": "resolved"}})
    r = make_request(url=url, method="PUT", data=payload)
    if r:
        print(f"Incident {incident_id} resolved")
    else:
        print(f"Failed to resolve incident {incident_id}")


def reassign_incident(incident_id, user_id):
    """Reassign a high-urgency incident to a different user."""
    url = f"https://api.pagerduty.com/incidents/{incident_id}"
    payload = json.dumps({
        "incident": {
            "type": "incident",
            "assignments": [{"assignee": {"id": user_id, "type": "user_reference"}}]
        }
    })
    r = make_request(url=url, method="PUT", data=payload)
    if r:
        print(f"Incident {incident_id} reassigned to user {user_id}")
    else:
        print(f"Failed to reassign incident {incident_id}")


def handle_incidents_based_on_urgency():
    """Resolve low-urgency incidents and reassign high-urgency incidents."""
    incidents = get_incidents(USER_ID)
    if not incidents:
        print("No open incidents found.")
        return

    for incident in incidents:
        incident_id = incident["id"]
        urgency = incident["urgency"]

        if urgency == "low":
            resolve_incident(incident_id)
        elif urgency == "high":
            reassign_incident(incident_id, REASSIGN_USER_ID)


def get_arguments():
    """Get arguments from command line and update global variables."""
    global API_TOKEN, USER_ID, USER_EMAIL
    parser = argparse.ArgumentParser(description="Manage incidents based on urgency and resolve/reassign them accordingly")
    parser.add_argument("--token", "-t", default=API_TOKEN, help="API Token")
    parser.add_argument("--user", "-u", default=USER_ID, help="User ID")
    parser.add_argument("--email", "-e", default=USER_EMAIL, help="Resolving User Email")
    args = parser.parse_args()
    API_TOKEN = args.token
    USER_ID = args.user
    USER_EMAIL = args.email


def main():
    get_arguments()
    handle_incidents_based_on_urgency()


if __name__ == "__main__":
    main()
