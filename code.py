import json
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Content
from parser import parse_pdf
import os
from prompts import EOB_CLAIMS_PROMPT, PATIENT_CPT_PROMPT
from google.oauth2 import service_account
import fitz
import time

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
        input_tokens = model.count_tokens(EOB_CLAIMS_PROMPT+text).total_tokens
        response = model.generate_content(contents=EOB_CLAIMS_PROMPT+text, generation_config=generation_config)
        out_tokens = model.count_tokens(response.text).total_tokens
        response_text = response.text.strip()

        if response_text.startswith("```"):
            response_text = "\n".join(response_text.split("\n")[1:-1])
            
        response_text = response_text.rstrip(',')
        
        try:
            parsed_json = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print("Raw Response:", response_text)
            return None, input_tokens, out_tokens

        return parsed_json, input_tokens, out_tokens

    except Exception as e:
        print(f"An error occurred: {e}")
        return None, 0, 0


def pateint_cpt_info_extraction(text, claim_number):
    try:
        input_tokens = model.count_tokens(PATIENT_CPT_PROMPT+text).total_tokens
        response = model.generate_content(contents="Given Claim number:"+claim_number+PATIENT_CPT_PROMPT+text, generation_config=generation_config)
        out_tokens = model.count_tokens(response.text).total_tokens
        response_text = response.text.strip()
        
        if response_text.startswith("```"):
            response_text = "\n".join(response_text.split("\n")[1:-1])
            
        response_text = response_text.rstrip(',')
        
        try:
            parsed_json = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print("Raw Response:", response_text)
            return None, input_tokens, out_tokens

        return parsed_json, input_tokens, out_tokens


    except Exception as e:
        print(f"An error occurred: {e}")
        return None, 0, 0

def total_pages(pdf_path):
    
    try:
        pdf_document = fitz.open(pdf_path)
        page_count = pdf_document.page_count
        pdf_document.close()  # Important: close the PDF
        return page_count
    except FileNotFoundError:
        print(f"Error: PDF file not found at {pdf_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
    
def process_pdf(pdf_path, output_pdf_path):
    inp_cost_per_m_tokens = 1.25 / 10**6
    out_cost_per_m_tokens = 5 / 10**6
    total_input_tokens = 0
    total_output_tokens = 0
    final_output = []

    pages = total_pages(pdf_path)
    llama_cost_per_page = 0.01

    text = parse_pdf(pdf_path)
    if text is None:
        return

    retries = 3
    eob_claims_info, inp, out = None, 0, 0
    for _ in range(retries):
        eob_claims_info, inp, out = eob_info_extraction(text)
        if eob_claims_info:
            break
        time.sleep(2)

    total_input_tokens += inp
    total_output_tokens += out

    if not eob_claims_info:
        return

    eob_info = eob_claims_info.get("EOB_info", {})
    claims = eob_claims_info.get("claim_numbers", [])
    print("Extracted Claims in this pdf:", claims)

    for claim_number in claims:
        patient_cpt_info, inp, out = None, 0, 0
        for _ in range(retries):
            patient_cpt_info, inp, out = pateint_cpt_info_extraction(text, claim_number)
            if patient_cpt_info:
                break
            time.sleep(2)

        total_input_tokens += inp
        total_output_tokens += out

        if patient_cpt_info is None:
            continue
        
        patient_info = patient_cpt_info.get("Patient_info", {})
        cpt_info = patient_cpt_info.get("service_line_items", [])
        print("Extracted service line items info for {} claim number".format(claim_number))
        final_entry = {
            "EOB_info": eob_info,
            "Patient_info": patient_info,
            "service_line_items": cpt_info
        }
        final_output.append(final_entry)
    
    total_cost = inp_cost_per_m_tokens*total_input_tokens+out_cost_per_m_tokens*total_output_tokens+pages*llama_cost_per_page
    print("Total cost for this pdf:",total_cost)
    print("Cost per page:", total_cost/pages)
    try:
        
        with open(output_pdf_path, "w") as json_file:
            json.dump(final_output, json_file, indent=4)
        print("Output saved to output.json")
    except Exception as e:
        print(f"An error occurred while saving the output: {e}")

input_pdf_path = r"C:\Users\nikhil.rajput\Downloads\ADVANCEDMOTION REHABILITATION_HIGHMARKBLUESHIELD_03-04-2025_$0.00_Availity.pdf"
file_name = os.path.basename(input_pdf_path).replace(".pdf", ".json")
output_pdf_path = r"C:\Users\nikhil.rajput\Desktop\GeminiStarterApps\docs\Llama_Parse\outputs\\"+file_name
process_pdf(input_pdf_path, output_pdf_path)

