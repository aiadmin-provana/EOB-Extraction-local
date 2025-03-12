
from llama_cloud_services import LlamaParse
from llama_index.core import SimpleDirectoryReader


parser = LlamaParse(
    result_type="markdown",
    api_key="llx-9rttBgLWAMPpLGB0hTXRSgYuPkcRTl7YAeHUElnS5GvyGE5l",
    # use_vendor_multimodal_model=True,
    # vendor_multimodal_model_name="openai-gpt-4o-mini"
    gpt4o_mode=True
    # parsing_mode="parse_document_with_llm",
    # continuous_mode=True
)

def parse_pdf(file_path):
    print("Parsing pdf to markdown")
    
    try:
        file_extractor = {".pdf": parser}
        documents = SimpleDirectoryReader(input_files=[file_path], file_extractor=file_extractor).load_data()

        text = ""
        for doc in documents:
            text += doc.text

        print("Suuccessfully parsed pdf to markdown")
        
        return text
    
    except Exception as e:
        print("An error occured while parsing the pdf: ", e)
        return None