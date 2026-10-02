import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import LandingPage from './pages/LandingPage'
import UploadPage from './pages/UploadPage'
import AnalysisPage from './pages/AnalysisPage'
import DashboardPage from './pages/DashboardPage'
import RecommendationsPage from './pages/RecommendationsPage'
import SkillsPage from './pages/SkillsPage'
import ImprovementsPage from './pages/ImprovementsPage'
import JobExplorerPage from './pages/JobExplorerPage'
import SkillGapPage from './pages/SkillGapPage'

function App() {
  return (
    <div className="flex flex-col min-h-screen bg-slate-50">
      <Navbar />
      <main className="flex-grow">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/jobs" element={<JobExplorerPage />} />
          <Route path="/analysis/:fileId" element={<AnalysisPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/dashboard/:fileId" element={<DashboardPage />} />
          <Route path="/recommendations/:fileId" element={<RecommendationsPage />} />
          <Route path="/skill-gap/:fileId/:jobId" element={<SkillGapPage />} />
          <Route path="/skills/:fileId" element={<SkillsPage />} />
          <Route path="/improvements/:fileId" element={<ImprovementsPage />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}

export default App
