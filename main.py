import json
import os
from src.agents import AnalystAgent, PublisherAgent

RAW_DATA = {
    "Product Name": "GlowBoost Vitamin C Serum",
    "Concentration": "10% Vitamin C",
    "Skin Type": "Oily, Combination",
    "Key Ingredients": "Vitamin C, Hyaluronic Acid",
    "Benefits": "Brightening, Fades dark spots",
    "How to Use": "Apply 2–3 drops in the morning before sunscreen",
    "Side Effects": "Mild tingling for sensitive skin",
    "Price": "₹699"
}

def ensure_output_dir():
    if not os.path.exists("output"):
        os.makedirs("output")

def main():
    ensure_output_dir()

    analyst = AnalystAgent(name='Analyst-001')
    publisher = PublisherAgent(name="Publisher-001")

    print("ANALYSIS")
    state = analyst.run(raw_data=RAW_DATA)

    with open("output/internal_state.json", "w") as f:
        f.write(state.model_dump_json(indent=2))

    
    print("PAGE GENERATION")
    
    faq_page = publisher.build_page(state, "faq_page")
    with open("output/faq_page.json", 'w') as f:
        f.write(faq_page.model_dump_json(indent=2))

    product_page = publisher.build_page(state, "product_page")
    with open("output/product_page.json", 'w') as f:
        f.write(product_page.model_dump_json(indent=2))

    comparison_page = publisher.build_page(state, "comparison_page")
    with open("output/comparison_page.json", 'w') as f:
        f.write(comparison_page.model_dump_json(indent=2))

    print("SUCCESS")
    print("ALL PAGES GENERATED")


if __name__ == "__main__":
    main()