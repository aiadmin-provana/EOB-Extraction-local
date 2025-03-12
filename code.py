import json
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Content
from parser import parse_pdf
import os
from prompts import EOB_CLAIMS_PROMPT, PATIENT_CPT_PROMPT

# Initialize Vertex AI
vertexai.init(
    project="gen-lang-client-0443511296",
    location="us-central1",
    api_endpoint="us-central1-aiplatform.googleapis.com"
)

model = GenerativeModel("gemini-2.0-pro-exp-02-05")

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 0.0,
    "top_p": 0.95,
}
def eob_info_extraction(text):
    try:
        response = model.generate_content(contents=EOB_CLAIMS_PROMPT+text, generation_config=generation_config)
        response_text = response.text.strip()

        if response_text.startswith("```"):
            response_text = "\n".join(response_text.split("\n")[1:-1])
            
        return json.loads(response_text)

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def pateint_cpt_info_extraction(text, claim_number):
    try:
        response = model.generate_content(contents="Given Claim number:"+claim_number+PATIENT_CPT_PROMPT+text, generation_config=generation_config)
        response_text = response.text.strip()
        
        if response_text.startswith("```"):
            response_text = "\n".join(response_text.split("\n")[1:-1])
            
        response_text = response_text.rstrip(',')
        
        try:
            parsed_json = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print("Raw Response:", response_text)
            return None

        return parsed_json

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def process_pdf(pdf_path, output_pdf_path):
    final_output = []
    
    text = parse_pdf(pdf_path)
    if text is None:
        print("Failed to parse PDF to markdown.")
        return
    
    eob_claims_info = eob_info_extraction(text)
    if not eob_claims_info:
        print("Failed to extract EOB claims info.")
        return
    
    eob_info = eob_claims_info.get("EOB_info", {})
    claims = eob_claims_info.get("claim_numbers", [])

    print("Extracted EOB and claims info")
    print("Claims:", claims)

    for claim_number in claims:
        patient_cpt_info = pateint_cpt_info_extraction(text, claim_number)
        if patient_cpt_info is None:
            print(f"Failed to extract patient CPT info for claim number: {claim_number}")
            continue
        else:
            patient_name = patient_cpt_info.get("Patient_info", {}).get("Patient_Name", "")
            print("Extracted patient CPT info for:", claim_number, "-", patient_name)
            patient_info = patient_cpt_info.get("Patient_info", {})
            cpt_info = patient_cpt_info.get("service_line_items", [])
            final_entry = {
                "EOB_info": eob_info,
                "Patient_info": patient_info,
                "service_line_items": cpt_info
            }
            final_output.append(final_entry)

    try:
        
        with open(output_pdf_path, "w") as json_file:
            json.dump(final_output, json_file, indent=4)
        print("Output saved to output.json")
    except Exception as e:
        print(f"An error occurred while saving the output: {e}")

input_pdf_path = r"C:\Users\nikhil.rajput\Desktop\GeminiStarterApps\docs\input pdfs\Fw_ Sample EOBs via Availity\02132025_0085036395_$4.06_Availityfederalemployee.pdf"
file_name = os.path.basename(input_pdf_path).replace(".pdf", ".json")

output_pdf_path = r"C:\Users\nikhil.rajput\Desktop\GeminiStarterApps\docs\Llama_Parse\outputs\\"+file_name
process_pdf(input_pdf_path, output_pdf_path)

