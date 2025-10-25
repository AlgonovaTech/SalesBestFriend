import { useState } from 'react'
import './DebugPanel.css'

interface DebugPanelProps {
  onTranscriptSubmit: (transcript: string) => void
  onVideoUpload: (file: File) => void
  onYouTubeSubmit: (url: string) => void
}

type TabMode = 'live' | 'transcript' | 'video' | 'youtube'

function DebugPanel({ onTranscriptSubmit, onVideoUpload, onYouTubeSubmit }: DebugPanelProps) {
  const [activeTab, setActiveTab] = useState<TabMode>('live')
  const [transcript, setTranscript] = useState('')
  const [youtubeUrl, setYouTubeUrl] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const handleTranscriptSubmit = () => {
    if (transcript.trim()) {
      onTranscriptSubmit(transcript.trim())
      setTranscript('')
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const handleFileUpload = () => {
    if (selectedFile) {
      onVideoUpload(selectedFile)
      setSelectedFile(null)
    }
  }

  const handleYouTubeSubmit = () => {
    if (youtubeUrl.trim()) {
      onYouTubeSubmit(youtubeUrl.trim())
      setYouTubeUrl('')
    }
  }

  return (
    <div className="debug-panel">
      <div className="debug-header">
        <h3>🔧 Debug Mode</h3>
        <p className="debug-subtitle">Тестирование с разными источниками</p>
      </div>

      <div className="debug-tabs">
        <button
          className={`debug-tab ${activeTab === 'live' ? 'active' : ''}`}
          onClick={() => setActiveTab('live')}
        >
          🎤 Live
        </button>
        <button
          className={`debug-tab ${activeTab === 'transcript' ? 'active' : ''}`}
          onClick={() => setActiveTab('transcript')}
        >
          📝 Text
        </button>
        <button
          className={`debug-tab ${activeTab === 'video' ? 'active' : ''}`}
          onClick={() => setActiveTab('video')}
        >
          🎬 Video
        </button>
        <button
          className={`debug-tab ${activeTab === 'youtube' ? 'active' : ''}`}
          onClick={() => setActiveTab('youtube')}
        >
          📺 YouTube
        </button>
      </div>

      <div className="debug-content">
        {activeTab === 'live' && (
          <div className="debug-mode">
            <p className="mode-description">
              📡 Захват аудио в реальном времени из Google Meet
            </p>
            <p className="mode-hint">
              Используйте кнопку "Начать запись" выше для live recording
            </p>
          </div>
        )}

        {activeTab === 'transcript' && (
          <div className="debug-mode">
            <p className="mode-description">
              📝 Вставьте текст диалога для быстрого тестирования
            </p>
            <textarea
              className="transcript-input"
              placeholder="Пример:&#10;Client: My child is 10 years old and loves Minecraft&#10;Manager: Have you done coding before?&#10;Client: No, but it sounds fun. How much does it cost?&#10;Manager: Our program starts at..."
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              rows={8}
            />
            <button
              className="btn btn-submit"
              onClick={handleTranscriptSubmit}
              disabled={!transcript.trim()}
            >
              ✅ Анализировать текст
            </button>
            <p className="mode-hint">
              💡 Формат: "Client: ..." или "Manager: ..." на каждой строке
            </p>
          </div>
        )}

        {activeTab === 'video' && (
          <div className="debug-mode">
            <p className="mode-description">
              🎬 Загрузите видео со звонка (MP4, MOV, AVI, WebM)
            </p>
            <div className="file-upload-zone">
              <input
                type="file"
                id="video-upload"
                accept="video/*,audio/*"
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />
              <label htmlFor="video-upload" className="file-upload-label">
                {selectedFile ? (
                  <>
                    📁 {selectedFile.name}
                    <br />
                    <span className="file-size">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </span>
                  </>
                ) : (
                  <>
                    📤 Нажмите для выбора файла
                    <br />
                    <span className="file-hint">или перетащите сюда</span>
                  </>
                )}
              </label>
            </div>
            <button
              className="btn btn-submit"
              onClick={handleFileUpload}
              disabled={!selectedFile}
            >
              ✅ Загрузить и обработать
            </button>
            <p className="mode-hint">
              ⚠️ Требует FFmpeg на backend для извлечения аудио
            </p>
          </div>
        )}

        {activeTab === 'youtube' && (
          <div className="debug-mode">
            <p className="mode-description">
              📺 Вставьте ссылку на YouTube видео со звонком
            </p>
            <input
              type="text"
              className="youtube-input"
              placeholder="https://www.youtube.com/watch?v=..."
              value={youtubeUrl}
              onChange={(e) => setYouTubeUrl(e.target.value)}
            />
            <button
              className="btn btn-submit"
              onClick={handleYouTubeSubmit}
              disabled={!youtubeUrl.trim()}
            >
              ✅ Загрузить с YouTube
            </button>
            <p className="mode-hint">
              ⚠️ Требует yt-dlp на backend для скачивания
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default DebugPanel

