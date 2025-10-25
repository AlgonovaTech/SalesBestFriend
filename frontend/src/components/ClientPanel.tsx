import { useState, useEffect } from 'react'
import './ClientPanel.css'

interface ClientInsight {
  stage: string
  emotion: string
  active_objections: string[]
  interests: string[]
  need: string | null
  engagement: number
  trend: string
}

interface ClientPanelProps {
  coachWs: WebSocket | null
}

const stageEmojis: Record<string, string> = {
  profiling: '🧭',
  presentation: '📊',
  objection: '💬',
  closing: '🤝'
}

const emotionEmojis: Record<string, string> = {
  engaged: '❤️',
  curious: '🤔',
  hesitant: '😐',
  defensive: '🛡️',
  negative: '😔'
}

const trendEmojis: Record<string, string> = {
  up: '↑',
  stable: '→',
  down: '↓'
}

const trendColors: Record<string, string> = {
  up: '#10b981',
  stable: '#f59e0b',
  down: '#ef4444'
}

function ClientPanel({ coachWs }: ClientPanelProps) {
  const [insight, setInsight] = useState<ClientInsight | null>(null)

  useEffect(() => {
    if (!coachWs) return

    const handleMessage = (e: MessageEvent) => {
      try {
        const data = JSON.parse(e.data)
        if (data.client_insight) {
          setInsight(data.client_insight)
          console.log('📊 Client Insight updated:', data.client_insight)
        }
      } catch (err) {
        console.error('Error parsing client insight:', err)
      }
    }

    coachWs.addEventListener('message', handleMessage)

    return () => {
      coachWs.removeEventListener('message', handleMessage)
    }
  }, [coachWs])

  const getStageLabel = (stage: string): string => {
    const labels: Record<string, string> = {
      profiling: 'Profiling',
      presentation: 'Presentation',
      objection: 'Objection Handling',
      closing: 'Closing'
    }
    return labels[stage] || stage
  }

  const getEmotionLabel = (emotion: string): string => {
    const labels: Record<string, string> = {
      engaged: 'Engaged',
      curious: 'Curious',
      hesitant: 'Hesitant',
      defensive: 'Defensive',
      negative: 'Negative'
    }
    return labels[emotion] || emotion
  }

  if (!insight) {
    return (
      <div className="client-panel">
        <div className="client-panel-header">
          <h2>🧠 Client Insights</h2>
        </div>
        <div className="client-panel-loading">
          <p>Waiting for conversation data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="client-panel">
      <div className="client-panel-header">
        <h2>🧠 Client Insights</h2>
        <p className="subtitle">Real-time analysis</p>
      </div>

      <div className="insight-section">
        <div className="insight-label">
          {stageEmojis[insight.stage] || '🧭'} Stage
        </div>
        <div className="insight-value stage-value">
          {getStageLabel(insight.stage)}
        </div>
      </div>

      <div className="insight-section">
        <div className="insight-label">
          {emotionEmojis[insight.emotion] || '🤔'} Emotion
        </div>
        <div className="insight-value emotion-value">
          {getEmotionLabel(insight.emotion)}
        </div>
      </div>

      <div className="insight-section">
        <div className="insight-label">💬 Active Objections</div>
        <div className="insight-value">
          {insight.active_objections && insight.active_objections.length > 0 ? (
            <div className="tags">
              {insight.active_objections.map((obj, idx) => (
                <span key={idx} className="tag tag-objection">
                  {obj}
                </span>
              ))}
            </div>
          ) : (
            <span className="empty-value">–</span>
          )}
        </div>
      </div>

      <div className="insight-section">
        <div className="insight-label">🌟 Interests</div>
        <div className="insight-value">
          {insight.interests && insight.interests.length > 0 ? (
            <div className="tags">
              {insight.interests.map((interest, idx) => (
                <span key={idx} className="tag tag-interest">
                  {interest}
                </span>
              ))}
            </div>
          ) : (
            <span className="empty-value">–</span>
          )}
        </div>
      </div>

      <div className="insight-section">
        <div className="insight-label">📘 Detected Need</div>
        <div className="insight-value need-value">
          {insight.need || <span className="empty-value">–</span>}
        </div>
      </div>

      <div className="insight-section">
        <div className="insight-label">📈 Engagement</div>
        <div className="insight-value">
          <div className="engagement-display">
            <span className="engagement-percentage">
              {Math.round(insight.engagement * 100)}%
            </span>
            <span
              className="engagement-trend"
              style={{ color: trendColors[insight.trend] || '#6b7280' }}
            >
              {trendEmojis[insight.trend] || '→'}
            </span>
          </div>
          <div className="engagement-bar">
            <div
              className="engagement-fill"
              style={{
                width: `${insight.engagement * 100}%`,
                backgroundColor:
                  insight.engagement > 0.7
                    ? '#10b981'
                    : insight.engagement > 0.4
                    ? '#f59e0b'
                    : '#ef4444',
              }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default ClientPanel

