import './LanguageSelector.css'

interface LanguageSelectorProps {
  selectedLanguage: string
  onLanguageChange: (language: string) => void
}

const LANGUAGES = [
  { code: 'id', name: 'Bahasa Indonesia', flag: '🇮🇩' },
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'ru', name: 'Русский', flag: '🇷🇺' },
  { code: 'zh', name: '中文', flag: '🇨🇳' },
  { code: 'es', name: 'Español', flag: '🇪🇸' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
  { code: 'ja', name: '日本語', flag: '🇯🇵' },
  { code: 'ko', name: '한국어', flag: '🇰🇷' },
  { code: 'pt', name: 'Português', flag: '🇵🇹' },
]

export default function LanguageSelector({ selectedLanguage, onLanguageChange }: LanguageSelectorProps) {
  return (
    <div className="language-selector">
      <label className="language-label">
        <span className="label-icon">🌍</span>
        <span className="label-text">Transcription Language:</span>
      </label>
      <select 
        className="language-select"
        value={selectedLanguage}
        onChange={(e) => onLanguageChange(e.target.value)}
      >
        {LANGUAGES.map(lang => (
          <option key={lang.code} value={lang.code}>
            {lang.flag} {lang.name}
          </option>
        ))}
      </select>
      <div className="language-hint">
        Choose the language spoken in the call
      </div>
    </div>
  )
}

