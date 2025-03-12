import json
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Content
from parser import parse_pdf
import os
from prompts import EOB_CLAIMS_PROMPT, PATIENT_CPT_PROMPT
from google.oauth2 import service_account


# Your JSON key as a string (Store securely!)
json_creds = """{
  "type": "service_account",
  "project_id": "gen-lang-client-0443511296",
  "private_key_id": "0f517c50a44b7d73ebf42e3f7de66895ffc04d32",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCYOOgpAsaKSz1R\\nnrmeyabzmbeG8TZ7Vi+VW4NgtcHVIYDtH7GBMVIn0qbe750KPCJYiOZi8WHvtuJ1\\nBpvpz6MctFH0qMwtmpJ8C9Vn8TRugR0rsKbld8yKhDLCjJquuJiNlUstnUidB+Ch\\nOc9+xtLsOCqdh3uqn/4jiodNnHhviWrbk64aoltiagXlSLVSQe8ht7FQCJhQy5Ux\\n1LTuF5uljiR35czdM8RArpRemFKCXm5wYTXOvD3LVniBtNCi3sretHipeXyTS+nV\\nKsP8Kf04qvmlb5BlO9LJv8TmYn9EIO3CfEnQG+vxPD2S7lQ4A3vxBGA3q/nUv5cs\\n3HXOevZhAgMBAAECggEADYRUHTwpXCNlPQeurOp0IEKAmQN3VolnLUiUiHRrU10n\\nwSak0PeLt4yNk9NMKxn+5MS3TIbprusa/dBJ7P+qmMRsWKDajJwisNAuMY4qHTvq\\n1rPXhh3WtGAbz8nDfItYxI3CwLisN4F5EWf8RGIsXZx5MEbVFOgjHY3SCPLBgQnc\\nN0L7x7Z+npUliHx53bSxr8WbSS9XlxaBWmShkodoX6yKZC2JQBVVQSp3RlGeMS4w\\nvS49eMfKzjLLzSxhH1ikZ9xjHnx7bPeLRdrrMqqzc29YcY0L2yFBEsFKYGDDypeV\\n4unw/JiGp338uy9uIGoJ/jzvkPBUx0NCcyWVJupH7wKBgQC/P6qOXOMoKec6Z94y\\ng65Az7/fekj3C/vzwU15tQxE/mu6MmQlyMgznSTujckHTFOVpztHDxCwMozJaxjC\\nGPAQXQqBz7zyqMoI0wdlrymBZ8YDz+2hbbnDiPyGHbqlCRBDMQCb6iX3SKeznzRk\\nK2Q7ghUybmj8Jv+06SBVyHGDRwKBgQDLwqg3ANdyKsY5/K3HObZDB62P2+xr9LkW\\nnIp89Xn6Ss2ZdpSdkpoXckJXrUVAqZC76XWzq1Ao+FRoEVhG8jMDEWNy+Va/6oI4\\nZiQdJdVNYOea46D494DRpP/9XPvdsLMqme/RPh3BdAzGm1I9TXpkYgxf9lshxLXu\\nyKvbjZ39FwKBgH8vl/2VSHwtYdk1uk9dw0TW5IN6j4u8LJKuuxd1j/NSP9JUMMXw\\nATRSDX2YTVjNKckcrg9TtYV4GKja0FxEuWIofhRWUxINrk6wCPtWwgONP+LJJP92\\nOVQQhd+rZbTbkjUdIYqO7TDG4MBT4EO9l6r7l50yUB9g0C0/3IEwDE2BAoGAM73Q\\nfXcnPoSCJcN2VXrgP5E5j6hnFtrkDUvfFvA280n/f5LPFlxd6MpI8n67cTod2Lnl\\n+6PrDRxSQsL0yb9DGOpXeKC8WKuyOaQmU4iB685Jwdk/zTj8a0AdCTeNdbQjKxRA\\nA8BkSfWwMNbMQWjlRYxoXA3xAlgzYtluWqhRkC0CgYAOT9KvJGIzzwfZ4o9YCboH\\n20VhoshRiN93+EfGXkDdHLgqM8AAhrL8ff4TbP0iVoNArVaqiy3gfipjW8oIX/J7\\ntUjMBmvpHEFIU5S0ROXChtKuQiRRGokJdYLqajeZiUIuEYAvJPpwP9g56ZxxpoII\\nerLgb+p1JA/bDYVcihukRg==\\n-----END PRIVATE KEY-----\\n",
  "client_email": "gen-lang-client-0443511296@appspot.gserviceaccount.com",
  "client_id": "115163114072113786507",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/gen-lang-client-0443511296%40appspot.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}"""

# Convert JSON string to dictionary
creds_dict = json.loads(json_creds)

# Create Google Credentials object from the JSON dictionary
credentials = service_account.Credentials.from_service_account_info(creds_dict)


generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.0,
        "top_p": 0.95,
}

# Initialize Vertex AI with credentials
vertexai.init(
    project=creds_dict["project_id"],
    location="us-central1",  # Change to your region if needed
    credentials=credentials
)

# Initialize the Gemini model with a valid public model name
model = GenerativeModel("gemini-2.0-pro-exp-02-05") 
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

