import logging
import azure.functions as func
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from shared_code import azure_config
import json


# import os

# def azure_config():

    # configs={}
    # configs["blob_search_facets"]= "Organization,Project,Area,WorkItemType"
    # configs["spo_search_facets"]= "metadata_spo_item_size,metadata_spo_item_content_type"
    # configs["blob_search_index_name"]=os.environ.get("SearchBlobIndexName","blobstoragedevopsdev")
    # configs["spo_search_index_name"]=os.environ.get("SearchSpoIndexName","sharepointdev")
    # configs["search_service_name"]=os.environ.get("SearchServiceName","srch-serviciobusqueda-standard-dev")
    # configs["search_api_key"]=os.environ.get("SearchApiKey","EB4EAF9AA1FE1B2C287BA11710CCE19F")

#     return configs

environment_vars = azure_config()


# Set Azure Search endpoint and key
endpoint = f'https://{environment_vars["search_service_name"]}.search.windows.net'
key = environment_vars["search_api_key"]

# Your index name
blob_index_name = environment_vars["blob_search_index_name"]
spo_index_name = environment_vars["spo_search_index_name"]

# Create Azure SDK client
blob_search_client = SearchClient(endpoint, blob_index_name, AzureKeyCredential(key))
spo_search_client = SearchClient(endpoint, spo_index_name, AzureKeyCredential(key))

def main(req: func.HttpRequest) -> func.HttpResponse:

    # variables sent in body
    req_body = req.get_json()
    q = req_body.get('q')
    top = req_body.get('top')
    suggester = req_body.get('suggester')

    if q:
        logging.info(f"/Sugerir q = {q}")
        blob_suggestions = blob_search_client.suggest(search_text=q, suggester_name=suggester, top=top)
        spo_suggestions = spo_search_client.suggest(search_text=q, suggester_name=suggester, top=top)
        
        # format the React app expects
        full_response = {}
        full_response["suggestions"] = blob_suggestions + spo_suggestions

        return func.HttpResponse(body=json.dumps(full_response), mimetype="application/json",status_code=200)
    else:
        return func.HttpResponse(
             "Parametro de consulta no encontrado.",
             status_code=200
        )

if __name__ == '__main__':

    load = {"q": "HU", "top": 5, "suggester": "sg"}
    load = json.dumps(load)
    load = bytes(load,'UTF-8')
    

    response = main(func.HttpRequest(method='post', url='', body=load))
    print(f'Status Code: {response.status_code}')
    resp = json.loads(response.get_body())
    print(resp)
