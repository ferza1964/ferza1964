import logging
from re import I
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

# returns obj like {authors: 'array', language_code:'string'}
def read_facets(facetsString):
    facets = facetsString.split(",")
    output = {}
    for x in facets:
        if(x.find('*') != -1):
            newVal = x.replace('*','')
            output[newVal]='array'
        else: 
            output[x]='string'
            
    return output


# creates filters in odata syntax
def create_filter_expression(filter_list, facets):
    i = 0
    filter_expressions = []
    return_string = ""
    separator = ' and '

    while (i < len(filter_list)) :
        field = filter_list[i]["field"]
        value = filter_list[i]["value"]
        
        if (facets[field] == 'array'): 
            print('array')
            filter_expressions.append(f'{field}/any(t: search.in(t, \'{value}\', \',\'))')
        else :
            print('value')
            filter_expressions.append(f'{field} eq \'{value}\'')
        
        i += 1
    
    
    return_string = separator.join(filter_expressions)

    return return_string

def blob_new_shape(docs):
    
    old_api_shape = list(docs)
    
    count=0
    client_side_expected_shape = []
    
    for item in old_api_shape:
        
        new_document = {}
        new_document["score"]=item["@search.score"]
        new_document["highlights"]=item["@search.highlights"]

        new_shape = {}
        new_shape["id"]=item["id"]
        new_shape["Organization"]=item["Organization"]
        new_shape["Project"]=item["Project"]
        new_shape["Area"]=item["Area"]        
        new_shape["WorkItemType"]=item["WorkItemType"]        
        new_shape["Title"]=item["Title"]
        new_shape["CreatedDate"]=item["CreatedDate"]
        new_shape["CreatedBy"]=item["CreatedBy"]
        new_shape["AssignedTo"]=item["AssignedTo"]
        new_shape["Description"]=item["Description"]
        new_shape["State"]=item["State"]
        new_shape["NonFunctionalType"]=item["NonFunctionalType"]
        new_shape["CompensarDelayGroup"]=item["CompensarDelayGroup"]
        new_shape["Url"]=item["Url"]
        
        new_document["document"]=new_shape
        
        client_side_expected_shape.append(new_document)
    
    return list(client_side_expected_shape)

def spo_new_shape(docs):
    
    old_api_shape = list(docs)
    
    count=0
    client_side_expected_shape = []
    
    for item in old_api_shape:
        
        new_document = {}
        new_document["score"]=item["@search.score"]
        new_document["highlights"]=item["@search.highlights"]

        new_shape = {}
        new_shape["id"]=item["id"]
        new_shape["Title"]=item["metadata_spo_item_name"]
        new_shape["Path"]=item["metadata_spo_item_path"]
        new_shape["Type"]=item["metadata_spo_item_content_type"]        
        new_shape["Modified"]=item["metadata_spo_item_last_modified"]        
        new_shape["Size"]=item["metadata_spo_item_size"]
        new_shape["Url"]=item["metadata_spo_item_weburi"]
        # new_shape["content"]=item["content"]
        
        new_document["document"]=new_shape
        
        client_side_expected_shape.append(new_document)
    
    return list(client_side_expected_shape)



def main(req: func.HttpRequest) -> func.HttpResponse:

    try:
        # variables sent in body
        req_body = req.get_json()
        q = req_body.get('q')
        top = req_body.get('top') or 8
        blob_skip = req_body.get('blob_skip') or 0
        spo_skip = req_body.get('spo_skip') or 0
        blob_filters = req_body.get('blob_filters') or []
        spo_filters = req_body.get('spo_filters') or []

        blob_facets = environment_vars["blob_search_facets"]
        blob_facetKeys = read_facets(blob_facets)

        spo_facets = environment_vars["spo_search_facets"]
        spo_facetKeys = read_facets(spo_facets)
        
        blob_filter = ""
        spo_filter = ""
        if(len(blob_filters) and len(spo_filters)):
            blob_filter = create_filter_expression(blob_filters, blob_facetKeys)
            spo_filter = create_filter_expression(spo_filters, spo_facetKeys)
        elif(len(spo_filters)):
            spo_filter = create_filter_expression(spo_filters, spo_facetKeys)
        elif(len(blob_filters)):
            blob_filter = create_filter_expression(blob_filters, blob_facetKeys)
        

        if q:
            logging.info(f"/Buscar q = {q}")
            
            blob_search_results = blob_search_client.search(
                search_text=q, 
                top=top,skip=blob_skip, 
                facets=blob_facetKeys, 
                filter=blob_filter, 
                include_total_count=True
            )
            spo_search_results = spo_search_client.search(
                search_text=q, 
                top=top,
                skip=spo_skip, 
                facets=spo_facetKeys, 
                filter=spo_filter, 
                include_total_count=True
            )
            blob_returned_docs = blob_new_shape(blob_search_results)
            spo_returned_docs = spo_new_shape(spo_search_results)
            blob_returned_count = blob_search_results.get_count()
            spo_returned_count = spo_search_results.get_count()
            blob_returned_facets = blob_search_results.get_facets()
            spo_returned_facets = spo_search_results.get_facets()
            
            # format the React app expects
            blob_response = {}
            blob_response["count"] = blob_returned_count
            blob_response["facets"] = blob_returned_facets
            blob_response["results"]=blob_returned_docs

            spo_response = {}
            spo_response["count"] = spo_returned_count
            spo_response["facets"] = spo_returned_facets
            spo_response["results"]=spo_returned_docs

            full_response = {"devops": blob_response, "sharepoint": spo_response}

            return func.HttpResponse(
                body=json.dumps(full_response, ensure_ascii=False), 
                mimetype="application/json",
                status_code=200
            )
        else:
            return func.HttpResponse(
                "No se ha encontrado ningún parámetro de consulta.",
                status_code=200
            )
    except Exception as err:
        return func.HttpResponse(
                body=f"Error: {err}",
                mimetype="application/json",
                status_code=400
            )


if __name__ == '__main__':

    load = {"q":"*","top":1,"blob_skip":0, "spo_skip":0,"blob_filters":[],"spo_filters":[]}
    load = json.dumps(load)
    load = bytes(load,'UTF-8')
    
    response = main(func.HttpRequest(method='post', url='', body=load))
    print(f'Status Code: {response.status_code}')
    resp_devops = json.loads(response.get_body())
    json_formatted_str = json.dumps(resp_devops, indent=4, ensure_ascii=False)
    print(json_formatted_str)


    # with open("SearchResponse.json", "w") as write_file:
    #     json.dump(resp_devops, write_file, indent=4)
