import React, { useEffect, useState } from 'react';
import axios from 'axios';
import CircularProgress  from '@material-ui/core/CircularProgress';
import { useLocation, useHistory } from "react-router-dom";

import Results from '../../components/Results/Results';
import Pager from '../../components/Pager/Pager';
import Facets from '../../components/Facets/Facets';
import SearchBar from '../../components/SearchBar/SearchBar';

import "./Search.css";

export default function Search() {
  
  let location = useLocation();
  let history = useHistory();
  
  const [ blob_results, setBlobResults ] = useState([]);
  const [ spo_results, setSpoResults ] = useState([]);

  const [ blob_resultCount, setBlobResultCount ] = useState(0);
  const [ spo_resultCount, setSpoResultCount ] = useState(0);

  const [ currentPage, setCurrentPage ] = useState(1);
  const [ q, setQ ] = useState(new URLSearchParams(location.search).get('q') ?? "*");
  const [ top ] = useState(new URLSearchParams(location.search).get('top') ?? 8);
  const [ skip, setSkip ] = useState(new URLSearchParams(location.search).get('skip') ?? 0);
  const [ blob_filters, setBlobFilters ] = useState([]);
  const [ spo_filters, setSpoFilters ] = useState([]);

  const [ blob_facets, setBlobFacets ] = useState({});
  const [ spo_facets, setSpoFacets ] = useState({});

  const [ isLoading, setIsLoading ] = useState(true);

  let resultsPerPage = top;
  
  useEffect(() => {
    setIsLoading(true);
    setSkip((currentPage-1) * top);
    const body = {
      q: q,
      top: top,
      skip: skip,
      blob_filters: blob_filters,
      spo_filters: spo_filters
    };
    
    console.log(body);

    axios.post( '/api/search', body)
      .then(response => {
            console.log(JSON.stringify(response.data))
            setBlobResults(response.data.devops.results);
            setBlobFacets(response.data.devops.facets);
            setBlobResultCount(response.data.devops.count);
            setSpoResults(response.data.sharepoint.results);
            setSpoFacets(response.data.sharepoint.facets);
            setSpoResultCount(response.data.sharepoint.count);
            setIsLoading(false);
        } )
        .catch(error => {
            console.log(error);
            setIsLoading(false);
        });
    
  }, [q, top, skip, blob_filters, spo_filters, currentPage]);

  // pushing the new search term to history when q is updated
  // allows the back button to work as expected when coming back from the details page
  useEffect(() => {
    history.push('/search?q=' + q);  
    setCurrentPage(1);
    setBlobFilters([]);
    setSpoFilters([]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q]);


  let postSearchHandler = (searchTerm) => {
    //console.log(searchTerm);
    setQ(searchTerm);
  }

  var body;
  if (isLoading) {
    body = (
      <div className="col-md-9">
        <CircularProgress />
      </div>);
  } else {
    body = (
      <div class="container">
        <div class="row">
          <div className="col-md-9">
            <h5>DevOps</h5>
            <Results documents={blob_results} top={top} skip={skip} count={blob_resultCount}></Results>
            <Pager className="pager-style" currentPage={currentPage} resultCount={blob_resultCount} resultsPerPage={resultsPerPage} setCurrentPage={setCurrentPage}></Pager>
          </div>
          <div className="col-md-9">
            <h5>Sharepoint</h5>
            <Results documents={spo_results} top={top} skip={skip} count={spo_resultCount}></Results>
            <Pager className="pager-style" currentPage={currentPage} resultCount={spo_resultCount} resultsPerPage={resultsPerPage} setCurrentPage={setCurrentPage}></Pager>
          </div>
        </div>
      </div>
    )
  }

  return (
    <main className="main main--search container-fluid">
      
      <div className="row">
        <div className="col-md-3">
          <div className="search-bar">
            <SearchBar postSearchHandler={postSearchHandler} q={q}></SearchBar>
          </div>
          <Facets facets={blob_facets} filters={blob_filters} setFilters={setBlobFilters}></Facets>
          <Facets facets={spo_facets} filters={spo_filters} setFilters={setSpoFilters}></Facets>
        </div>
        {body}
      </div>
    </main>
  );
}
