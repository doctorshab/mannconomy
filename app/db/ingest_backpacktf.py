import requests
import json

# TODO: Replace with your actual Backpack.tf API key
API_KEY = "YOUR_API_KEY_HERE"

def fetch_backpacktf_data():
    print("Initiating connection to Backpack.tf API...")
    
    # We will hit the IGetPrices endpoint to see how they structure item pricing
    url = "https://backpack.tf/api/IGetPrices/v4"
    
    params = {
        "key": API_KEY,
        "compress": 1  # Standard API parameter to reduce payload size
    }
    
    try:
        # Send the GET request to the API
        response = requests.get(url, params=params)
        
        # Check if the connection was successful (HTTP 200)
        if response.status_code == 200:
            print("Success! Data retrieved.\n")
            data = response.json()
            
            # The full JSON is massive, so we will just print a formatted snippet
            # to verify the shape of the data we are getting.
            print("--- RAW JSON RESPONSE SNIPPET ---")
            formatted_json = json.dumps(data, indent=2)
            
            # Slicing the first 1500 characters so we don't flood your terminal
            print(formatted_json[:1500] + "\n\n... [TRUNCATED]")
            
            print("\n--- TEST COMPLETE ---")
            print("If you see the JSON above, you have successfully pulled live market data!")
            
        elif response.status_code == 401:
            print("Error 401: Unauthorized. Your API key might be missing or invalid.")
        else:
            print(f"Error {response.status_code}: Could not fetch data.")
            print(response.text)
            
    except Exception as e:
        print(f"A critical error occurred: {e}")

if __name__ == "__main__":
    if API_KEY == "YOUR_API_KEY_HERE":
        print("WARNING: You need to insert your Backpack.tf API key into the script first!")
    else:
        fetch_backpacktf_data()