import { useEffect, useState } from 'react'
import './ClientInfoSummary.css'

interface ClientInfoSummaryProps {
  coachWs: WebSocket | null
}

interface ClientInfo {
  objections: string[]
  interests: string[]
  needs: string[]
  concerns: string[]
  emotion: string
  engagement: number
}

export default function ClientInfoSummary({ coachWs }: ClientInfoSummaryProps) {
  const [clientInfo, setClientInfo] = useState<ClientInfo>({
    objections: [],
    interests: [],
    needs: [],
    concerns: [],
    emotion: 'neutral',
    engagement: 0.5
  })

  useEffect(() => {
    if (!coachWs) return

    const handleMessage = (e: MessageEvent) => {
      try {
        const data = JSON.parse(e.data)
        
        if (data.client_insight) {
          const insight = data.client_insight
          
          setClientInfo({
            objections: insight.active_objections || [],
            interests: insight.interests || [],
            needs: insight.need ? [insight.need] : [],
            concerns: [], // Can be extracted from objections
            emotion: insight.emotion || 'neutral',
            engagement: insight.engagement || 0.5
          })
        }
      } catch (err) {
        console.error('Error parsing client info:', err)
      }
    }

    coachWs.addEventListener('message', handleMessage)

    return () => {
      coachWs.removeEventListener('message', handleMessage)
    }
  }, [coachWs])

  const getEmotionIcon = (emotion: string) => {
    const icons: Record<string, string> = {
      engaged: '😊',
      curious: '🤔',
      hesitant: '😕',
      defensive: '🛡️',
      negative: '😞',
      neutral: '😐',
      positive: '🙂'
    }
    return icons[emotion] || '😐'
  }

  const getTotalItems = () => {
    return clientInfo.objections.length + 
           clientInfo.interests.length + 
           clientInfo.needs.length
  }

  return (
    <div className="client-info-summary">
      <div className="section-header">
        <h2 className="section-title">Key Client Information</h2>
        <span className="info-count">{getTotalItems()} items</span>
      </div>

      <div className="info-display">
        {/* Objections */}
        <div className="info-block">
          <div className="info-block-header">
            <span className="icon">⚠️</span>
            <span className="block-title">Objections</span>
          </div>
          {clientInfo.objections.length > 0 ? (
            <div className="info-items">
              {clientInfo.objections.map((obj, idx) => (
                <div key={idx} className="info-item objection-item">• {obj}</div>
              ))}
            </div>
          ) : (
            <div className="info-empty">No objections yet</div>
          )}
        </div>

        {/* Interests */}
        <div className="info-block">
          <div className="info-block-header">
            <span className="icon">⭐</span>
            <span className="block-title">Interests</span>
          </div>
          {clientInfo.interests.length > 0 ? (
            <div className="info-items">
              {clientInfo.interests.map((interest, idx) => (
                <div key={idx} className="info-item interest-item">• {interest}</div>
              ))}
            </div>
          ) : (
            <div className="info-empty">No interests detected</div>
          )}
        </div>

        {/* Needs */}
        <div className="info-block">
          <div className="info-block-header">
            <span className="icon">🎯</span>
            <span className="block-title">Needs / Pain Points</span>
          </div>
          {clientInfo.needs.length > 0 ? (
            <div className="info-items">
              {clientInfo.needs.map((need, idx) => (
                <div key={idx} className="info-item need-item">• {need}</div>
              ))}
            </div>
          ) : (
            <div className="info-empty">No needs identified</div>
          )}
        </div>

        {/* Emotion & Engagement */}
        <div className="info-block emotion-block">
          <div className="info-block-header">
            <span className="icon">{getEmotionIcon(clientInfo.emotion)}</span>
            <span className="block-title">Emotional State</span>
          </div>
          <div className="emotion-display">
            <div className="emotion-info">
              <span className="emotion-text">{clientInfo.emotion}</span>
              <span className="engagement-label">Engagement</span>
            </div>
            <div className="engagement-bar">
              <div 
                className="engagement-fill"
                style={{ 
                  width: `${clientInfo.engagement * 100}%`,
                  backgroundColor: clientInfo.engagement > 0.7 ? '#10b981' : clientInfo.engagement > 0.4 ? '#f59e0b' : '#ef4444'
                }}
              />
            </div>
            <span className="engagement-text">
              {Math.round(clientInfo.engagement * 100)}%
            </span>
          </div>
        </div>
      </div>

      {getTotalItems() === 0 && (
        <div className="empty-state">
          <p>🎧 Listening for client information...</p>
        </div>
      )}
    </div>
  )
}

