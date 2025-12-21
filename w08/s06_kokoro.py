import os
import queue
import threading

from kokoro import KPipeline, KModel
from IPython.display import display, Audio
import soundfile as sf
import sounddevice as sd
import torch
from kokoro.istftnet import Generator


class AudioGenerator:
    def __init__(self):
        self.config_path = "D:/AllFiles/HumanoidRobotHomework/kokoro/kokoro/model/kokoro82m/config.json"
        self.model_path = "D:/AllFiles/HumanoidRobotHomework/kokoro/kokoro/model/kokoro82m/kokoro-v1_0.pth"
        #self.voice = torch.load('D:/AllFiles/HumanoidRobotHomework/kokoro/kokoro/model/kokoro82m/zf_xiaoxiao.pt', weights_only=False)
        self.kmodel = KModel(config=self.config_path, model=self.model_path)
        self.pipeline = KPipeline(lang_code='z', device='cpu', model=self.kmodel)
        self._play_pause_event = threading.Event()
        self._generate_pause_event = threading.Event()
        self._stop_event = threading.Event()
        self.text_queue = queue.Queue()
        self.audio_queue = queue.Queue()
 
    def generate_audio(self):
        while not self._stop_event.is_set():
            # 如果文本队列为空，则等待
            if self.text_queue.empty():
                self._generate_pause_event.clear()
            self._generate_pause_event.wait()

            text = self.text_queue.get()
            print(f">>>开始生成音频：{text}")
            generator = self.pipeline(
                text, voice='zf_xiaoxiao', model=self.kmodel,
                speed=0.95, split_pattern=r'[。！？,\.\!\?、\n]+'
            )
            for i, (gs, ps, audio) in enumerate(generator):
                print(f"生成音频: {gs} / {ps}")
                self.audio_queue.put((i, audio))
                self._play_pause_event.set()

    def play_audio(self, rate=24000):
        stream = sd.OutputStream(
            samplerate=rate,
            channels=1,  # 根据你的音频调整
            blocksize=2048,  # 调整以优化延迟
            dtype='float32'
        )
        stream.start()
        while not self._stop_event.is_set():
            # 如果音频队列为空，则等待
            if self.audio_queue.empty():
                self._play_pause_event.clear()
            self._play_pause_event.wait()
            i, audio = self.audio_queue.get()
            if audio is None:
                break
            # print(f"▶ 正在播放第 {i} 段...")
            # 直接写入流，不会阻塞
            stream.write(audio)
            # sf.write(f'{i}.wav', audio, rate)
            self.audio_queue.task_done()

    def get_audio(self):
        while not self._stop_event.is_set():
            # 如果音频队列为空，则等待
            if self.audio_queue.empty():
                self._play_pause_event.clear()
            i, audio = self.audio_queue.get()
            if audio is None:
                break
            yield audio


    def push_text(self, text):
        self.text_queue.put(text)
        self._generate_pause_event.set()

    def stop(self):
        self._stop_event.set()
        self._generate_pause_event.set()
        self._play_pause_event.set()

    def push_text_manually(self):
        print("💬 输入要转换的文本（输入 'exit' 或 'quit' 退出）：")
        while True:
            text = input("请输入要转换的文本：")
            if text.lower() in ("exit", "quit"):
                self.stop()
                print("🛑 已退出文本输入模式。")
                break
            elif not text:
                print("(提示：输入为空，已跳过。)")
                continue
            self.push_text(text)

    def start(self):
        threading.Thread(target=self.generate_audio, daemon=True).start()
        threading.Thread(target=self.play_audio, daemon=True).start()

    def start_generate(self):
        threading.Thread(target=self.generate_audio, daemon=True).start()

    def start_with_text(self):
        self.start()
        self.push_text_manually()


if __name__ == '__main__':
    audio_generator = AudioGenerator()
    audio_generator.start_with_text()

    """
    你对于某个问题没有调查，就停止你对于某个问题的发言权。这不太野蛮了吗？一点也不野蛮。你对那个问题的现实情况和历史情况既然没有调查，不知底里，对于那个问题的发言便一定是瞎说一顿。

    """
