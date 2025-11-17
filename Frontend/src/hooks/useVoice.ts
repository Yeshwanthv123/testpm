import { useState, useRef, useCallback } from 'react';
import { VoiceRecording } from '../types';

export const useVoice = () => {
  const [voiceState, setVoiceState] = useState<VoiceRecording>({
    isRecording: false,
    transcript: '',
    confidence: 0
  });
  
  const recognitionRef = useRef<any>(null);
  // Buffer refs to reduce frequent state updates from interim speech results
  const finalTranscriptRef = useRef<string>('');
  const pendingTranscriptRef = useRef<string>('');
  const updateTimerRef = useRef<number | null>(null);

  const startRecording = useCallback(() => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Speech recognition not supported in this browser');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognitionRef.current = new SpeechRecognition();
    
    recognitionRef.current.continuous = true;
    recognitionRef.current.interimResults = true;
    recognitionRef.current.lang = 'en-US';
    recognitionRef.current.maxAlternatives = 1;

    recognitionRef.current.onstart = () => {
      setVoiceState(prev => ({ ...prev, isRecording: true }));
    };

  recognitionRef.current.onresult = (event: any) => {
      let finalTranscript = '';
      let interimTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }

      // Append final transcript to the final buffer
      if (finalTranscript) {
        finalTranscriptRef.current = (finalTranscriptRef.current || '') + finalTranscript;
      }

      // Build the pending full transcript (final + interim)
      pendingTranscriptRef.current = (finalTranscriptRef.current || '') + interimTranscript;

      // Update state immediately with transcript for real-time display
      setVoiceState(prev => ({
        ...prev,
        transcript: pendingTranscriptRef.current,
        confidence: event.results[event.results.length - 1][0].confidence || 0
      }));
    };

  recognitionRef.current.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setVoiceState(prev => ({ ...prev, isRecording: false }));
    };

    recognitionRef.current.onend = () => {
      // Don't automatically set isRecording to false on silence
      // Only stop if explicitly told to stop
      if (recognitionRef.current && !recognitionRef.current.shouldStop) {
        try {
          recognitionRef.current.start();
        } catch (e) {
          console.log('Already started or error restarting recognition');
        }
      } else {
        setVoiceState(prev => ({ ...prev, isRecording: false }));
      }
    };

    recognitionRef.current.start();
  }, []);

  const stopRecording = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.shouldStop = true;
      recognitionRef.current.stop();
    }
    setVoiceState(prev => ({ ...prev, isRecording: false }));
  }, []);

  const speakText = useCallback((text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1;
      utterance.volume = 0.8;
      
      // Try to use a more natural voice
      const voices = speechSynthesis.getVoices();
      const preferredVoice = voices.find(voice => 
        voice.name.includes('Google') || 
        voice.name.includes('Microsoft') ||
        voice.lang.startsWith('en')
      );
      
      if (preferredVoice) {
        utterance.voice = preferredVoice;
      }
      
      speechSynthesis.speak(utterance);
    }
  }, []);

  const clearTranscript = useCallback(() => {
    // Reset all transcript buffers completely
    finalTranscriptRef.current = '';
    pendingTranscriptRef.current = '';
    if (updateTimerRef.current) {
      window.clearTimeout(updateTimerRef.current as any);
      updateTimerRef.current = null;
    }
    // Reset voice state with empty transcript
    setVoiceState(prev => ({ ...prev, transcript: '', confidence: 0 }));
  }, []);

  return {
    voiceState,
    startRecording,
    stopRecording,
    speakText,
    clearTranscript,
    isSupported: 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window
  };
};

// Extend Window interface for TypeScript
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}