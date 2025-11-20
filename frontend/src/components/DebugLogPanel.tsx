/**
 * Debug Log Panel
 * 
 * Shows real-time AI decisions for debugging:
 * - Checklist item completions with reasoning
 * - Client field extractions
 * - Stage transitions
 * - Validation passes/failures
 */

import { useState, useEffect, useRef } from 'react'
import './DebugLogPanel.css'

interface LogEntry {
  timestamp: string
  type: 'checklist' | 'client_field' | 'stage_transition' | 'validation'
  action: string
  details: {
    item?: string
    field?: string
    stage?: string
    confidence?: number
    evidence?: string
    reasoning?: string
    validated?: boolean
    validationReason?: string
  }
  status: 'success' | 'warning' | 'error' | 'info'
}

interface DebugLogPanelProps {
  logs: LogEntry[]
  isVisible: boolean
  onClose: () => void
}

export default function DebugLogPanel({ logs, isVisible, onClose }: DebugLogPanelProps) {
  const [filter, setFilter] = useState<string>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const logsEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Auto-scroll to bottom when new logs arrive
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs])

  if (!isVisible) return null

  const filteredLogs = logs.filter(log => {
    if (filter !== 'all' && log.type !== filter) return false
    if (searchTerm && !JSON.stringify(log).toLowerCase().includes(searchTerm.toLowerCase())) return false
    return true
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return '#10b981'
      case 'warning': return '#f59e0b'
      case 'error': return '#ef4444'
      default: return '#6b7280'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'checklist': return '📋'
      case 'client_field': return '👤'
      case 'stage_transition': return '🔄'
      case 'validation': return '🔍'
      default: return '📝'
    }
  }

  return (
    <div className="debug-log-overlay">
      <div className="debug-log-panel">
        {/* Header */}
        <div className="debug-log-header">
          <h2>🐛 Debug Log</h2>
          <button onClick={onClose} className="close-btn">✕</button>
        </div>

        {/* Filters */}
        <div className="debug-log-filters">
          <div className="filter-buttons">
            <button 
              className={filter === 'all' ? 'active' : ''}
              onClick={() => setFilter('all')}
            >
              All ({logs.length})
            </button>
            <button 
              className={filter === 'checklist' ? 'active' : ''}
              onClick={() => setFilter('checklist')}
            >
              📋 Checklist
            </button>
            <button 
              className={filter === 'client_field' ? 'active' : ''}
              onClick={() => setFilter('client_field')}
            >
              👤 Client
            </button>
            <button 
              className={filter === 'stage_transition' ? 'active' : ''}
              onClick={() => setFilter('stage_transition')}
            >
              🔄 Stages
            </button>
            <button 
              className={filter === 'validation' ? 'active' : ''}
              onClick={() => setFilter('validation')}
            >
              🔍 Validation
            </button>
          </div>

          <input
            type="text"
            placeholder="Search logs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        {/* Logs */}
        <div className="debug-log-content">
          {filteredLogs.length === 0 ? (
            <div className="no-logs">
              <p>No logs yet. Start recording to see AI decisions in real-time.</p>
            </div>
          ) : (
            filteredLogs.map((log, index) => (
              <div 
                key={index} 
                className="log-entry"
                style={{ borderLeftColor: getStatusColor(log.status) }}
              >
                <div className="log-header">
                  <span className="log-icon">{getTypeIcon(log.type)}</span>
                  <span className="log-time">{log.timestamp}</span>
                  <span 
                    className="log-status"
                    style={{ backgroundColor: getStatusColor(log.status) }}
                  >
                    {log.status}
                  </span>
                </div>

                <div className="log-action">{log.action}</div>

                <div className="log-details">
                  {log.details.item && (
                    <div className="detail-row">
                      <strong>Item:</strong> {log.details.item}
                    </div>
                  )}
                  
                  {log.details.field && (
                    <div className="detail-row">
                      <strong>Field:</strong> {log.details.field}
                    </div>
                  )}

                  {log.details.stage && (
                    <div className="detail-row">
                      <strong>Stage:</strong> {log.details.stage}
                    </div>
                  )}

                  {log.details.confidence !== undefined && (
                    <div className="detail-row">
                      <strong>Confidence:</strong> {(log.details.confidence * 100).toFixed(0)}%
                    </div>
                  )}

                  {log.details.evidence && (
                    <div className="detail-row">
                      <strong>Evidence:</strong>
                      <div className="evidence-text">{log.details.evidence}</div>
                    </div>
                  )}

                  {log.details.reasoning && (
                    <div className="detail-row">
                      <strong>Reasoning:</strong>
                      <div className="reasoning-text">{log.details.reasoning}</div>
                    </div>
                  )}

                  {log.details.validated !== undefined && (
                    <div className="detail-row">
                      <strong>Validated:</strong> {log.details.validated ? '✅ Pass' : '❌ Fail'}
                    </div>
                  )}

                  {log.details.validationReason && (
                    <div className="detail-row">
                      <strong>Validation Reason:</strong>
                      <div className="validation-reason">{log.details.validationReason}</div>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          <div ref={logsEndRef} />
        </div>

        {/* Footer */}
        <div className="debug-log-footer">
          <button onClick={() => {/* Clear logs */}} className="clear-btn">
            🗑️ Clear Logs
          </button>
          <button onClick={() => {/* Export logs */}} className="export-btn">
            📥 Export JSON
          </button>
        </div>
      </div>
    </div>
  )
}

