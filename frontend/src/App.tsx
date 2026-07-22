import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Findings from './pages/Findings'
import KVStore from './pages/KVStore'
import Scans from './pages/Scans'
import './App.css'

export default function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <nav className="navbar">
          <div className="nav-brand">
            <h1>Guardrails</h1>
          </div>
          <ul className="nav-links">
            <li>
              <Link to="/">Dashboard</Link>
            </li>
            <li>
              <Link to="/findings">Findings</Link>
            </li>
            <li>
              <Link to="/kv">KV Store</Link>
            </li>
            <li>
              <Link to="/scans">Scans</Link>
            </li>
          </ul>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/findings" element={<Findings />} />
            <Route path="/kv" element={<KVStore />} />
            <Route path="/scans" element={<Scans />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
