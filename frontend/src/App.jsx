// -*- mode: js-jsx-mode; lexical-binding: t; -*-
import './App.css';
import './BooksList.jsx';
import BooksList from './BooksList.jsx';

function App() {
  return (
  <div>
    <h1>Bücherverwaltung</h1>
    <BooksList />
  </div>);
}

export default App;
