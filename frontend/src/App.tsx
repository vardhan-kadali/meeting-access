import { useState, useEffect, useRef } from 'react'

interface HealthResponse {
  status: string
  service: string
  version: string
  timestamp: string
  python_version: string
  configured_gemini_model: string
  api_key_configured: boolean
  max_upload_size_mb?: number
  max_page_count?: number
}

interface FindingItem {
  category: string
  category_label: string
  status: 'found' | 'unclear' | 'not_found_in_document' | 'not_applicable'
  quote?: string | null
  page_number?: number | null
  is_quote_verified: boolean
  verification_notes?: string | null
  explanation: string
  suggested_action: string
}

interface DocumentAnalysisResponse {
  filename: string
  total_pages: number
  extraction_status: string
  model_used: string
  analyzed_at: string
  findings: FindingItem[]
  verified_evidence_count: number
  missing_evidence_count: number
  unclear_evidence_count: number
  ocr_warning?: string | null
}

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false)
  const [analysisResult, setAnalysisResult] = useState<DocumentAnalysisResponse | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<'all' | 'found' | 'unclear' | 'not_found_in_document'>('all')

  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    fetch('/api/health')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data) setHealth(data)
      })
      .catch(() => {})
  }, [])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      setSelectedFile(file)
      setAnalysisResult(null)
      setErrorMessage(null)
    }
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      setSelectedFile(file)
      setAnalysisResult(null)
      setErrorMessage(null)
    }
  }

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
  }

  const handleAnalyze = async () => {
    if (!selectedFile) return

    setIsAnalyzing(true)
    setErrorMessage(null)
    setAnalysisResult(null)

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await fetch('/api/documents/analyze', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || `Analysis failed with status ${response.status}`)
      }

      setAnalysisResult(data)
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message)
      } else {
        setErrorMessage('An unexpected error occurred during document analysis.')
      }
    } finally {
      setIsAnalyzing(false)
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }

  const renderStatusBadge = (status: string) => {
    switch (status) {
      case 'found':
        return (
          <span style={{
            backgroundColor: '#dcfce7',
            color: '#15803d',
            border: '1px solid #86efac',
            padding: '0.2rem 0.6rem',
            borderRadius: '9999px',
            fontSize: '0.8rem',
            fontWeight: 700
          }}>
            FOUND
          </span>
        )
      case 'unclear':
        return (
          <span style={{
            backgroundColor: '#fef3c7',
            color: '#b45309',
            border: '1px solid #fcd34d',
            padding: '0.2rem 0.6rem',
            borderRadius: '9999px',
            fontSize: '0.8rem',
            fontWeight: 700
          }}>
            UNCLEAR
          </span>
        )
      case 'not_found_in_document':
        return (
          <span style={{
            backgroundColor: '#f1f5f9',
            color: '#475569',
            border: '1px solid #cbd5e1',
            padding: '0.2rem 0.6rem',
            borderRadius: '9999px',
            fontSize: '0.8rem',
            fontWeight: 700
          }}>
            NOT FOUND IN DOCUMENT
          </span>
        )
      case 'not_applicable':
        return (
          <span style={{
            backgroundColor: '#f8fafc',
            color: '#94a3b8',
            border: '1px solid #e2e8f0',
            padding: '0.2rem 0.6rem',
            borderRadius: '9999px',
            fontSize: '0.8rem',
            fontWeight: 700
          }}>
            NOT APPLICABLE
          </span>
        )
      default:
        return <span>{status}</span>
    }
  }

  const filteredFindings = analysisResult
    ? analysisResult.findings.filter((f) => {
        if (statusFilter === 'all') return true
        return f.status === statusFilter
      })
    : []

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f8fafc',
      color: '#0f172a',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
      padding: '2rem 1rem',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center'
    }}>
      {/* Header */}
      <header style={{
        maxWidth: '960px',
        width: '100%',
        marginBottom: '2rem',
        textAlign: 'center'
      }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.5rem',
          backgroundColor: '#0f172a',
          color: '#ffffff',
          padding: '0.35rem 0.85rem',
          borderRadius: '9999px',
          fontSize: '0.8rem',
          fontWeight: 600,
          letterSpacing: '0.05em',
          marginBottom: '1rem',
          textTransform: 'uppercase'
        }}>
          <span>Civic Accessibility Intelligence</span>
          <span>&bull;</span>
          <span>Milestone 3: Evidence Analysis</span>
        </div>

        <h1 style={{
          fontSize: '2.5rem',
          fontWeight: 800,
          color: '#0f172a',
          margin: '0 0 0.5rem 0',
          letterSpacing: '-0.025em'
        }}>
          MEETING ACCESS
        </h1>
        <p style={{
          fontSize: '1.25rem',
          color: '#475569',
          margin: 0,
          fontWeight: 400
        }}>
          Know if you can participate before the meeting begins.
        </p>

        {health && (
          <div style={{
            marginTop: '1rem',
            fontSize: '0.85rem',
            color: '#64748b',
            display: 'inline-flex',
            gap: '1rem',
            backgroundColor: '#ffffff',
            padding: '0.4rem 1rem',
            borderRadius: '0.5rem',
            border: '1px solid #e2e8f0'
          }}>
            <span>API: <strong>Active</strong></span>
            <span>Model: <strong>{health.configured_gemini_model}</strong></span>
            <span>Key: <strong>{health.api_key_configured ? 'Verified' : 'Pending'}</strong></span>
          </div>
        )}
      </header>

      {/* Main Content Area */}
      <main style={{
        maxWidth: '960px',
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.5rem'
      }}>
        {/* Document Ingestion & Analysis Card */}
        <section aria-labelledby="upload-heading" style={{
          backgroundColor: '#ffffff',
          border: '1px solid #e2e8f0',
          borderRadius: '0.75rem',
          padding: '2rem',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)'
        }}>
          <h2 id="upload-heading" style={{
            fontSize: '1.3rem',
            fontWeight: 700,
            color: '#0f172a',
            margin: '0 0 0.5rem 0'
          }}>
            Analyze Public Meeting Agenda
          </h2>
          <p style={{ fontSize: '0.95rem', color: '#64748b', margin: '0 0 1.5rem 0' }}>
            Upload a California public meeting agenda (PDF). The system extracts and verifies disability accommodations, deadlines, ASL, CART captions, and participation instructions with verbatim page citations.
          </p>

          {/* Accessible Dropzone */}
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onClick={() => fileInputRef.current?.click()}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault()
                fileInputRef.current?.click()
              }
            }}
            tabIndex={0}
            role="button"
            aria-label="Upload agenda PDF document for participation analysis"
            style={{
              border: '2px dashed #94a3b8',
              borderRadius: '0.5rem',
              padding: '2.5rem 1.5rem',
              textAlign: 'center',
              backgroundColor: '#f8fafc',
              cursor: 'pointer',
              outline: 'none'
            }}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept="application/pdf,.pdf"
              style={{ display: 'none' }}
            />
            <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>📄</div>
            <div style={{ fontSize: '1.05rem', fontWeight: 600, color: '#1e293b', marginBottom: '0.25rem' }}>
              Click to select or drag and drop agenda PDF
            </div>
            <div style={{ fontSize: '0.85rem', color: '#64748b' }}>
              Standard California public meeting agendas &bull; Ephemeral in-memory analysis
            </div>
          </div>

          {/* File Selected State */}
          {selectedFile && (
            <div style={{
              marginTop: '1.25rem',
              padding: '1rem',
              backgroundColor: '#f1f5f9',
              borderRadius: '0.5rem',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '0.75rem'
            }}>
              <div>
                <div style={{ fontWeight: 600, color: '#0f172a', fontSize: '0.95rem' }}>
                  {selectedFile.name}
                </div>
                <div style={{ fontSize: '0.85rem', color: '#64748b' }}>
                  {formatFileSize(selectedFile.size)} &bull; Ready for Participation Analysis
                </div>
              </div>

              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button
                  onClick={handleAnalyze}
                  disabled={isAnalyzing}
                  style={{
                    backgroundColor: '#1e3a8a',
                    color: '#ffffff',
                    border: 'none',
                    padding: '0.65rem 1.35rem',
                    borderRadius: '0.375rem',
                    fontWeight: 600,
                    fontSize: '0.95rem',
                    cursor: isAnalyzing ? 'not-allowed' : 'pointer',
                    opacity: isAnalyzing ? 0.7 : 1
                  }}
                >
                  {isAnalyzing ? 'Analyzing Agenda...' : 'Analyze Participation Readiness'}
                </button>
                <button
                  onClick={() => {
                    setSelectedFile(null)
                    setAnalysisResult(null)
                    setErrorMessage(null)
                  }}
                  disabled={isAnalyzing}
                  style={{
                    backgroundColor: '#ffffff',
                    color: '#64748b',
                    border: '1px solid #cbd5e1',
                    padding: '0.65rem 0.9rem',
                    borderRadius: '0.375rem',
                    fontWeight: 600,
                    fontSize: '0.95rem',
                    cursor: isAnalyzing ? 'not-allowed' : 'pointer'
                  }}
                >
                  Clear
                </button>
              </div>
            </div>
          )}

          {/* Loading Indicator */}
          {isAnalyzing && (
            <div
              role="status"
              aria-live="polite"
              style={{
                marginTop: '1.5rem',
                padding: '1.5rem',
                backgroundColor: '#eff6ff',
                border: '1px solid #bfdbfe',
                borderRadius: '0.5rem',
                textAlign: 'center'
              }}
            >
              <div style={{ fontWeight: 700, color: '#1e40af', fontSize: '1.05rem', marginBottom: '0.5rem' }}>
                Analyzing Public Meeting Participation Instructions...
              </div>
              <div style={{ fontSize: '0.9rem', color: '#3b82f6' }}>
                Extracting verbatim evidence, verifying page numbers, and distinguishing accommodation deadlines.
              </div>
            </div>
          )}

          {/* Error Banner */}
          {errorMessage && (
            <div
              role="alert"
              style={{
                marginTop: '1.5rem',
                padding: '1.25rem',
                backgroundColor: '#fef2f2',
                border: '1px solid #fecaca',
                borderRadius: '0.5rem',
                color: '#991b1b'
              }}
            >
              <div style={{ fontWeight: 700, marginBottom: '0.25rem' }}>
                Analysis Request Failed:
              </div>
              <div style={{ fontSize: '0.95rem' }}>{errorMessage}</div>
            </div>
          )}
        </section>

        {/* Participation Readiness Report Section */}
        {analysisResult && (
          <section aria-labelledby="report-heading" style={{
            backgroundColor: '#ffffff',
            border: '1px solid #e2e8f0',
            borderRadius: '0.75rem',
            padding: '2rem',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)'
          }}>
            {/* Report Header */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-start',
              flexWrap: 'wrap',
              gap: '1rem',
              marginBottom: '1.5rem',
              borderBottom: '1px solid #e2e8f0',
              paddingBottom: '1.25rem'
            }}>
              <div>
                <h2 id="report-heading" style={{
                  fontSize: '1.4rem',
                  fontWeight: 800,
                  color: '#0f172a',
                  margin: '0 0 0.35rem 0'
                }}>
                  Participation Readiness Report
                </h2>
                <div style={{ fontSize: '0.9rem', color: '#64748b' }}>
                  Document: <strong>{analysisResult.filename}</strong> &bull; Total Pages: <strong>{analysisResult.total_pages}</strong> &bull; Engine: <strong>{analysisResult.model_used}</strong>
                </div>
              </div>

              <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                Analyzed: {new Date(analysisResult.analyzed_at).toLocaleTimeString()}
              </div>
            </div>

            {/* OCR Advisory If Present */}
            {analysisResult.ocr_warning && (
              <div style={{
                backgroundColor: '#fffbeb',
                border: '1px solid #fde68a',
                borderRadius: '0.5rem',
                padding: '1rem',
                color: '#92400e',
                fontSize: '0.9rem',
                marginBottom: '1.5rem'
              }}>
                <strong>Notice:</strong> {analysisResult.ocr_warning}
              </div>
            )}

            {/* Scorecard Metric Grid (NO numerical score) */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '1rem',
              marginBottom: '1.75rem'
            }}>
              <div style={{
                backgroundColor: '#f0fdf4',
                border: '1px solid #bbf7d0',
                borderRadius: '0.5rem',
                padding: '1rem'
              }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#166534', textTransform: 'uppercase' }}>
                  Verified Evidence
                </div>
                <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#15803d', marginTop: '0.25rem' }}>
                  {analysisResult.verified_evidence_count} Items
                </div>
                <div style={{ fontSize: '0.8rem', color: '#166534', marginTop: '0.25rem' }}>
                  Verbatim quotes matched to physical pages
                </div>
              </div>

              <div style={{
                backgroundColor: '#f8fafc',
                border: '1px solid #e2e8f0',
                borderRadius: '0.5rem',
                padding: '1rem'
              }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#475569', textTransform: 'uppercase' }}>
                  Not Found In Agenda
                </div>
                <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#334155', marginTop: '0.25rem' }}>
                  {analysisResult.missing_evidence_count} Items
                </div>
                <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.25rem' }}>
                  Information absent from uploaded text
                </div>
              </div>

              <div style={{
                backgroundColor: '#fffbeb',
                border: '1px solid #fde68a',
                borderRadius: '0.5rem',
                padding: '1rem'
              }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#92400e', textTransform: 'uppercase' }}>
                  Unclear / Ambiguous
                </div>
                <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#b45309', marginTop: '0.25rem' }}>
                  {analysisResult.unclear_evidence_count} Items
                </div>
                <div style={{ fontSize: '0.8rem', color: '#92400e', marginTop: '0.25rem' }}>
                  Needs clarification from meeting clerk
                </div>
              </div>
            </div>

            {/* Filter Tabs */}
            <div style={{
              display: 'flex',
              gap: '0.5rem',
              marginBottom: '1.25rem',
              flexWrap: 'wrap'
            }}>
              <button
                onClick={() => setStatusFilter('all')}
                style={{
                  padding: '0.4rem 0.85rem',
                  borderRadius: '0.375rem',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  border: '1px solid #cbd5e1',
                  backgroundColor: statusFilter === 'all' ? '#0f172a' : '#ffffff',
                  color: statusFilter === 'all' ? '#ffffff' : '#475569',
                  cursor: 'pointer'
                }}
              >
                All Categories ({analysisResult.findings.length})
              </button>
              <button
                onClick={() => setStatusFilter('found')}
                style={{
                  padding: '0.4rem 0.85rem',
                  borderRadius: '0.375rem',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  border: '1px solid #86efac',
                  backgroundColor: statusFilter === 'found' ? '#15803d' : '#f0fdf4',
                  color: statusFilter === 'found' ? '#ffffff' : '#166534',
                  cursor: 'pointer'
                }}
              >
                Found ({analysisResult.findings.filter((f) => f.status === 'found').length})
              </button>
              <button
                onClick={() => setStatusFilter('not_found_in_document')}
                style={{
                  padding: '0.4rem 0.85rem',
                  borderRadius: '0.375rem',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  border: '1px solid #cbd5e1',
                  backgroundColor: statusFilter === 'not_found_in_document' ? '#475569' : '#f1f5f9',
                  color: statusFilter === 'not_found_in_document' ? '#ffffff' : '#334155',
                  cursor: 'pointer'
                }}
              >
                Not Found ({analysisResult.missing_evidence_count})
              </button>
              <button
                onClick={() => setStatusFilter('unclear')}
                style={{
                  padding: '0.4rem 0.85rem',
                  borderRadius: '0.375rem',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  border: '1px solid #fcd34d',
                  backgroundColor: statusFilter === 'unclear' ? '#b45309' : '#fffbeb',
                  color: statusFilter === 'unclear' ? '#ffffff' : '#92400e',
                  cursor: 'pointer'
                }}
              >
                Unclear ({analysisResult.unclear_evidence_count})
              </button>
            </div>

            {/* Findings List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {filteredFindings.map((finding) => (
                <article
                  key={finding.category}
                  style={{
                    border: '1px solid #e2e8f0',
                    borderRadius: '0.5rem',
                    padding: '1.25rem',
                    backgroundColor: '#ffffff'
                  }}
                >
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    flexWrap: 'wrap',
                    gap: '0.5rem',
                    marginBottom: '0.75rem'
                  }}>
                    <h3 style={{
                      fontSize: '1.05rem',
                      fontWeight: 700,
                      color: '#0f172a',
                      margin: 0
                    }}>
                      {finding.category_label}
                    </h3>
                    <div>{renderStatusBadge(finding.status)}</div>
                  </div>

                  {/* Verbatim Evidence Quote Callout */}
                  {finding.quote && (
                    <div style={{
                      backgroundColor: '#f8fafc',
                      borderLeft: finding.is_quote_verified ? '4px solid #16a34a' : '4px solid #f59e0b',
                      padding: '0.85rem 1rem',
                      borderRadius: '0 0.375rem 0.375rem 0',
                      marginBottom: '0.85rem'
                    }}>
                      <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        color: finding.is_quote_verified ? '#15803d' : '#b45309',
                        marginBottom: '0.35rem',
                        textTransform: 'uppercase'
                      }}>
                        <span>
                          {finding.is_quote_verified ? 'Verified Document Citation' : 'Citation Requires Inspection'}
                        </span>
                        {finding.page_number && (
                          <span style={{
                            backgroundColor: finding.is_quote_verified ? '#dcfce7' : '#fef3c7',
                            padding: '0.1rem 0.45rem',
                            borderRadius: '0.25rem'
                          }}>
                            Physical Page {finding.page_number}
                          </span>
                        )}
                      </div>
                      <blockquote style={{
                        margin: 0,
                        fontSize: '0.9rem',
                        fontStyle: 'italic',
                        color: '#1e293b',
                        lineHeight: 1.5
                      }}>
                        "{finding.quote}"
                      </blockquote>
                      {finding.verification_notes && (
                        <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.4rem' }}>
                          Note: {finding.verification_notes}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Plain Language Explanation */}
                  <div style={{ fontSize: '0.92rem', color: '#334155', lineHeight: 1.5, marginBottom: '0.75rem' }}>
                    {finding.explanation}
                  </div>

                  {/* Suggested Next Action */}
                  <div style={{
                    backgroundColor: '#f0f9ff',
                    border: '1px solid #bae6fd',
                    borderRadius: '0.375rem',
                    padding: '0.65rem 0.9rem',
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '0.5rem',
                    fontSize: '0.85rem',
                    color: '#0369a1'
                  }}>
                    <strong style={{ color: '#0284c7' }}>Suggested Action:</strong>
                    <span>{finding.suggested_action}</span>
                  </div>
                </article>
              ))}
            </div>
          </section>
        )}
      </main>

      {/* Footer */}
      <footer style={{
        marginTop: '3rem',
        fontSize: '0.85rem',
        color: '#64748b',
        textAlign: 'center'
      }}>
        MEETING ACCESS &bull; Bridge The Gap Hacks &bull; Civic Accessibility Intelligence &bull; Ralph M. Brown Act &bull; ADA Title II
      </footer>
    </div>
  )
}
