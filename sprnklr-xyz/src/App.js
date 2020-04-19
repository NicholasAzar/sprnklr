import React from 'react';
import './App.css';
import {
  BrowserRouter as Router,
  Switch,
  Route,
} from 'react-router-dom';
import Dashboard from './dashboard/dashboard.js' ;
import axios from 'axios';
axios.defaults.withCredentials = true;

function App() {
  return (
    <Router>
      <div className="App">
        {
          <Switch>
            <Route path="/dashboard">
              <Dashboard/>
            </Route>
            <Route path="/">
              <Home></Home>
            </Route>
          </Switch>
        }
      </div>
    </Router>
  );
}

function Home() {
  return (
    <>
      <h1>Home!</h1>
      <a href="http://localhost:3000/login">Login</a>
      {/* <a href="http://localhost:3000/add-google-account">Add Google Account</a> */}
    </> 
  )
}

export default App;
