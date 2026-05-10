import React, { useState } from 'react'

function App() {
  const [file, setFile] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [showAdvanced, setShowAdvanced] = useState(false)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      if (!['audio/wav', 'audio/mpeg', 'audio/mp3'].includes(selectedFile.type) && !selectedFile.name.endsWith('.wav') && !selectedFile.name.endsWith('.mp3')) {
        setError('Invalid file type. Please upload .wav or .mp3')
        return
      }
      setFile(selectedFile)
      setError(null)
      setResult(null)
    }
  }

  const analyzeAudio = async () => {
    if (!file) return

    setIsAnalyzing(true)
    setError(null)
    setResult(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()
      if (data.status === 'success') {
        setResult(data.data)
      } else {
        setError(data.message || 'Analysis failed')
      }
    } catch (err) {
      setError('Could not connect to the backend server. Make sure it is running at localhost:8000')
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="container">
      <header className="hero">
        <h1>Deepfake Forensic AI</h1>
        <p>Advanced audio analysis and evidence-based XAI detection system.</p>
      </header>

      <main>
        {/* Uploader Section */}
        <div 
          className="uploader-box glass"
          onClick={() => document.getElementById('audio-upload').click()}
        >
          <input 
            type="file" 
            id="audio-upload" 
            accept=".wav,.mp3" 
            onChange={handleFileChange} 
          />
          <div className="upload-icon">📊</div>
          <h3>{file ? file.name : 'Drop Audio File Here'}</h3>
          <p>{file ? 'Click to change file' : 'Support for .wav and .mp3 (Min 1s)'}</p>
          {file && !isAnalyzing && (
            <button 
              className="btn-toggle" 
              style={{marginTop: '1.5rem', background: 'linear-gradient(to right, #fff, var(--text-muted))', WebkitBackgroundClip: 'text', backgroundClip: 'text', WebkitTextFillColor: 'transparent'}}
              onClick={(e) => {
                e.stopPropagation()
                analyzeAudio()
              }}
            >
              Start Forensic Analysis
            </button>
          )}
        </div>

        {/* Loading State */}
        {isAnalyzing && (
          <div className="loading-container glass">
            <div className="spinner"></div>
            <h3>Analyzing Forensic Markers...</h3>
            <p className="text-muted">Extracting signal metrics and runing ConvNext inference</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="error-msg text-center">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Results Section */}
        {result && (
          <div className="results-grid">
            <div className="main-result-card glass">
              
              {/* STAGE 1: CORE AUDIT */}
              <div className="stage-container">
                <div className="stage-header">
                  <div className="stage-number">1</div>
                  <div className="stage-title">Core Prediction Audit</div>
                </div>
                <div style={{textAlign: 'center', padding: '1rem 0'}}>
                  <div className={`prediction-badge ${result.report.Prediction === 'Fake' ? 'prediction-fake' : 'prediction-real'}`}>
                    {result.report.Prediction} DETECTED
                  </div>
                  <h2>Confidence: {result.report.Confidence.interpretation} ({Math.round(result.report.Confidence.calibrated * 100)}%)</h2>
                  <p className="text-muted" style={{marginTop: '0.5rem'}}>{result.report['Risk Statement']}</p>
                </div>
              </div>

              {/* EXPERT INTERPRETATION (ALIGNMENT) */}
              {result.report['Forensic Alignment'] && (
                <div className="stage-container" style={{borderColor: result.report['Forensic Alignment'].includes('DISCREPANCY') ? 'var(--warning)' : 'var(--border)'}}>
                  <div className="stage-header">
                    <span style={{fontSize: '1.2rem'}}>⚖️</span>
                    <div className="stage-title">Forensic Cross-Check</div>
                  </div>
                  <div style={{padding: '0.5rem 0'}}>
                    <p style={{
                      color: result.report['Forensic Alignment'].includes('DISCREPANCY') ? 'var(--warning)' : 'var(--success)',
                      fontWeight: 600,
                      fontSize: '0.95rem'
                    }}>
                      {result.report['Forensic Alignment']}
                    </p>
                  </div>
                </div>
              )}

              {/* STAGE 2: FORENSIC PULSE */}
              <div className="stage-container">
                <div className="stage-header">
                  <div className="stage-number">2</div>
                  <div className="stage-title">Forensic Evidence Pulse</div>
                </div>
                <div className="evidence-section" style={{marginTop: 0}}>
                  {result.report['Evidence Summary']['Key Indicators'].map((item, idx) => (
                    <div key={idx} className="reason-card">
                      <div className="reason-text">
                        <div className="reason-title">{item.reason}</div>
                        <div className="reason-evidence">{item.evidence}</div>
                      </div>
                      <div className={`severity-badge sev-${item.severity.toLowerCase()}`}>
                        {item.severity}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* STAGE 3: COMPARATIVE DNA */}
              <div className="stage-container">
                <div className="stage-header">
                  <div className="stage-number">3</div>
                  <div className="stage-title">Comparative Pattern DNA</div>
                </div>
                <div className="similarity-section" style={{marginTop: 0}}>
                  <div className="bar-container">
                    <div className="bar-label">
                      <span>Synthetic Pattern Alignment</span>
                      <span>{Math.round(result.report['Similarity Analysis'].fake_similarity * 100)}%</span>
                    </div>
                    <div className="bar-bg">
                      <div className="bar-fill bar-fake" style={{width: `${result.report['Similarity Analysis'].fake_similarity * 100}%`}}></div>
                    </div>
                  </div>
                  <div className="bar-container">
                    <div className="bar-label">
                      <span>Natural Speech Alignment</span>
                      <span>{Math.round(result.report['Similarity Analysis'].real_similarity * 100)}%</span>
                    </div>
                    <div className="bar-bg">
                      <div className="bar-fill bar-real" style={{width: `${result.report['Similarity Analysis'].real_similarity * 100}%`}}></div>
                    </div>
                  </div>
                  <p className="reason-evidence" style={{marginTop: '1rem', textAlign: 'center'}}>
                    Decision: {result.report['Similarity Analysis'].decision} ({result.report['Similarity Analysis'].strength} strength)
                  </p>
                </div>
              </div>

              {/* Advanced Toggle */}
              <div className="advanced-toggle">
                <button className="btn-toggle" onClick={() => setShowAdvanced(!showAdvanced)}>
                  {showAdvanced ? 'Hide Advanced Forensic View' : 'Show Advanced Forensic View'}
                </button>
                
                {showAdvanced && (
                  <div className="advanced-content">
                    <div className="heatmap-container">
                      <div className="heatmap-card glass">
                        <div className="evidence-header">Attention Heatmap (Grad-CAM)</div>
                        <p className="reason-evidence">Visualizes areas of high neural network activation in the Mel-spectrogram.</p>
                        {result.heatmap ? (
                          <img src={`data:image/png;base64,${result.heatmap}`} className="heatmap-img" alt="Grad-CAM Heatmap" />
                        ) : (
                          <div className="error-msg" style={{marginTop: '1rem'}}>Heatmap generation unavailable for this sample.</div>
                        )}
                      </div>
                      <div className="heatmap-card glass">
                        <div className="evidence-header">Model Focus & Metadata</div>
                        <div className="reason-card" style={{display: 'block', textAlign: 'left'}}>
                           <div className="reason-title">Primary Frequency Region</div>
                           <div className="reason-evidence">Bin: {result.report['Model Focus'].frequency_region}</div>
                        </div>
                        <div className="reason-card" style={{display: 'block', textAlign: 'left'}}>
                           <div className="reason-title">Decision Justification</div>
                           <ul className="reason-evidence" style={{paddingLeft: '1.2rem', marginTop: '0.5rem'}}>
                             {result.report['Decision Justification'].map((j, i) => <li key={i}>{j}</li>)}
                           </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>
      
      <footer style={{marginTop: '4rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem'}}>
        <p>© 2026 Forensic AI Project — Built for Explainable Deepfake Detection</p>
      </footer>
    </div>
  )
}

export default App
