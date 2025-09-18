import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard/Dashboard';
import Rules from './pages/Rules/Rules';
import Validation from './pages/Validation/Validation';
import Health from './pages/Health/Health';
import { initializeTheme } from './utils/theme';

function App() {
  useEffect(() => {
    initializeTheme();
  }, []);

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="rules" element={<Rules />} />
            <Route path="rules/upload" element={<Rules />} />
            <Route path="validation" element={<Validation />} />
            <Route path="validation/new" element={<Validation />} />
            <Route path="health" element={<Health />} />
          </Route>
        </Routes>

        {/* Toast notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: 'var(--toast-bg)',
              color: 'var(--toast-color)',
            },
            success: {
              style: {
                background: '#10B981',
                color: 'white',
              },
            },
            error: {
              style: {
                background: '#EF4444',
                color: 'white',
              },
            },
          }}
        />
      </div>

      <style>{`
        :root {
          --toast-bg: #ffffff;
          --toast-color: #374151;
        }

        .dark {
          --toast-bg: #1f2937;
          --toast-color: #f3f4f6;
        }
      `}</style>
    </Router>
  );
}

export default App;