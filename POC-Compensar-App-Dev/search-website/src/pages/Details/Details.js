import React, { useState, useEffect } from "react";
import { useParams } from 'react-router-dom';
// import Rating from '@material-ui/lab/Rating';
import CircularProgress from '@material-ui/core/CircularProgress';
import axios from 'axios';

import "./Details.css";

export default function Details() {

  let { id } = useParams();
  const [document, setDocument] = useState({});
  const [source, setSource] = useState("")
  const [selectedTab, setTab] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    // console.log(id);
    axios.get('/api/lookup?id=' + id)
      .then(response => {
        console.log(JSON.stringify(response.data))
        const doc = response.data.document;
        const src = response.data.source;
        setDocument(doc);
        setSource(src);
        setIsLoading(false);
      })
      .catch(error => {
        console.log(error);
        setIsLoading(false);
      });

  }, [id]);

  // View default is loading with no active tab
  let detailsBody = (<CircularProgress />),
      resultStyle = "nav-link",
      rawStyle    = "nav-link";

  if (!isLoading && document) {
    // View result
    if (selectedTab === 0) {
      if (source === "blob"){
        resultStyle += " active";
        detailsBody = (
          <div className="card-body">
            <h5 className="card-text">Item id: {document.id}</h5>
            <h5 className="card-title">{document.Title}</h5>
            <p className="card-text">Tipo: {document.WorkItemType}</p>
            <p className="card-text">Organización: {document.Organization} - Proyecto: {document.Project}</p>
            <p className="card-text">Creado por: {document.CreatedBy} - Fecha: {document.CreatedDate}</p>
            <p>Url: <a href={document.Url}>{document.Url}</a></p>
          </div>
        );
      } else if (source === "sharepoint"){
        resultStyle += " active";
        detailsBody = (
          <div className="card-body">
            {/* <h5 className="card-text">ID: {document.id}</h5> */}
            <h5 className="card-title">{document.Title}</h5>
            <p className="card-text">Tipo: {document.Type}</p>
            <p className="card-text">Fecha ultima modificacion: {document.Modified}</p>
            <p>Url: <a href={document.Url}>{document.Url}</a></p>
          </div>
        );
      }
    }

    // View raw data
    else {
      rawStyle += " active";
      detailsBody = (
        <div className="card-body text-left">
          <pre><code>
            {JSON.stringify(document, null, 2)}
          </code></pre>
        </div>
      );
    }
  }

  return (
    <main className="main main--details container fluid">
      <div className="card text-center result-container">
        <div className="card-header">
          <ul className="nav nav-tabs card-header-tabs">
              <li className="nav-item"><button className={resultStyle} onClick={() => setTab(0)}>Result</button></li>
              <li className="nav-item"><button className={rawStyle} onClick={() => setTab(1)}>Raw Data</button></li>
          </ul>
        </div>
        {detailsBody}
      </div>
    </main>
  );
}
