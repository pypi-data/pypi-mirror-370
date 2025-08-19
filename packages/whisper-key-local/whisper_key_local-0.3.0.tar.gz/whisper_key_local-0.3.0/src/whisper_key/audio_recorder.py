import logging
import threading
import time
from typing import Optional

import numpy as np
import sounddevice as sd

class AudioRecorder:
    WHISPER_SAMPLE_RATE = 16000
    THREAD_JOIN_TIMEOUT = 2.0
    RECORDING_SLEEP_INTERVAL = 100
    STREAM_DTYPE = np.float32
       
    def __init__(self, 
                 channels: int = 1,
                 dtype: str = "float32", 
                 max_duration: int = 30,
                 on_max_duration_reached: callable = None):
        
        self.sample_rate = self.WHISPER_SAMPLE_RATE
        self.channels = channels
        self.dtype = dtype
        self.max_duration = max_duration
        self.on_max_duration_reached = on_max_duration_reached
        self.is_recording = False
        self.audio_data = []
        self.recording_thread = None
        self.recording_start_time = None
        self.logger = logging.getLogger(__name__)
        
        self._test_microphone()
    
    def _wait_for_thread_finish(self):
        if self.recording_thread:
            self.recording_thread.join(timeout=self.THREAD_JOIN_TIMEOUT)
    
    def _test_microphone(self):
        try:
            default_input = sd.query_devices(kind='input')
            self.logger.info(f"Default microphone: {default_input['name']}")

        except Exception as e:
            self.logger.error(f"Microphone test failed: {e}")
            raise
    
    def start_recording(self):
        if self.is_recording:
            return False
        
        try:
            self.logger.info("Starting audio recording...")
            self.is_recording = True
            self.audio_data = []
            self.recording_start_time = time.time()
            
            self.recording_thread = threading.Thread(target=self._record_audio)
            self.recording_thread.daemon = True  # Thread will close when main program closes
            self.recording_thread.start()
            
            print("🎤 Recording started! Speak now...")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start audio recording: {e}")
            print("❌ Failed to start recording!")
            self.is_recording = False
            return False
    
    def stop_recording(self) -> Optional[np.ndarray]:
        if not self.is_recording:
            return None
        
        self.is_recording = False
        self._wait_for_thread_finish()
        
        return self._process_audio_data()
    
    def _process_audio_data(self) -> Optional[np.ndarray]:
        if len(self.audio_data) == 0:
            print("   ✗ No audio data recorded!")
            return None
        
        # Convert list of audio chunks into a single numpy array
        audio_array = np.concatenate(self.audio_data, axis=0)
        duration = self.get_audio_duration(audio_array)
        self.logger.info(f"Recorded {duration:.2f} seconds of audio")
        return audio_array
    
    def cancel_recording(self):
        if not self.is_recording:
            return
        
        self.is_recording = False
        self._wait_for_thread_finish()
        
        self.audio_data = []
        self.recording_start_time = None
    
    def _record_audio(self):
        try:
            def audio_callback(audio_data, frames, time, status):                
                if self.is_recording:
                    self.audio_data.append(audio_data.copy())

                if status:
                    self.logger.debug(f"Audio callback status: {status}")
            
            with sd.InputStream(samplerate=self.sample_rate,
                                channels=self.channels,
                                callback=audio_callback,
                                dtype=self.STREAM_DTYPE):
                
                while self.is_recording:
                    if self._check_max_duration_exceeded():
                        break
                    
                    sd.sleep(self.RECORDING_SLEEP_INTERVAL)
                
        except Exception as e:
            self.logger.error(f"Error during audio recording: {e}")
            self.is_recording = False
    
    def _check_max_duration_exceeded(self) -> bool:
        if self.max_duration > 0 and self.recording_start_time:
            elapsed_time = time.time() - self.recording_start_time
            if elapsed_time >= self.max_duration:
                self.logger.info(f"Maximum recording duration of {self.max_duration}s reached")
                print(f"⏰ Maximum recording duration of {self.max_duration}s reached - stopping recording")
                
                self.is_recording = False
                audio_data = self._process_audio_data()
                
                if self.on_max_duration_reached:
                    self.on_max_duration_reached(audio_data)
                return True
        return False
    
    def get_recording_status(self) -> bool:
        return self.is_recording
    
    def get_audio_duration(self, audio_data: np.ndarray) -> float:
        if audio_data is None or len(audio_data) == 0:
            return 0.0
        return len(audio_data) / self.sample_rate