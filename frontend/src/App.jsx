import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import GeneratePage from './pages/GeneratePage'
import PreviewPage from './pages/PreviewPage'

export default function App() {
  return (
    <div className="min-h-screen bg-gray-950">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/generate" element={<GeneratePage />} />
        <Route path="/preview" element={<PreviewPage />} />
      </Routes>
    </div>
  )
}
