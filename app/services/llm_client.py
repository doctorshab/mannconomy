import json
from google import genai
from google.genai import types
from pydantic import ValidationError

from app.schemas.valuation import ValuationResponse
from app.core.config import settings
client = genai.Client(api_key=settings.GEMINI_API_KEY)

def generate_valuation_narrative(prompt: str) -> ValuationResponse:
    """
    Sends the deterministically compiled prompt to the LLM and forces 
    a strictly formatted JSON response matching the ValuationResponse schema.
    """
    print("🚀 Sending valuation request to Gemini...")
    
    try:
        # 2. The API Call
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL_NAME,  
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ValuationResponse,
                temperature=0.1,  # Keep it low to prevent hallucination!
            ),
        )
        
        # 3. Pydantic Validation
        # The API returns a JSON string in response.text. We feed that directly 
        # into our Pydantic model to guarantee the types (floats, ints, strings) are correct.
        valuation_obj = ValuationResponse.model_validate_json(response.text)
        
        return valuation_obj
        
    except ValidationError as e:
        # If the LLM somehow breaks the schema (rare with structured output), catch it
        print(f"❌ Pydantic Schema Validation Error:\n{e}")
        raise RuntimeError("LLM returned malformed JSON that did not match the schema.")
        
    except Exception as e:
        # Catch standard API errors (503 Service Unavailable, Quota exceeded, etc.)
        print(f"❌ Gemini API Error:\n{e}")
        raise RuntimeError(f"Failed to communicate with LLM: {str(e)}")