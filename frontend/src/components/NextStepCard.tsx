import { useEffect, useState } from 'react'
import './NextStepCard.css'

interface NextStepCardProps {
  coachWs: WebSocket | null
}

interface NextStepData {
  recommendation: string
  stage: string
  timestamp?: number
}

export default function NextStepCard({ coachWs }: NextStepCardProps) {
  const [nextStep, setNextStep] = useState<NextStepData>({
    recommendation: 'Waiting for call to start...',
    stage: 'greeting'
  })
  const [used, setUsed] = useState(false)

  useEffect(() => {
    if (!coachWs) return

    const handleMessage = (e: MessageEvent) => {
      try {
        const data = JSON.parse(e.data)
        
        if (data.next_step) {
          setNextStep({
            recommendation: data.next_step,
            stage: data.current_stage || 'discovery',
            timestamp: Date.now()
          })
          // Reset checkbox when recommendation changes
          setUsed(false)
        }
      } catch (err) {
        console.error('Error parsing next step data:', err)
      }
    }

    coachWs.addEventListener('message', handleMessage)

    return () => {
      coachWs.removeEventListener('message', handleMessage)
    }
  }, [coachWs])

  const getStageIcon = (stage: string) => {
    const icons: Record<string, string> = {
      greeting: '👋',
      discovery: '🔍',
      profiling: '📋',
      presentation: '📊',
      objection: '💬',
      objections: '💬',
      closing: '🤝'
    }
    return icons[stage] || '💡'
  }

  const getStageName = (stage: string) => {
    const names: Record<string, string> = {
      greeting: 'Greeting',
      discovery: 'Discovery',
      profiling: 'Profiling',
      presentation: 'Presentation',
      objection: 'Objection Handling',
      objections: 'Objection Handling',
      closing: 'Closing'
    }
    return names[stage] || 'Discovery'
  }

  return (
    <div className="next-step-card">
      <div className="next-step-header">
        <span className="stage-badge">
          {getStageIcon(nextStep.stage)} {getStageName(nextStep.stage)}
        </span>
        <span className="update-indicator">
          <span className="pulse-dot"></span>
          Live
        </span>
      </div>
      
      <h2 className="next-step-title">Next Step Recommendation</h2>
      
      <div className="next-step-content">
        <div className="recommendation-icon">💡</div>
        <p className="recommendation-text">{nextStep.recommendation}</p>
      </div>

      {/* Checkbox for tracking usage */}
      <div className="recommendation-action">
        <label className="checkbox-label">
          <input 
            type="checkbox" 
            checked={used}
            onChange={(e) => setUsed(e.target.checked)}
            className="checkbox-input"
          />
          <span className="checkbox-text">
            {used ? '✅ Used this approach' : '☐ Mark when used'}
          </span>
        </label>
      </div>
    </div>
  )
}

