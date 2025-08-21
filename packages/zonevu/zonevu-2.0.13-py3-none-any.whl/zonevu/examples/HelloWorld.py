"""
Hello World example for the ZoneVu SDK.

Demonstrates basic client initialization and a simple API call.
"""

from zonevu.Zonevu import Zonevu

def hello():
    print('ZoneVu says "Hello"')

    """
    Option 1 - Create a file in your users directory called zonevu_keyfile.json:
    It should contain the following text:
    {"apikey": "your-api-key"}
    Then use,
        zonevu = Zonevu.init_from_std_keyfile()
    to get an instance of the zonevu python web api client.
    """
    # Option 1
    # zonevu = Zonevu.init_from_std_keyfile()  # Creating a zonevu client will print out the zonevu notice.

    """
    Option 2 -- Embed your api key in your code
    """
    my_api_key = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # Replace with your actual API key generated in the ZoneVu GUI
    zonevu = Zonevu.init_from_apikey(my_api_key)  # Creating a zonevu client will print out the zonevu notice.

    project_entries = zonevu.project_service.get_projects()  # Get a list of projects in this zonevu account.
    print(f'There are {len(project_entries)} projects in your zonevu account')
    for entry in project_entries:
        print(f'  - {entry.name}')

    first_project_entry = project_entries[0]
    first_project = zonevu.project_service.find_project(first_project_entry.id)
    pass

if __name__ == "__main__":
    hello()