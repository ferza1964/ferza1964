#fecha:08/07/2022
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

    docid = req.params.get('id') 
    # docid = "Y29tcGVuc2FyLnNoYXJlcG9pbnQuY29tLDhlYjkxZjIzLWFiZGUtNDNlMC1hNDU3LTgwMWIzMmY4Y2U3NCw5NWVjMTQxYS1lMDZhLTRlZjUtYWEwOS00NmE2YTExNWMzMjA6OmIhSXgtNWp0NnI0RU9rVjRBYk12ak9kQm9VN0pWcTRQVk9xZ2xHcHFFVnd5QWZ0QzY0V2xpdVJJdlFQTU1hdFZxZDo6MDFDT0pYVFhKUU81MlRUVU41QlpBTEdVQkFLWVZFQlQ3NQ2"        # Recordar quitar este número que es el de las pruebas
    # docid = 618 #Comentar
    # print(docid)

    if docid:
        logging.info(f"/Id de búsqueda = {docid}")

        try:
            blob_returnedDocument = blob_search_client.get_document(key=docid)
            composicion_url = f"""https://dev.azure.com/{blob_returnedDocument["Organization"]}/{blob_returnedDocument["Project"]}/_workItems/edit/{blob_returnedDocument["id"]}"""
            blob_returnedDocument["Url"] = composicion_url
        except:
            blob_returnedDocument = ""
        try:   
            spo_returnedDocument = spo_search_client.get_document(key=docid)
            key_map_dict = {
                "id":"id",
                "metadata_spo_item_name": "Title",
                "metadata_spo_item_path": "Path",
                "metadata_spo_item_content_type": "Type",
                "metadata_spo_item_last_modified": "Modified",
                "metadata_spo_item_size": "Size",
                "metadata_spo_item_weburi": "Url"
            }
            spo_returnedDocument = {(key_map_dict[k] if k in key_map_dict else k):v  for (k,v) in spo_returnedDocument.items() }
        except:
            spo_returnedDocument = ""

        full_response = {}
        if blob_returnedDocument != "":
            full_response["document"]=blob_returnedDocument
            full_response["source"]="blob"
        elif spo_returnedDocument != "":

            full_response["document"]=spo_returnedDocument
            full_response["source"]="sharepoint"

        return func.HttpResponse(body=json.dumps(full_response), mimetype="application/json", status_code=200)
    else:
        return func.HttpResponse(
             "No se ha encontrado ningún parámetro de id de documento.",
             status_code=200
        )


if __name__ == '__main__':

    response = main(func.HttpRequest(method='get', url='', body=''))
    print(f'Status Code: {response.status_code}')
    print(response.get_body())
