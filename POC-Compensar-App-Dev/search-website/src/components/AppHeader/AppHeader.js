import React from 'react';
import AppHeaderAuth from '../AppHeaderAuth/AppHeaderAuth';

import './AppHeader.css';

export default function AppHeader() {
  return (
    <header className="header">
      <nav className="navbar navbar-expand-lg">
        <a className="navbar-brand" href="/">
          <img src="/images/microsoft-small.svg" className="navbar-logo" alt="Microsoft" />
        </a>
        <a className="navbar-brand" href="/">
          <img src="/images/compensar-logo.png" className="navbar-logo1" alt="Compensar" />
        </a>
        <a className="navbar-brand" href="/">
          <img src="/images/Logo-Ultracom.png" className="navbar-logo2" alt="UltracomITSAS" />
        </a>
        <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
          <span className="navbar-toggle  r-icon"></span>
        </button>

        <div className="collapse navbar-collapse" id="navbarSupportedContent">
          <ul className="navbar-nav mr-auto">
            <li className="nav-item">
              <a className="nav-link" href="/Search">Buscar</a>
            </li>
            <li className="nav-item">
              <a className="nav-link" href="https://azure.microsoft.com/services/search/">Aprender más</a>
            </li>
          </ul>
        </div>

        <AppHeaderAuth />
      </nav>
      
    </header>
  );
};
