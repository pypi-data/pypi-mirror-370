import requests


def get_user_groups(access_token):
    graph_url = "https://graph.microsoft.com/v1.0/me/memberOf"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    all_groups = []

    while graph_url:
        # Make the request to get the user's groups
        group_response = requests.get(graph_url, headers=headers)

        # Check if the response is successful
        if not group_response.ok:
            raise Exception(f"Error retrieving user groups: {group_response.status_code}-{group_response.text}")

        # Parse the response JSON
        group_data = group_response.json()

        # accumulate group_data["value"] from each page in the loop and the dedupe before returning
        all_groups.extend(group_data["value"])
        # Check for more pages of results
        graph_url = group_data.get("@odata.nextLink")

    return list(dict.fromkeys([group["displayName"] for group in all_groups if group.get("displayName") is not None]))
