"""
YouTube video processor
Downloads and transcribes YouTube videos
"""

import os
import tempfile
from typing import Optional, Dict
import yt_dlp
from faster_whisper import WhisperModel


class YouTubeProcessor:
    """Process YouTube videos: download + transcribe"""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize processor
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self._model: Optional[WhisperModel] = None
        
    @property
    def model(self) -> WhisperModel:
        """Lazy load Whisper model"""
        if self._model is None:
            print(f"🔄 Loading Whisper model '{self.model_size}'...")
            self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            print(f"✅ Whisper model loaded")
        return self._model
    
    def download_audio(self, youtube_url: str) -> str:
        """
        Download audio from YouTube video
        
        Args:
            youtube_url: YouTube video URL
            
        Returns:
            Path to downloaded audio file
        """
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        output_template = os.path.join(temp_dir, "audio")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        print(f"📥 Downloading from YouTube: {youtube_url}")
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                
                print(f"✅ Downloaded: {title} ({duration}s)")
                
                # Ищем скачанный файл в temp директории
                import glob
                audio_files = glob.glob(os.path.join(temp_dir, "audio.*"))
                
                if not audio_files:
                    raise Exception(f"No audio file found in {temp_dir}")
                
                output_path = audio_files[0]
                print(f"📁 Audio file: {output_path}")
                
                return output_path
                
        except Exception as e:
            raise Exception(f"Failed to download YouTube video: {str(e)}")
    
    def transcribe_audio(self, audio_path: str, language: str = "id") -> str:
        """
        Transcribe audio file using Whisper
        
        Args:
            audio_path: Path to audio file
            language: Language code (default: "id" for Bahasa Indonesia)
            
        Returns:
            Transcribed text
        """
        print(f"🎤 Transcribing audio: {audio_path} (language: {language})")
        
        try:
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                vad_filter=True,  # Voice Activity Detection
                beam_size=5
            )
            
            # Собираем текст из сегментов
            transcript_lines = []
            for segment in segments:
                text = segment.text.strip()
                if text:
                    transcript_lines.append(text)
            
            transcript = "\n".join(transcript_lines)
            
            print(f"✅ Transcription complete: {len(transcript)} chars, {info.language} detected")
            
            return transcript
            
        except Exception as e:
            raise Exception(f"Failed to transcribe audio: {str(e)}")
    
    def process_youtube_url(self, youtube_url: str, language: str = "id") -> str:
        """
        Complete pipeline: download + transcribe
        
        Args:
            youtube_url: YouTube video URL
            language: Language code for transcription
            
        Returns:
            Transcribed text
        """
        audio_path = None
        
        try:
            # Download
            audio_path = self.download_audio(youtube_url)
            
            # Transcribe with specified language
            transcript = self.transcribe_audio(audio_path, language=language)
            
            return transcript
            
        finally:
            # Cleanup
            if audio_path and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                    print(f"🗑️ Cleaned up: {audio_path}")
                except:
                    pass


# Global instance
_processor: Optional[YouTubeProcessor] = None


def get_processor() -> YouTubeProcessor:
    """Get or create global processor instance"""
    global _processor
    if _processor is None:
        _processor = YouTubeProcessor(model_size="base")
    return _processor


def process_youtube_url(youtube_url: str, language: str = "id") -> str:
    """
    Convenience function to process YouTube URL
    
    Args:
        youtube_url: YouTube video URL
        language: Language code for transcription
        
    Returns:
        Transcribed text
    """
    processor = get_processor()
    return processor.process_youtube_url(youtube_url, language=language)

