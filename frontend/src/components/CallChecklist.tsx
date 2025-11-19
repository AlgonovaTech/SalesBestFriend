import { useEffect, useState } from 'react'
import './CallChecklist.css'

interface CallChecklistProps {
  coachWs: WebSocket | null
}

interface ChecklistItem {
  id: string
  text: string
  completed: boolean
  evidence?: string
}

interface ChecklistStage {
  name: string
  items: ChecklistItem[]
  isActive: boolean
}

interface ChecklistData {
  greeting: ChecklistStage
  discovery: ChecklistStage
  presentation: ChecklistStage
  objections: ChecklistStage
  closing: ChecklistStage
}

interface ModalState {
  isOpen: boolean
  itemId: string | null
  itemText: string | null
  evidence: string | null
}

export default function CallChecklist({ coachWs }: CallChecklistProps) {
  const [checklist, setChecklist] = useState<ChecklistData>({
    greeting: {
      name: 'Greeting & Rapport',
      isActive: true,
      items: [
        { id: 'intro_yourself', text: 'Introduce yourself and company', completed: false },
        { id: 'ask_availability', text: 'Check if they have time for the call', completed: false },
        { id: 'set_agenda', text: 'Set agenda and expectations', completed: false },
        { id: 'build_rapport', text: 'Build initial rapport (small talk)', completed: false },
      ]
    },
    discovery: {
      name: 'Discovery & Profiling',
      isActive: false,
      items: [
        { id: 'current_situation', text: 'Understand current situation', completed: false },
        { id: 'pain_points', text: 'Identify pain points and challenges', completed: false },
        { id: 'goals', text: 'Discover goals and desired outcomes', completed: false },
        { id: 'decision_process', text: 'Understand decision-making process', completed: false },
        { id: 'budget_timeline', text: 'Qualify budget and timeline', completed: false },
        { id: 'stakeholders', text: 'Identify all stakeholders', completed: false },
      ]
    },
    presentation: {
      name: 'Solution Presentation',
      isActive: false,
      items: [
        { id: 'tailor_solution', text: 'Tailor solution to their needs', completed: false },
        { id: 'demo_key_features', text: 'Demo key features relevant to pain points', completed: false },
        { id: 'show_value', text: 'Show clear value and ROI', completed: false },
        { id: 'provide_examples', text: 'Provide case studies/examples', completed: false },
        { id: 'check_understanding', text: 'Check understanding and engagement', completed: false },
      ]
    },
    objections: {
      name: 'Objection Handling',
      isActive: false,
      items: [
        { id: 'address_price', text: 'Address price concerns', completed: false },
        { id: 'address_time', text: 'Address time/implementation concerns', completed: false },
        { id: 'address_competition', text: 'Differentiate from competitors', completed: false },
        { id: 'address_risks', text: 'Address perceived risks', completed: false },
        { id: 'confirm_resolution', text: 'Confirm objection is resolved', completed: false },
      ]
    },
    closing: {
      name: 'Closing & Next Steps',
      isActive: false,
      items: [
        { id: 'summary', text: 'Summarize key benefits and fit', completed: false },
        { id: 'ask_for_commitment', text: 'Ask for commitment or next step', completed: false },
        { id: 'schedule_followup', text: 'Schedule specific follow-up action', completed: false },
        { id: 'send_materials', text: 'Confirm materials to send', completed: false },
        { id: 'thank_them', text: 'Thank them for their time', completed: false },
      ]
    }
  })

  const [modal, setModal] = useState<ModalState>({
    isOpen: false,
    itemId: null,
    itemText: null,
    evidence: null
  })

  useEffect(() => {
    if (!coachWs) return

    const handleMessage = (e: MessageEvent) => {
      try {
        const data = JSON.parse(e.data)
        
        if (data.current_stage || data.checklist_progress) {
          setChecklist(prev => {
            const newChecklist = { ...prev }
            
            // Update active stage
            if (data.current_stage) {
              Object.keys(newChecklist).forEach(stage => {
                newChecklist[stage as keyof ChecklistData].isActive = stage === data.current_stage
              })
            }
            
            // Update completed items
            if (data.checklist_progress) {
              Object.entries(data.checklist_progress).forEach(([itemId, completed]) => {
                // Find which stage this item belongs to
                Object.keys(newChecklist).forEach(stageKey => {
                  const stage = newChecklist[stageKey as keyof ChecklistData]
                  const item = stage.items.find(i => i.id === itemId)
                  if (item) {
                    item.completed = completed as boolean
                    // Add evidence if available
                    if (data.checklist_evidence && data.checklist_evidence[itemId]) {
                      item.evidence = data.checklist_evidence[itemId]
                    }
                  }
                })
              })
            }
            
            return newChecklist
          })
        }
      } catch (err) {
        console.error('Error parsing checklist data:', err)
      }
    }

    coachWs.addEventListener('message', handleMessage)

    return () => {
      coachWs.removeEventListener('message', handleMessage)
    }
  }, [coachWs])

  const getStageIcon = (stageKey: string) => {
    const icons: Record<string, string> = {
      greeting: '👋',
      discovery: '🔍',
      presentation: '📊',
      objections: '💬',
      closing: '🤝'
    }
    return icons[stageKey] || '📋'
  }

  const getStageProgress = (stage: ChecklistStage) => {
    const completed = stage.items.filter(item => item.completed).length
    const total = stage.items.length
    return { completed, total, percentage: Math.round((completed / total) * 100) }
  }

  const getTotalProgress = () => {
    let totalCompleted = 0
    let totalItems = 0
    
    Object.values(checklist).forEach(stage => {
      totalCompleted += stage.items.filter((item: any) => item.completed).length
      totalItems += stage.items.length
    })
    
    return { completed: totalCompleted, total: totalItems, percentage: Math.round((totalCompleted / totalItems) * 100) }
  }

  const openDetailsModal = (itemId: string, itemText: string, evidence?: string) => {
    setModal({
      isOpen: true,
      itemId,
      itemText,
      evidence: evidence || 'No evidence available'
    })
  }

  const closeDetailsModal = () => {
    setModal({
      isOpen: false,
      itemId: null,
      itemText: null,
      evidence: null
    })
  }

  const totalProgress = getTotalProgress()

  return (
    <div className="call-checklist">
      <div className="checklist-header">
        <h2 className="checklist-title">Call Progress Checklist</h2>
        <div className="total-progress">
          <span className="progress-text">{totalProgress.completed}/{totalProgress.total}</span>
          <div className="progress-ring">
            <svg width="50" height="50" viewBox="0 0 50 50">
              <circle
                cx="25"
                cy="25"
                r="20"
                fill="none"
                stroke="#e5e7eb"
                strokeWidth="4"
              />
              <circle
                cx="25"
                cy="25"
                r="20"
                fill="none"
                stroke="#10b981"
                strokeWidth="4"
                strokeDasharray={`${2 * Math.PI * 20}`}
                strokeDashoffset={`${2 * Math.PI * 20 * (1 - totalProgress.percentage / 100)}`}
                strokeLinecap="round"
                transform="rotate(-90 25 25)"
                style={{ transition: 'stroke-dashoffset 0.5s ease' }}
              />
            </svg>
            <span className="progress-percentage">{totalProgress.percentage}%</span>
          </div>
        </div>
      </div>

      <div className="checklist-stages">
        {Object.entries(checklist).map(([stageKey, stage]) => {
          const progress = getStageProgress(stage)
          
          return (
            <div 
              key={stageKey}
              className={`checklist-stage ${stage.isActive ? 'active' : ''} ${progress.completed === progress.total ? 'completed' : ''}`}
            >
              <div className="stage-header" onClick={() => {
                // Toggle collapse (можно добавить state для collapsed stages)
              }}>
                <div className="stage-title-wrapper">
                  <span className="stage-icon">{getStageIcon(stageKey)}</span>
                  <h3 className="stage-title">{stage.name}</h3>
                  {stage.isActive && <span className="active-badge">Active</span>}
                </div>
                <div className="stage-progress-bar">
                  <div 
                    className="stage-progress-fill"
                    style={{ width: `${progress.percentage}%` }}
                  />
                </div>
                <span className="stage-progress-text">{progress.completed}/{progress.total}</span>
              </div>

              <ul className="checklist-items">
                {stage.items.map((item: any) => (
                  <li 
                    key={item.id}
                    className={`checklist-item ${item.completed ? 'completed' : ''}`}
                  >
                    <label className="checkbox-label">
                      <input 
                        type="checkbox" 
                        checked={item.completed}
                        readOnly
                        className="checkbox-input"
                      />
                      <span className="checkbox-custom">
                        {item.completed && <span className="checkmark">✓</span>}
                      </span>
                      <span className="item-text">{item.text}</span>
                    </label>
                    {item.completed && item.evidence && (
                      <button 
                        className="details-btn"
                        onClick={() => openDetailsModal(item.id, item.text, item.evidence)}
                        title="View evidence"
                      >
                        📋 Details
                      </button>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )
        })}
      </div>

      {/* Modal for showing evidence */}
      {modal.isOpen && (
        <div className="modal-overlay" onClick={closeDetailsModal}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Evidence for: {modal.itemText}</h3>
              <button className="modal-close" onClick={closeDetailsModal}>✕</button>
            </div>
            <div className="modal-body">
              <p className="evidence-text">{modal.evidence}</p>
            </div>
            <div className="modal-footer">
              <button className="modal-btn" onClick={closeDetailsModal}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

