# fuckfif: 使用生成语音全自动完成FiF英语口语作业 (增强版)

本项目是基于 [Aurorabili 的 fuckfif](https://github.com/Aurorabili/fuckfif) 的**大幅增强和优化版本**，旨在提供更广泛的平台兼容性、更强大的题型处理能力以及更便捷的使用体验。

**请注意，此项目与原项目存在显著差异。** 为了更好地适应开发环境并优化模块导入，**本项目在 PyCharm 中的运行配置，默认将当前工作目录设置为 `src` 目录。** 这意味着所有对文件路径的引用都应以 `src` 目录为基准。

原项目能够利用生成语音自动完成 FiF 英语口语作业，但主要针对 Linux 环境，且在处理某些复杂题型时可能遇到限制。本分支在保留原有核心功能的基础上，解决了多项痛点，让更多用户受益。

## 新增功能与改进

以下是本版本相较于原项目的主要增强：

  * **全面支持 Windows 平台：**
      * **告别 PulseAudio 依赖：** 替换了原版对 Linux `pulseaudio` 的依赖，现在在 Windows 上可以通过 **VB-Audio Virtual Cable** 完美替代虚拟麦克风功能。用户只需安装 VB-Audio Virtual Cable 驱动即可在 Windows 系统上无缝运行。
  * **优化问答与对话题型处理：**
      * **智能角色对话识别：** 解决了“论文答辩”和“毕业典礼”等对话场景中，语音合成顺序错乱的问题。现在程序能够智能判断对话的**第一个发言者（`w1:` 或 `m1:`）**，并据此调整后续录音顺序，确保合成语音符合 FiF 对话的实际流程（例如，FiF 先提问时，会先合成用户角色的回答，再合成 FiF 角色的回答，反之亦然）。
      * **问答类型题目全覆盖：** 移除了原版中关于“问答题无法录音故跳过”的限制。现在，所有问答类型的题目都能够被程序正常识别并处理，从而实现作业的全面自动化完成。
  * **个性化成绩跳过机制：**
      * **“情景词汇”专项优化：** 针对“情景词汇”这一特定板块，新增了自定义分数阈值。当该板块的当前得分达到 **70分或以上**时，程序将自动跳过，无需重复测试，大大提高了运行效率和用户体验。而其他等级仍保持原有的80分跳过标准。
  * **便捷的目标音色生成：**
      * 引入 `generate_target_voice.py` 脚本，允许用户**自动生成**用于朗读的 `target_voice.wav` 音色文件。这省去了用户自己录音的麻烦，并且在某些情况下可能提供更清晰的生成音色。

## 风险提示 (关于 `generate_target_voice.py`)

请注意，使用 `generate_target_voice.py` 生成目标音色存在一定风险。**该脚本通过技术手段，可能在不经用户实际发声的情况下，生成模拟用户声音的音频文件。** 在某些国家或地区，这种行为可能涉及**道德、法律或隐私风险**。请务必：

  * **仅在您 fully understand and accept the risks** 的情况下使用此功能。
  * **遵守当地法律法规**，并尊重个人隐私。
  * **自行承担所有潜在风险和责任。**

## 快速开始

### 1\. 克隆项目 (或直接在 PyCharm 中打开现有项目)

```bash
git clone [你的项目地址，例如：https://github.com/你的用户名/fuckfif.git]
cd fuckfif
```

### 2\. PyCharm 环境设置

**重要：** 本项目在 PyCharm 中运行时，建议将**运行配置 (Run Configuration) 的工作目录 (Working directory) 设置为 `src` 目录**。

  * 打开 `main.py` 文件。
  * 点击 PyCharm 工具栏中的 **Run** -\> **Edit Configurations...**。
  * 在左侧选择 `main` (或你为 `main.py` 创建的运行配置)。
  * 找到 **Working directory (工作目录)** 字段，点击右侧的文件夹图标，然后选择你项目根目录下的 `src` 文件夹。
  * 点击 **Apply** -\> **OK** 保存设置。

### 3\. 安装依赖

请参考原项目的 `requirements.txt` 文件，并确保安装所有必要的 Python 库。

### 4\. Windows 用户额外设置 (VB-Audio Virtual Cable)

1.  下载并安装 [VB-Audio Virtual Cable](https://vb-audio.com/Cable/)。
2.  在你的操作系统声音设置中，将 VB-Cable Input 设置为默认麦克风设备。
3.  确保 `Speaker.py` 中 `VirtualMic` 的初始化参数 `vmic` 设置为 `VB-Audio Virtual Cable` 或其对应的设备名称。

### 5\. 配置用户凭据

在项目根目录（与 `src` 文件夹同级）创建 `user.json` 文件，并填入你的 FiF 账号信息：

```json
{
    "username": "你的FiF学号",
    "password": "你的FiF密码"
}
```

### 6\. 准备目标音色 (`target_voice.wav`)

你可以选择以下两种方式之一：

  * **手动录制：** 提供一个约10秒左右的你的英语录音（wav格式），并将其路径配置到 `Speaker.py` 中 `target_voice_path` 参数。例如：`"draft/target_voice.wav"`。

  * **自动生成 (推荐，但需注意风险)：** 运行 `generate_target_voice.py` 脚本来生成 `target_voice.wav` 文件。

    ```bash
    python generate_target_voice.py
    ```

    **重要提示：** 在使用此功能前，请务必阅读并理解上方的**风险提示**部分。

### 7\. 运行

```bash
python main.py
```

## 注意事项

  * 语音合成的清晰度取决于所使用的 TTS 模型和目标音色文件。
  * 请确保网络连接稳定。
  * 项目仅供学习交流使用，请遵守相关法律法规及平台使用协议。
