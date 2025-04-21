import json
from openai import OpenAI
from core.config import settings
from services.extractor.prompt_doc import SEGMENT_RULE_PROMPT
from api.utils.json_parser import safe_json_parse  # or wherever you've placed it


client = OpenAI(api_key=settings.OPENAI_API_KEY)

def parse_segmentation_prompt(prompt: str) -> dict:
    full_prompt = SEGMENT_RULE_PROMPT + f"\n\nINPUT:\n{prompt}"

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a rule generator."},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.2
    )

    raw_json = response.choices[0].message.content
    try:
        
            rule_data = safe_json_parse(raw_json)
        
            if rule_data is None:
                raise ValueError("Failed to parse segmentation rule from LLM response.")
            else:
                return rule_data    

    except Exception as e:
            raise ValueError(f"Failed to parse rule JSON: {str(e)}")
    



