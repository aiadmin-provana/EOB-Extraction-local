EOB_CLAIMS_PROMPT = """ You are an AI model designed to extract structured data from a **Markdown representation of a PDF document**.
                    Your task is to read the entire Markdown text and extract the required values from it. Along with that extract the **bounding box coordinates** of those values from the given PDF.
                    Extraction of the values should be from the markdown text only and bounding box coordinates of the corresponding values must be from the PDF only.
                    ### **Instructions:**
                    1. **Process the entire markdown text** to ensure all relevant details are captured accurately.
                    2. **Extract the first occurrence** of each requested value from the document.
                    3. **Extract all unique claim numbers** and include them as a list of strings in the output JSON.
                    4. **Provide bounding box coordinates** as a list of integers in the format `[y_min, x_min, y_max, x_max]` from the pdf for each extracted value.
                    5. **Return only the JSON output** in the exact format given below, without any explanations or extra text.
                    6. If a field value spans multiple lines, replace any `\n` with a **single space**.
                    7. Extract the **page number** where the EOB details are located and include it in the `eob_page_number` field.
                    8. **Identify key-value mappings** from the structured Markdown text using the mappings below:

                    ### **Field Mappings:**
                    - **Provider** = `Payee Name`
                    - **Cheque number** = `Check/EFT Trace Number`
                    - **Cheque amount** = `Payment Amount` / `Total Paid`
                    - **Cheque date** = `Check/EFT Date`

                    ### **Additional Guidelines:**
                    - Ensure **consistency in extracted data** by correctly interpreting Markdown structure such as headings, tables, and key-value pairs.
                    - Accurately capture the details **regardless of text formatting** (e.g., bold, italics, bullet points).
                    - **Do not hallucinate** missing values—if a value is not found in the Markdown document, leave it empty.
                    - Preserve the **hierarchical relationships** of claim numbers, patient details, and service line items.
                    - Convert extracted Markdown tables into structured JSON arrays.
                    - **Maintain a high degree of accuracy** when mapping values.

                    ### **Output Format:**
                    Return the extracted data strictly in JSON format with the correct structure, ensuring proper nesting of claim details and service line items.

                    This ensures precise extraction of structured information from Markdown-converted PDFs.



                    ### **Expected JSON Output Format:**
                    ```json
                    {
                        "claim_numbers": [
                            "",
                            ""
                        ],
                        "EOB_info": {
                            "EOB_file_path": "",
                            "EOB_file_downloaded_date": "",
                            "EOB_page_number": "",
                            "Payer": "",
                            "Payer_bounding_box": [],
                            "Provider": "",
                            "Provider_bounding_box": [],
                            "Payee_ID": "",
                            "Payee_ID_bounding_box": [],
                            "Cheque_number": "",
                            "Cheque_number_bounding_box": [],
                            "Cheque_amount": "",
                            "Cheque_amount_bounding_box": [],
                            "Cheque_date": "",
                            "Cheque_date_bounding_box": []
                        }
                        }
                    ```
                    Ensure accuracy in extraction and maintain the format strictly.
                    
                    Below is the markdown text extracted from the PDF along with the PDF document:\n


                    """

PATIENT_CPT_PROMPT = """You are an AI model designed to extract structured data from a **Markdown representation of a PDF document**.
                    Your task is to read the entire Markdown text and extract the required values. along with that extract the **bounding box coordinates** of those values from the given PDF.
                    Extraction of the values should be from the markdown text only and bounding box coordinates of the corresponding values must be from the PDF only.
                ### **Instructions:**

                1. **Process the entire Markdown text** to ensure all relevant details are captured.
                2. **Locate the given claim number** in the markdown text.
                4. **Provide bounding box coordinates** of the extracted value as a list of integers in the format `[y_min, x_min, y_max, x_max]` from thr PDF document.
                4. **Extract patient information and service line items** associated with the specified claim number.
                5. **Populate the provided JSON template** with the extracted information.
                6. **Ensure data integrity** by preserving multi-line values correctly, replacing line breaks with spaces where necessary.
                7. **For the patient information section:**
                - Use the mappings below to extract the values correctly:
                    - **Date of Service** = Claim Date
                    - **Patient’s Account Number** = Patient Ctrl Nmbr
                    - **Primary Insurance** = Claim Status Code
                    - **Patient Responsibility** = Patient Resp
                8. **For the service\_line\_items section:**
                - Locate "Line Details" after the claim number in the Markdown document.
                - Extract all service item details until the next claim number or patient name appears.
                - Use the following mappings to extract values correctly:
                    - **CPT/HCPCS** = Adjud Proc
                    - **Modifier** = Modifier
                    - **DU** = Units
                    Note: Extract from the "Adjud Proc/Modifier/Units" column. Example: If the value is "HC:97112 / GP / 1", extract: CPT/HCPCS = HC:97112,  Modifier = GP, DU = 1.
                    - **Date of Service** = Extracted from the table, not the patient claim date.
                    - **Reason Code** =  Adjustments(Qty)
                    Note: Extract all the values in the column Adjustments(Qty) and separate them by commas.
                    - **Paid_Amount** = Payment
                    - **Allowed_Amount** = Supp Info (AMT)
                    - **Billed_Amount** = Charge
                    - **Adj_Amount** = Adj Amount
                    Note:Extract all values from "Adj Amount" column and separate by comma in the Adj_Amount field; Note: For reason code = PR-1, PR-2, PR-3 map the value extracted to the corresponding fields instead of putting in adj_amount field:
                    Deductible = PR-1,
                    Co-insurance = PR-2,
                    Co-pay = PR-3;(For example if we have two reason codes PR-3: $11, CO-45: $44,CO-45: $55; then put $11(value of PR-1) in co-pay and rest other values of CO-45 should go in adj_amount field only separated by comma)
                    Note: only for PR-1, PR-2, PR-3 values should not be present in the adj_amount field, rest every value lets it be PR-XX, CO-XX must be included in the adj_amount filed.
                - Extract full Date of Service values, even if they span multiple lines.
                - Ensure multiple reason codes are separated by commas instead of line breaks.
                9. **Maintain the structured format** by preserving lists, tables, and hierarchical data.
                10. **Ensure the output is ONLY the completed JSON**—no extra text, explanations, or hallucinated values.
                11. **If a value is not present in the document, leave it empty instead of making assumptions.**


                Expected JSON output format:
                ```json
                    {
                    "Patient_info": {
                        "Patient_Name": "<Extracted Patient Name>",
                        "Patient_Name_bounding_box": [y_min, x_min, y_max, x_max],
                        "Claim_Number": "<Extracted Claim Number>",
                        "Claim_Number_bounding_box": [y_min, x_min, y_max, x_max],
                        "Date_of_Service": "<extracted Date of Service>",
                        "Date_of_Service_bounding_box": [y_min, x_min, y_max, x_max],
                        "Patient_Account_Number": "<extracted Patient Account Number>",
                        "Patient_Account_Number_bounding_box": [y_min, x_min, y_max, x_max],
                        "Diagnosis": "<extracted Diagnosis>",
                        "Diagnosis_bounding_box": [y_min, x_min, y_max, x_max],
                        "Patient_ID": "<extracted Patient ID>",
                        "Patient_ID_bounding_box": [y_min, x_min, y_max, x_max],
                        "Primary_insurance": "<extracted Primary Insurance>",
                        "Primary_insurance_bounding_box": [y_min, x_min, y_max, x_max],
                        "Claim_Frequency": "<extracted Claim Frequency>",
                        "Claim_Frequency_bounding_box": [y_min, x_min, y_max, x_max],
                        "Claim_charge": "<extracted Claim Charge>",
                        "Claim_charge_bounding_box": [y_min, x_min, y_max, x_max],
                        "Claim_Payment": "<extracted Claim Payment>",
                        "Claim_Payment_bounding_box": [y_min, x_min, y_max, x_max],
                        "Patient_responsibility": "<extracted Patient Responsibility>",
                        "Patient_responsibility_bounding_box": [y_min, x_min, y_max, x_max],
                        "Group_Policy": "<extracted Group Policy>",
                        "Group_Policy_bounding_box": [y_min, x_min, y_max, x_max],
                        "Patient_Date_of_Birth": "<extracted Patient Date of Birth>",
                        "Patient_Date_of_Birth_bounding_box": [y_min, x_min, y_max, x_max],
                        "Subscriber_id": "<extracted Subscriber ID>",
                        "Subscriber_id_bounding_box": [y_min, x_min, y_max, x_max]
                    },
                    "service_line_items": [
                        {
                        "CPT_HCPCS": "<extracted CPT_HCPCS>",
                        "CPT_HCPCS_bounding_box": [y_min, x_min, y_max, x_max],
                        "Modifier": "<extracted Modifier>",
                        "Modifier_bounding_box": [y_min, x_min, y_max, x_max],
                        "DU": "<extracted DU>",
                        "DU_bounding_box": [y_min, x_min, y_max, x_max],
                        "Reason_Code": "<extracted Reason Code>",
                        "Reason_Code_bounding_box": [y_min, x_min, y_max, x_max],
                        "Adj_Amount": "<extracted Adj Amount>",
                        "Adj_Amount_bounding_box": [y_min, x_min, y_max, x_max],
                        "Paid_Amount": "<extracted Paid Amount>",
                        "Paid_Amount_bounding_box": [y_min, x_min, y_max, x_max],
                        "Allowed_Amount": "<extracted Allowed Amount>",
                        "Allowed_Amount_bounding_box": [y_min, x_min, y_max, x_max],
                        "Payer_Code": "<extracted Payer Code>",
                        "Payer_Code_bounding_box": [y_min, x_min, y_max, x_max],
                        "Billed_Amount": "<extracted Billed Amount>",
                        "Billed_Amount_bounding_box": [y_min, x_min, y_max, x_max],
                        "Dx_Pt": "<extracted Dx Pt>",
                        "Dx_Pt_bounding_box": [y_min, x_min, y_max, x_max],
                        "Co_Pay": "<extracted amount value of PR-3>",
                        "Co_Pay_bounding_box": [y_min, x_min, y_max, x_max],
                        "Deductible": "<extracted amount value of PR-1>",
                        "Deductible_bounding_box": [y_min, x_min, y_max, x_max],
                        "Co_insurance": "<extracted value of PR-2>",
                        "Co_insurance_bounding_box": [y_min, x_min, y_max, x_max],
                        "Bill_to_Secondary": "<extracted Bill to Secondary>",
                        "Bill_to_Secondary_bounding_box": [y_min, x_min, y_max, x_max],
                        "Date_of_Service": "<extracted Date of Service>",
                        "Date_of_Service_bounding_box": [y_min, x_min, y_max, x_max],
                        "User_Status": "<extracted User Status>",
                        "User_Status_bounding_box": [y_min, x_min, y_max, x_max]
                        }
                    ]
                    }
                    ```
                    Ensure accuracy in extraction and maintain the format strictly.
                    
                    Below is the markdown text extracted from the PDF along with the PDF document:/n
                    """