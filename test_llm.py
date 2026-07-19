import os
import json
from google import genai
from google.genai import types

# Import your Pydantic model
from app.schemas.valuation import ValuationResponse

# 1. Initialize the modern client
# Make sure your GEMINI_API_KEY environment variable is set!
client = genai.Client()

def test_valuation_call():
    print("🚀 Sending request to Gemini...")
    
    # 2. A mock prompt simulating what the Math layer will output
    mock_prompt = """
    You are a TF2 trading expert. Analyze the following data and generate a valuation narrative.
    
    Item: Burning Flames Team Captain (ID: 105)
    Calculated Value: 6500.0 ref
    Low Bound: 6000.0 ref
    High Bound: 7000.0 ref
    Discount Percentage (if user asked): N/A
    
    Comps found in database:
    - ID 801: Sold for 6600 ref on 2026-07-01
    - ID 802: Sold for 6400 ref on 2026-06-15
    - ID 803: Sold for 6500 ref on 2026-05-20
    
    Confidence: High (3 high-quality matches)
    """

    try:
        # 3. Call the API using the strict schema
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite', # Or gemini-3.5-flash if you are on the newest tier
            contents=mock_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ValuationResponse,
                temperature=0.1,
            ),
        )
        
        # 4. Parse the response text back into our Pydantic model
        valuation_obj = ValuationResponse.model_validate_json(response.text)
        
        print("\n✅ SUCCESS! The LLM followed the strict Pydantic schema.\n")
        
        # Print the resulting Python object as formatted JSON so you can inspect it
        print(json.dumps(valuation_obj.model_dump(), indent=2))
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    # Ensure the API key is present before running
    if not os.environ.get("GEMINI_API_KEY"):
        print("Error: Please set the GEMINI_API_KEY environment variable.")
    else:
        test_valuation_call()