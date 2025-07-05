import io
import json

print("[main] 正在检测环境并加载神经网络。")

from connector.FiFWebClient import FiFWebClient
from speaker.Speaker import Speaker

print("[main] FiF口语,启动!")

fif = FiFWebClient()  # 初始化FiF口语网页客户端
speaker = Speaker(  # 初始化语音合成器
    "tts_models/multilingual/multi-dataset/your_tts",  # 语音合成器模型
    "cpu",  # cuda|cpu 是否启用GPU加速
    "VirtualPipeMic",  # 虚拟麦克风名称 最后会将音频流输出到/tmp/{此选项的名称}
    "draft/target_voice.wav",  # 10秒左右的你的录音，用于生成目标音色
)

with io.open("user.json") as f:
    user_json = json.load(f)
    username = user_json["username"]
    password = user_json["password"]

user_info = fif.login(username, password)

print(
    "[main] {}登录成功。用户ID为{}。".format(
        user_info["data"]["realName"], user_info["data"]["userId"]
    )
)

for i, task in enumerate(fif.get_task_list(fif.get_page())["data"]["ttiList"]):
    ttd_list = fif.get_ttd_list(fif.get_page(), task["id"])
    print(
        "[main] 正在开始第{}个任务。任务代码为{}。任务名为{}。".format(i + 1, task["id"], task["taskName"])
    )
    for j, ttd in enumerate(ttd_list["data"]["ttdList"]):
        print(
            "[main] 正在开始第{}个单元。单元代码为{}。单元名为{}。".format(
                j + 1, ttd["id"], ttd["unitName"]
            )
        )
        unit_info = fif.get_unit_info(fif.get_page(), ttd["unitid"], task["taskId"])[
            "data"
        ]
        print("[main] 正在开始第{}个单元。单元代码为{}。".format(j + 1, unit_info["id"]))
        for k, level in enumerate(unit_info["levelList"]):
            # 定义一个默认的目标分数
            target_score = 80

            # 如果当前等级是“情景词汇”，则将目标分数设置为70
            if level["levelName"] == "情景词汇":
                target_score = 80
                print(f"[DEBUG] 检测到等级 '{level['levelName']}'，将其目标分数设置为 {target_score}。")
            else:
                print(f"[DEBUG] 等级 '{level['levelName']}' 目标分数保持为 {target_score}。")

            # 进行分数检测，使用新的 target_score
            if level["levelScore"] >= target_score:
                print("[main] 等级{}（当前分数：{}）超过目标分数 {}。已跳过。".format(
                    level["levelName"], level["levelScore"], target_score))
                continue

            # 获取当前等级名称，用于判断是否是“情景词汇”
            current_level_name = level["levelName"]

            # 判断是否是情景词汇
            is_vocabulary_level = (current_level_name == "情景词汇")

            fif.start_level_test(
                fif.get_page(),
                speaker,
                unit_id=unit_info["id"],
                task_id=task["id"],
                level_id=level["levelId"],
                # 传递 is_vocabulary_level 标志
                is_vocabulary=is_vocabulary_level
            )

            print("[main] 第{}个等级完成。".format(k + 1))
