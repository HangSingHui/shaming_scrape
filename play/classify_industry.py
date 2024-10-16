import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# Load the tokenizer and model for industry classification
tokenizer = AutoTokenizer.from_pretrained("sampathkethineedi/industry-classification")
model = AutoModelForSequenceClassification.from_pretrained("sampathkethineedi/industry-classification")

# Initialize the pipeline
industry_tags = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)

# Hardcode input file path
input_file_path = "output_data.json"

# Function to classify industry based on company description
def classify_industry(description):
    result = industry_tags(description)
    return result[0]['label']  # Return the label with the highest score

# Function to process the JSON data
def classify_companies():
    # Read the input JSON data
    with open(input_file_path, 'r') as infile:
        data = json.load(infile)
    
    # Iterate over each company and classify its industry
    for company in data:
        company_name = company.get('company', '')
        company_description = company.get('industry information', '')
        
        # Classify the industry using the model
        industry = classify_industry(company_description)
        
        # Add the industry classification to the existing data
        company['industry'] = industry  # Update or create 'industry' key

    # Save the updated data back to the same input file
    with open(input_file_path, 'w') as outfile:
        json.dump(data, outfile, indent=4)
    
    print(f"Classification completed. Results saved to {input_file_path}")

# Run the classification
if __name__ == "__main__":
    classify_companies()
