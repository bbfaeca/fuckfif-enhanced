# TTSSolver.py
from TTS.api import TTS


class TTSSolver:
    def __init__(self, model, mode, target_voice_path):
        print("[TTS] 正在初始化神经网络。")
        self.model = model
        self.target_voice_path = target_voice_path
        self.tts = TTS(model_name=model, progress_bar=False).to(mode)

    def get_voice(self, text):
        return

    # 增加 is_vocabulary 参数，默认为 False
    def get_file(self, text: str, path, is_vocabulary: bool = False):
        if text == "":
            return
        print(f"[TTS] 正在合成语音 (文本: '{text}', 词汇模式: {is_vocabulary})。")

        processed_text = text

        if is_vocabulary:
            # 对于情景词汇，直接合成原始单词，不加任何修饰，追求最纯粹清晰的发音
            processed_text = text.strip()  # 确保没有多余空格
            print(f"[TTS] 情景词汇模式：直接合成原始文本 '{processed_text}'。")
        else:
            # 对于其他短文本（如问答），尝试用标点符号辅助发音
            words = text.split(" ")
            if len(words) <= 2:  # 比如 "why?" 或 "hello world"
                # 尝试用逗号加空格的组合来创造微小停顿，引导清晰发音
                # 例如 "Why?" -> "Why, " (一个词后面跟着一个逗号和一个空格，通常会有点停顿)
                # 或者 "Hello world" -> "Hello, world." (中间加逗号)
                if text.endswith("?"):  # 如果是问句，保留问号
                    processed_text = f"{text.replace('?', '')}, ?"  # "Why?" -> "Why, ?"
                elif text.endswith("."):  # 如果是句号，保留句号
                    processed_text = f"{text.replace('.', '')}, ."  # "Hello." -> "Hello, ."
                else:  # 其他情况，添加逗号或句号
                    processed_text = f"{text},"  # "word" -> "word,"

                # 你可以尝试其他形式，例如：
                # processed_text = f"{text} ." # 单词后加空格再加句号
                # processed_text = f"{words[0]} {words[0]}." # 简单重复，但更短的重复

                print(f"[TTS] 非情景词汇短文本，处理为: '{processed_text}'。")
            else:
                # 对于正常长度的文本，保持不变
                print("[TTS] 处理正常长度文本。")

        self.tts.tts_to_file(
            text=processed_text,
            speaker_wav=self.target_voice_path,
            language="en",
            file_path=path,
        )
        return