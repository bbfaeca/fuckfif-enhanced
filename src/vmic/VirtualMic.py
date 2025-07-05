import os
import platform
import pyaudio
import wave
import subprocess
import time

class VirtualMic:
    def __init__(self, device_name="VirtualMic", format="s16le", rate=44100, channels=1):
        self.device_name = device_name
        self.format = format
        self.rate = rate
        self.channels = channels

        if platform.system() == "Linux":
            self._init_linux()
        elif platform.system() == "Windows":
            self._init_windows()
        else:
            raise NotImplementedError("Unsupported OS: {}".format(platform.system()))

    def _init_linux(self):
        retry = 0
        while not os.path.exists("/tmp/" + self.device_name):
            retry += 1
            if retry > 5:
                raise Exception("[VirtualMic] 虚拟声卡初始化失败。")
            print("[VirtualMic] 开始初始化虚拟声卡。")
            os.system(
                "pactl load-module module-pipe-source source_name={} file=/tmp/{} format={} rate={} channels={}".format(
                    self.device_name, self.device_name, self.format, self.rate, self.channels
                )
            )
            os.system(
                "pacmd update-source-proplist {} device.description={}".format(
                    self.device_name, self.device_name
                )
            )
            os.system("pacmd set-default-source {}".format(self.device_name))
        print("[VirtualMic] 虚拟声卡初始化完成。")

    def _init_windows(self):
        print("[VirtualMic] 开始初始化Windows虚拟麦克风。")
        p = pyaudio.PyAudio()
        try:
            vb_cable_index = self._get_vb_cable_index(p)
            if vb_cable_index is None:
                raise Exception("[VirtualMic] 未找到VB-CABLE设备。")
            print("[VirtualMic] 找到VB-CABLE设备，索引：{}".format(vb_cable_index))
        finally:
            p.terminate()
        print("[VirtualMic] Windows虚拟麦克风初始化完成。")

    def _get_vb_cable_index(self, pyaudio_instance):
        for i in range(pyaudio_instance.get_device_count()):
            dev = pyaudio_instance.get_device_info_by_index(i)
            if 'CABLE Input' in dev['name'] and dev['maxOutputChannels'] > 0:
                return i
        return None

    def play(self, file_path):
        if platform.system() == "Linux":
            self._play_linux(file_path)
        elif platform.system() == "Windows":
            self._play_windows(file_path)
        else:
            raise NotImplementedError("Unsupported OS")

    def _play_linux(self, file_path):
        print("[VirtualMic] 音频流开始从{}读到虚拟声卡中。".format(file_path))
        cmd = (
            "ffmpeg -re -i {} -f {} -ar {} -ac {} -async 1 -filter:a volume=0.8 - > /tmp/{}".format(
                file_path, self.format, self.rate, self.channels, self.device_name
            )
        )
        process = subprocess.Popen(cmd, shell=True)
        exit_code = process.wait()
        if exit_code != 0:
            raise Exception("[VirtualMic] ffmpeg播放失败。")
        print("[VirtualMic] 音频流结束。")

    def _play_windows(self, file_path):
        print("[VirtualMic] 音频流开始从{}读到虚拟麦克风中。".format(file_path))
        wf = wave.open(file_path, 'rb')
        p = pyaudio.PyAudio()
        try:
            vb_cable_index = self._get_vb_cable_index(p)
            if vb_cable_index is None:
                raise Exception("[VirtualMic] 未找到VB-CABLE设备。")
            stream = p.open(
                format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                output_device_index=vb_cable_index,
                frames_per_buffer=1024
            )
            data = wf.readframes(1024)
            while data:
                stream.write(data)
                data = wf.readframes(1024)
            stream.stop_stream()
            stream.close()
        except Exception as e:
            print("[VirtualMic] 播放失败：{}".format(e))
            raise
        finally:
            p.terminate()
            wf.close()
        print("[VirtualMic] 音频流结束。")