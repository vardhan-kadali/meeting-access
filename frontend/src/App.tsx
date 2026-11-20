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

interface PageExtractionResult {
  page_number: int
  text: string
  char_count: number
  status: 'text_extracted' | 'low_text' | 'empty_or_image'
}

type int = number

interface DocumentExtractionResponse {
  filename: string
  file_size_bytes: number
  total_pages: number
  overall_status: 'text_extracted' | 'partially_extracted' | 'likely_scanned' | 'no_extractable_text'
  ocr_warning?: string | null
  pages: PageExtractionResult[]
  extracted_at: string
}

export default function App() {
  // Backend health state
  const [health, setHealth] = useState<HealthResponse | null>(null)

  // Document upload & extraction state
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isExtracting, setIsExtracting] = useState<boolean>(false)
  const [extractionResult, setExtractionResult] = useState<DocumentExtractionResponse | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [expandedPages, setExpandedPages] = useState<Record<number, boolean>>({})

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
      setExtractionResult(null)
      setErrorMessage(null)
      setExpandedPages({})
    }
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      setSelectedFile(file)
      setExtractionResult(null)
      setErrorMessage(null)
      setExpandedPages({})
    }
  }

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
  }

  const handleUploadAndExtract = async () => {
    if (!selectedFile) return

    setIsExtracting(true)
    setErrorMessage(null)
    setExtractionResult(null)

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await fetch('/api/documents/extract', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || `Upload failed with status ${response.status}`)
      }

      setExtractionResult(data)
      // Expand first page by default
      if (data.pages && data.pages.length > 0) {
        setExpandedPages({ 1: true })
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message)
      } else {
        setErrorMessage('An unexpected error occurred while uploading the document.')
      }
    } finally {
      setIsExtracting(false)
    }
  }

  const togglePage = (pageNum: number) => {
    setExpandedPages((prev) => ({
      ...prev,
      [pageNum]: !prev[pageNum],
    }))
  }

  const expandAll = () => {
    if (!extractionResult) return
    const allExpanded: Record<number, boolean> = {}
    extractionResult.pages.forEach((p) => {
      allExpanded[p.page_number] = true
    })
    setExpandedPages(allExpanded)
  }

  const collapseAll = () => {
    setExpandedPages({})
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }

  const renderStatusBadge = (status: string) => {
    switch (status) {
      case 'text_extracted':
        return (
          <span style={{
            backgroundColor: '#dcfce7',
            color: '#15803d',
            border: '1px solid #86efac',
            padding: '0.25rem 0.65rem',
            borderRadius: '9999px',
            fontSize: '0.85rem',
            fontWeight: 700
          }}>
            Text Extracted
          </span>
        )
      case 'partially_extracted':
        return (
          <span style={{
            backgroundColor: '#e0f2fe',
            color: '#0369a1',
            border: '1px solid #7dd3fc',
            padding: '0.25rem 0.65rem',
            borderRadius: '9999px',
            fontSize: '0.85rem',
            fontWeight: 700
          }}>
            Partially Extracted
          </span>
        )
      case 'likely_scanned':
        return (
          <span style={{
            backgroundColor: '#fef3c7',
            color: '#b45309',
            border: '1px solid #fcd34d',
            padding: '0.25rem 0.65rem',
            borderRadius: '9999px',
            fontSize: '0.85rem',
            fontWeight: 700
          }}>
            Likely Scanned
          </span>
        )
      case 'no_extractable_text':
        return (
          <span style={{
            backgroundColor: '#f1f5f9',
            color: '#475569',
            border: '1px solid #cbd5e1',
            padding: '0.25rem 0.65rem',
            borderRadius: '9999px',
            fontSize: '0.85rem',
            fontWeight: 700
          }}>
            No Extractable Text
          </span>
        )
      default:
        return <span>{status}</span>
    }
  }

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
        maxWidth: '900px',
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
          <span>Milestone 2: PDF Ingestion Engine</span>
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
            <span>API: <strong>Active (v{health.version})</strong></span>
            <span>Max Upload: <strong>{health.max_upload_size_mb || 15} MB</strong></span>
            <span>Max Pages: <strong>{health.max_page_count || 100}</strong></span>
          </div>
        )}
      </header>

      {/* Main Container */}
      <main style={{
        maxWidth: '900px',
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.5rem'
      }}>
        {/* Upload Card */}
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
            Upload California Meeting Agenda
          </h2>
          <p style={{ fontSize: '0.95rem', color: '#64748b', margin: '0 0 1.5rem 0' }}>
            Upload a public meeting agenda in PDF format to test in-memory text extraction, physical page mapping, and scanned document detection.
          </p>

          {/* Drag & Drop Area */}
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
            aria-label="Upload PDF agenda document"
            style={{
              border: '2px dashed #94a3b8',
              borderRadius: '0.5rem',
              padding: '2.5rem 1.5rem',
              textAlign: 'center',
              backgroundColor: '#f8fafc',
              cursor: 'pointer',
              transition: 'border-color 0.15s ease-in-out',
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
              Standard PDF files up to 15MB &bull; Ephemeral in-memory processing
            </div>
          </div>

          {/* Selected File Details */}
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
                  {formatFileSize(selectedFile.size)} &bull; {selectedFile.type || 'application/pdf'}
                </div>
              </div>

              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button
                  onClick={handleUploadAndExtract}
                  disabled={isExtracting}
                  style={{
                    backgroundColor: '#1e3a8a',
                    color: '#ffffff',
                    border: 'none',
                    padding: '0.6rem 1.25rem',
                    borderRadius: '0.375rem',
                    fontWeight: 600,
                    fontSize: '0.95rem',
                    cursor: isExtracting ? 'not-allowed' : 'pointer',
                    opacity: isExtracting ? 0.7 : 1
                  }}
                >
                  {isExtracting ? 'Extracting Pages...' : 'Extract Text & Pages'}
                </button>
                <button
                  onClick={() => {
                    setSelectedFile(null)
                    setExtractionResult(null)
                    setErrorMessage(null)
                  }}
                  disabled={isExtracting}
                  style={{
                    backgroundColor: '#ffffff',
                    color: '#64748b',
                    border: '1px solid #cbd5e1',
                    padding: '0.6rem 0.9rem',
                    borderRadius: '0.375rem',
                    fontWeight: 600,
                    fontSize: '0.95rem',
                    cursor: isExtracting ? 'not-allowed' : 'pointer'
                  }}
                >
                  Clear
                </button>
              </div>
            </div>
          )}

          {/* Loading Indicator */}
          {isExtracting && (
            <div
              role="status"
              aria-live="polite"
              style={{
                marginTop: '1.5rem',
                padding: '1.25rem',
                backgroundColor: '#eff6ff',
                border: '1px solid #bfdbfe',
                borderRadius: '0.5rem',
                textAlign: 'center'
              }}
            >
              <div style={{ fontWeight: 600, color: '#1e40af', marginBottom: '0.5rem' }}>
                Extracting document pages and calculating text density...
              </div>
              <div style={{ fontSize: '0.85rem', color: '#3b82f6' }}>
                Preserving 1-based physical page indices in memory.
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
                Extraction Rejected or Failed:
              </div>
              <div style={{ fontSize: '0.95rem' }}>{errorMessage}</div>
            </div>
          )}
        </section>

        {/* Extraction Results View */}
        {extractionResult && (
          <section aria-labelledby="results-heading" style={{
            backgroundColor: '#ffffff',
            border: '1px solid #e2e8f0',
            borderRadius: '0.75rem',
            padding: '2rem',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)'
          }}>
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
                <h2 id="results-heading" style={{
                  fontSize: '1.3rem',
                  fontWeight: 700,
                  color: '#0f172a',
                  margin: '0 0 0.35rem 0'
                }}>
                  Document Extraction Report
                </h2>
                <div style={{ fontSize: '0.9rem', color: '#64748b' }}>
                  File: <strong>{extractionResult.filename}</strong> &bull; Size: {formatFileSize(extractionResult.file_size_bytes)} &bull; Total Pages: <strong>{extractionResult.total_pages}</strong>
                </div>
              </div>

              <div>
                {renderStatusBadge(extractionResult.overall_status)}
              </div>
            </div>

            {/* OCR Advisory Banner */}
            {extractionResult.ocr_warning && (
              <div style={{
                backgroundColor: '#fffbeb',
                border: '1px solid #fde68a',
                borderRadius: '0.5rem',
                padding: '1rem',
                color: '#92400e',
                fontSize: '0.9rem',
                marginBottom: '1.5rem'
              }}>
                <strong>Technical Advisory:</strong> {extractionResult.ocr_warning}
              </div>
            )}

            {/* Page Inspector Controls */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '1rem'
            }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#1e293b', margin: 0 }}>
                Physical Pages ({extractionResult.pages.length})
              </h3>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button
                  onClick={expandAll}
                  style={{
                    backgroundColor: '#f1f5f9',
                    border: '1px solid #cbd5e1',
                    borderRadius: '0.25rem',
                    padding: '0.35rem 0.75rem',
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >
                  Expand All
                </button>
                <button
                  onClick={collapseAll}
                  style={{
                    backgroundColor: '#f1f5f9',
                    border: '1px solid #cbd5e1',
                    borderRadius: '0.25rem',
                    padding: '0.35rem 0.75rem',
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >
                  Collapse All
                </button>
              </div>
            </div>

            {/* List of Pages */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {extractionResult.pages.map((p) => {
                const isExpanded = !!expandedPages[p.page_number]
                return (
                  <div
                    key={p.page_number}
                    style={{
                      border: '1px solid #e2e8f0',
                      borderRadius: '0.5rem',
                      overflow: 'hidden'
                    }}
                  >
                    <button
                      onClick={() => togglePage(p.page_number)}
                      aria-expanded={isExpanded}
                      style={{
                        width: '100%',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '0.85rem 1rem',
                        backgroundColor: isExpanded ? '#f8fafc' : '#ffffff',
                        border: 'none',
                        textAlign: 'left',
                        cursor: 'pointer',
                        fontSize: '0.95rem'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <span style={{ fontWeight: 700, color: '#0f172a' }}>
                          Page {p.page_number}
                        </span>
                        <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                          ({p.char_count} chars)
                        </span>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <span style={{
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          padding: '0.15rem 0.5rem',
                          borderRadius: '0.25rem',
                          backgroundColor:
                            p.status === 'text_extracted'
                              ? '#dcfce7'
                              : p.status === 'low_text'
                              ? '#fef3c7'
                              : '#f1f5f9',
                          color:
                            p.status === 'text_extracted'
                              ? '#166534'
                              : p.status === 'low_text'
                              ? '#92400e'
                              : '#475569',
                        }}>
                          {p.status}
                        </span>
                        <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
                          {isExpanded ? '▲' : '▼'}
                        </span>
                      </div>
                    </button>

                    {isExpanded && (
                      <div style={{
                        padding: '1rem',
                        borderTop: '1px solid #e2e8f0',
                        backgroundColor: '#ffffff'
                      }}>
                        {p.text.trim().length > 0 ? (
                          <pre style={{
                            margin: 0,
                            padding: '1rem',
                            backgroundColor: '#f8fafc',
                            borderRadius: '0.375rem',
                            border: '1px solid #e2e8f0',
                            fontSize: '0.85rem',
                            color: '#1e293b',
                            lineHeight: 1.5,
                            whiteSpace: 'pre-wrap',
                            wordBreak: 'break-word',
                            maxHeight: '350px',
                            overflowY: 'auto'
                          }}>
                            {p.text}
                          </pre>
                        ) : (
                          <div style={{
                            padding: '1rem',
                            backgroundColor: '#f8fafc',
                            borderRadius: '0.375rem',
                            color: '#94a3b8',
                            fontStyle: 'italic',
                            fontSize: '0.85rem',
                            textAlign: 'center'
                          }}>
                            No selectable text detected on this page (likely scanned image or blank page).
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )
              })}
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
        MEETING ACCESS &bull; Bridge The Gap Hacks &bull; Civic Accessibility Intelligence
      </footer>
    </div>
  )
}
