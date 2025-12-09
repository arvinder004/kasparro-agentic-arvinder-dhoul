from typing import List, Dict, Any
from src.models import ProductData, CompetitorProduct

class ContentLogicBlocks:
    
    @staticmethod
    def extract_benefits_list(product: ProductData) -> str:
        items = "".join([f"<li>{b}</li>" for b in product.benefits])
        return f"<ul>{items}</ul>"
    
    @staticmethod
    def compare_prices(p1: ProductData, p2: CompetitorProduct) -> str:
        try:
            diff = p1.price - p2.price

            if diff < 0:
                return f"{p1.name} is cheaper by ₹{abs(diff):.2f}."
            elif diff > 0:
                return f"{p2.name} is cheaper by ₹{abs(diff):.2f}."
            else:
                return "Both products have the exact same price."
        except:
            return "Price comparison unavailable"
        

TEMPLATES = {
    "faq_page": {
        "page_type": "FAQ Page",
        "structure": [
            {"section": "Header", "instruction": "Write a welcoming H1 and intro text using product name"},
            {"section": "Safety_Questions", "source": "subset_questions", "filter": "Safety"},
            {"section": "Usage_Questions", "source": "subset_questions", "filter": "Usage"},
        ]
    },
    "product_page": {
        "page_type": "Product Description Page",
        "structure": [
            {"section": "Hero", "instruction": "Write a persuasive marketing hook."},
            {"section": "Key Benefits", "source": "logic_block", "function": "extract_benefits_list"},
            {"section": "How to Use", "instruction": "Step by step guide based on 'how_to_use' field."},
        ]
    },
    "comparison_page": {
        "page_type": "Comparison Page",
        "structure": [
            {"section": "Head-to-Head", "instruction": "Intro comparing Primary vs Competitor B."},
            {"section": "Price Analysis", "source": "logic_block", "function": "compare_prices"},
            {"section": "Why Choose Us", "instruction": "Summarize advantages of Primary product."},
        ]
    }
}
    