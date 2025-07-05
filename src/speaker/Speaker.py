# Speaker.py
import time

from tts.TTSSolver import TTSSolver
from vmic.VirtualMic import VirtualMic


class Speaker:
    def __init__(self, tts_model_name, mode, vmic, target_voice_path):
        self.tts_solver = TTSSolver(tts_model_name, mode, target_voice_path)
        self.virtual_mic = VirtualMic(vmic, "s16le", "44100", "2")
        pass

    # 修改 speak 方法，增加 is_vocabulary 参数
    def speak(self, text: str, is_vocabulary: bool = False):
        print("[Speaker] 正在合成语音。")
        # 将 is_vocabulary 参数传递给 tts_solver
        self.tts_solver.get_file(text, "tmp/temp.wav", is_vocabulary=is_vocabulary) 
        print("[Speaker] 正在播放语音。")
        self.virtual_mic.play("tmp/temp.wav")
        print("[Speaker] 语音播放完成。")
        return