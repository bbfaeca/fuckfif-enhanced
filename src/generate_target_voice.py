from TTS.api import TTS
import os

# 初始化 TTS 模型
model = "tts_models/en/vctk/vits"
tts = TTS(model_name=model, progress_bar=False).to("cpu")

# 目标句子
text = (
    "The original vision of AI was re-articulated in two sousands via the term "
    "Artificial General Intelligence or AGI. This vision is to build Thinking Machines "
    "computer systems that can learn, reason, and solve problems similar to the way humans do."
)

# 输出路径
output_path = "D:/app/githubprojects/fuckfif/fuckfif-main/fuckfif-main/src/draft/target_voice_male.wav"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# 生成音频
print("[TTS] Generating target voice audio with male voice...")

# 请将 "YOUR_MALE_SPEAKER_ID_HERE" 替换为您从上面列表中找到的男性说话人 ID
tts.tts_to_file(
    text=text,
    file_path=output_path,
    speaker="p228" # 替换为您选择的男性说话人 ID
)
print(f"[TTS] Generated male target voice: {output_path}")