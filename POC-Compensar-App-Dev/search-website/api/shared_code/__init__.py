import os

def azure_config():
    
    configs={}
    configs["blob_search_facets"]= "Organization,Project,Area,WorkItemType"
    configs["spo_search_facets"]= "metadata_spo_item_size,metadata_spo_item_content_type"
    configs["blob_search_index_name"]=os.environ.get("SearchBlobIndexName","blobstoragedevopsdev")
    configs["spo_search_index_name"]=os.environ.get("SearchSpoIndexName","sharepointdev")
    configs["search_service_name"]=os.environ.get("SearchServiceName","srch-serviciobusqueda-standard-dev")
    configs["search_api_key"]=os.environ.get("SearchApiKey","EB4EAF9AA1FE1B2C287BA11710CCE19F")
        
    return configs


if __name__ == '__main__':
    environment_vars = azure_config()
    print(environment_vars)
