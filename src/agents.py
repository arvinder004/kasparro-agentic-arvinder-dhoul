import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
from src.models import AgentState, ProductData, UserQuestion, CompetitorProduct, PageOutput, PageSection
from src.content_engine import ContentLogicBlocks, TEMPLATES

load_dotenv()

genai.configure(api_key=os.environ['GEMINI_API_KEY'])

class BaseAgent:
    def __init__(self, name):
        self.name = name

    def call_llm(self, system_prompt, user_content, expect_json=False):
        generation_config = {
            "temperature": 0.7
        }

        if expect_json:
            generation_config["response_mime_type"] = "application/json"

        model = genai.GenerativeModel(
            model_name="gemini_1.5_flash",
            system_instruction=system_prompt,
            generation_config=generation_config
        )

        try:
            response = model.generate_content(user_content)
            return response.text
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            return "{}" if expect_json else "Error generating content"
        


class AnalystAgent(BaseAgent):
    def run(self, raw_data: dict) -> AgentState:
        print(f"[{self.name}] Ingesting and Enriching Data")

        product = ProductData(
            name=raw_data['Product Name'],
            concentration=raw_data.get("Concentration"),
            skin_type=[x.strip() for x in raw_data['Skin Type'].split(",")],
            ingredients=[x.strip() for x in raw_data['Key Ingredients'].split(",")],
            benefits=[x.strip() for x in raw_data['Benefits'].split(",")],
            how_to_use=raw_data['How to Use'],
            side_effects=raw_data['Side Effects'],
            price=raw_data['Price']
        )

        print(f"[{self.name}] Generating Questions")
        
        q_prompt = f"""
            Generate exactly 15 user questions for this product: {product.name}.
            Categories: Informational, Safety, Usage, Purchase, Comparison.
        
            Output Structure (JSON):
            {{ "questions": [ {{ "category": "...", "question_text": "..." }} ] }}
        """

        q_response = self.call_llm(
            system_prompt="You are a data generation assistant. Output valid JSON only.",
            user_content=q_prompt,
            expect_json=True
        )

        try:
            questions_data = json.loads(q_response)["questions"]
            questions = [UserQuestion(**q) for q in questions_data]
        except Exception as e:
            print(f"JSON Parsing error (Questions): {e}")
            questions = []


        print(f"[{self.name}] Creating Fictional Competitor")
        
        c_prompt = f"""
            Create a fictional competitor product (Product B) competing with {product.name}.
            The competitor should be realistic but different.
        
            Output Structure (JSON):
            {{ "name": "...", "key_ingredients": ["..."], "benefits": ["..."], "price": "..." }}
        """

        c_response = self.call_llm(
            system_prompt="You are a creative product strategist. Output valid JSON only.",
            user_content=c_prompt,
            expect_json=True
        )

        try:
            competitor = CompetitorProduct(**json.loads(c_response))
        except Exception as e:
             print(f"JSON Parsing Error (Competitor): {e}")
             competitor = CompetitorProduct(name="Unknown", key_ingredients=[], benefits=[], price="0")

        
        return AgentState(
            primary_product=product,
            generated_questions=questions,
            competitor_product=competitor
        )