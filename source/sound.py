import numpy as np
import sounddevice as sd

class SoundPlayer:
    def __init__(self, get_frequency_callback, get_melody_state_callback, get_wow_state_callback):
        self.get_frequency = get_frequency_callback
        self.is_melody_on = get_melody_state_callback
        self.is_wow_on = get_wow_state_callback

        self.fs = 44100
        self.blocksize = 512
        self.phase = 0.0
        self.prev_melody_on = False
        self.fade_samples = int(self.fs * 0.01)  # 10ms 페이드

        self.waveform_callback = None  # 파형 시각화 콜백

        # 기본 파형 선택: 아래 중 하나
        #self.wave_function = self.generate_recorder_wave
        #self.wave_function = self.generate_sine_wave
        #self.wave_function = self.generate_saw_wave

        self.stream = sd.OutputStream(
            samplerate=self.fs,
            channels=1,
            blocksize=self.blocksize,
            callback=self.audio_callback
        )
        self.stream.start()

    def audio_callback(self, outdata, frames, time, status):
        freq = self.get_frequency()
        t = np.arange(frames) / self.fs
        phase_array = self.phase + 2 * np.pi * freq * t

        if self.is_wow_on():
            wave = self.generate_saw_wave(freq, phase_array, volume=0.3)
        else:
            wave = self.generate_recorder_wave(freq, phase_array)

        self.phase += 2 * np.pi * freq * frames / self.fs
        self.phase %= 2 * np.pi

        # 멜로디 On/Off 처리
        current_melody_on = self.is_melody_on()
        fade = np.ones(frames, dtype=np.float32)

        if current_melody_on and not self.prev_melody_on:
            fade[:min(frames, self.fade_samples)] = np.linspace(0.0, 1.0, min(frames, self.fade_samples))
        elif not current_melody_on and self.prev_melody_on:
            fade[-min(frames, self.fade_samples):] = np.linspace(1.0, 0.0, min(frames, self.fade_samples))
        elif not current_melody_on:
            wave[:] = 0.0

        outdata[:, 0] = 0.5 * wave.astype(np.float32) * fade
        self.prev_melody_on = current_melody_on

        # 파형 콜백에 현재 wave 데이터를 넘김 (시각화용)
        if self.waveform_callback:
            # 너무 길면 화면에 다 못 그리므로 512개만 슬라이스
            self.waveform_callback(wave[:512].copy())

    def stop(self):
        self.stream.stop()
        self.stream.close()

    # ──────────────── 파형 생성 함수들 ────────────────

    def generate_sine_wave(self, freq, phase_array):
        return np.sin(phase_array)

    def generate_recorder_wave(self, freq, phase_array):
        base = 0.6 * np.sin(phase_array)
        harmonic2 = 0.2 * np.sin(2 * phase_array)
        harmonic3 = 0.1 * np.sin(3 * phase_array)
        return base + harmonic2 + harmonic3

    def generate_saw_wave(self, freq, phase_array, harmonics=10, volume=0.3):
        wave = np.zeros_like(phase_array)
        for n in range(1, harmonics + 1):
            wave += (1 / n) * np.sin(n * phase_array)
        return volume * wave

    def set_waveform_callback(self, callback):
        self.waveform_callback = callback
