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

  const [ blob_currentPage, setBlobCurrentPage ] = useState(1);
  const [ spo_currentPage, setSpoCurrentPage ] = useState(1);

  const [ q, setQ ] = useState(new URLSearchParams(location.search).get('q') ?? "*");
  const [ top ] = useState(new URLSearchParams(location.search).get('top') ?? 8);
  const [ blob_skip, setBlobSkip ] = useState(new URLSearchParams(location.search).get('skip') ?? 0);
  const [ spo_skip, setSpoSkip ] = useState(new URLSearchParams(location.search).get('skip') ?? 0);
  const [ blob_filters, setBlobFilters ] = useState([]);
  const [ spo_filters, setSpoFilters ] = useState([]);

  const [ blob_facets, setBlobFacets ] = useState({});
  const [ spo_facets, setSpoFacets ] = useState({});

  const [ isLoading, setIsLoading ] = useState(true);

  let resultsPerPage = top;
  
  useEffect(() => {
    setIsLoading(true);
    setBlobSkip((blob_currentPage-1) * top);
    setSpoSkip((spo_currentPage-1) * top);

    const body = {
      q: q,
      top: top,
      blob_skip: blob_skip,
      spo_skip: spo_skip,
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
    
  }, [q, top, blob_skip, spo_skip, blob_filters, spo_filters, blob_currentPage, spo_currentPage]);

  // pushing the new search term to history when q is updated
  // allows the back button to work as expected when coming back from the details page
  useEffect(() => {
    history.push('/search?q=' + q);
    setBlobCurrentPage(1);
    setSpoCurrentPage(1);
    setBlobFilters([]);
    setSpoFilters([]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q]);


  let postSearchHandler = (searchTerm) => {
    //console.log(searchTerm);
    setQ(searchTerm);
  }

  var devopsbody;
  var spobody;
  if (isLoading) {
    devopsbody = (
        <div className="col-md-9">
          <CircularProgress />
        </div>);
    spobody = (
        <div className="col-md-9">
          <CircularProgress />
        </div>);
  } else {
    devopsbody = (
        <div className="col-9">
            <h5>DevOps</h5>
            <Results documents={blob_results} top={top} skip={blob_skip} count={blob_resultCount}></Results>
            <Pager className="pager-style" currentPage={blob_currentPage} resultCount={blob_resultCount} resultsPerPage={resultsPerPage} setCurrentPage={setBlobCurrentPage}></Pager>
        </div>
    )
    spobody = (
        <div className="col-9">
            <h5>Sharepoint</h5>
            <Results documents={spo_results} top={top} skip={spo_skip} count={spo_resultCount}></Results>
            <Pager className="pager-style" currentPage={spo_currentPage} resultCount={spo_resultCount} resultsPerPage={resultsPerPage} setCurrentPage={setSpoCurrentPage}></Pager>
        </div>
    )

  }

  return (
    <main className="main main--search container-fluid">
      <div class="container">
        <div className="row">
          <div className="col-12">
            <div className="search-bar">
              <SearchBar postSearchHandler={postSearchHandler} q={q}></SearchBar>
            </div>
          </div>
        </div>
        <div className="row">
          <div class="col-3">
          <Facets facets={blob_facets} filters={blob_filters} setFilters={setBlobFilters}></Facets>
          </div>
          {devopsbody}
        </div>
        <div className="row">
          <div class="col-3">
          <Facets facets={spo_facets} filters={spo_filters} setFilters={setSpoFilters}></Facets>
          </div>
          {spobody}
        </div>
      </div>
    </main>
  );
}
