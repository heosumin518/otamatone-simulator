import numpy as np
import sounddevice as sd

class SoundPlayer:
    def __init__(self, get_frequency_callback, get_melody_state_callback, get_wow_state_callback):
        self.get_frequency = get_frequency_callback
        self.is_melody_on = get_melody_state_callback
        self.is_wow_on = get_wow_state_callback

        self.fs = 44100  # 샘플레이트
        self.blocksize = 512  # 블록 크기
        self.phase = 0.0  # 현재 위상
        self.prev_melody_on = False  # 이전 멜로디 상태 기억

        self.fade_samples = int(self.fs * 0.01)  # 10ms 페이드

        self.stream = sd.OutputStream(
            samplerate=self.fs,
            channels=1,
            blocksize=self.blocksize,
            callback=self.audio_callback
        )
        self.stream.start()

    def audio_callback(self, outdata, frames, time, status):
        freq = self.get_frequency()
        phase_inc = 2 * np.pi * freq / self.fs
        phase_array = self.phase + phase_inc * np.arange(frames)
        wave = np.sin(phase_array).astype(np.float32)
        self.phase = (phase_array[-1] + phase_inc) % (2 * np.pi)

        # 현재 멜로디 상태 확인
        current_melody_on = self.is_melody_on()

        # 페이드 처리를 위한 계수 계산
        fade = np.ones(frames, dtype=np.float32)

        if current_melody_on and not self.prev_melody_on:
            # ON 직후 → fade-in
            fade_len = min(frames, self.fade_samples)
            fade[:fade_len] = np.linspace(0.0, 1.0, fade_len)

        elif not current_melody_on and self.prev_melody_on:
            # OFF 직후 → fade-out
            fade_len = min(frames, self.fade_samples)
            fade[-fade_len:] = np.linspace(1.0, 0.0, fade_len)

        elif not current_melody_on:
            # 멜로디 꺼져 있으면 음 없음
            wave[:] = 0.0

        outdata[:, 0] = 0.5 * wave * fade
        self.prev_melody_on = current_melody_on

    def stop(self):
        self.stream.stop()
        self.stream.close()
