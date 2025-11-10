import os
import queue
import threading
import datetime

from kokoro import KPipeline, KModel
from IPython.display import display, Audio
import soundfile as sf
import sounddevice as sd
import torch
from kokoro.istftnet import Generator


class AudioGenerator:
    def __init__(self, save_audio=True, output_dir="generated_audio"):
        self.config_path = "D:/AllFiles/HumanoidRobotHomework/kokoro/kokoro/model/kokoro82m/config.json"
        self.model_path = "D:/AllFiles/HumanoidRobotHomework/kokoro/kokoro/model/kokoro82m/kokoro-v1_0.pth"
        self.kmodel = KModel(config=self.config_path, model=self.model_path)
        self.pipeline = KPipeline(lang_code='z', device='cpu')
        self._play_pause_event = threading.Event()
        self._generate_pause_event = threading.Event()
        self._stop_event = threading.Event()
        self.text_queue = queue.Queue()
        self.audio_queue = queue.Queue()
        
        # 新增：保存音频相关设置
        self.save_audio = save_audio
        self.output_dir = output_dir
        if self.save_audio:
            os.makedirs(self.output_dir, exist_ok=True)
            print(f"✅ 音频文件将保存到: {os.path.abspath(self.output_dir)}")

    def generate_audio(self):
        while not self._stop_event.is_set():
            # 如果文本队列为空，则等待
            if self.text_queue.empty():
                self._generate_pause_event.clear()
            self._generate_pause_event.wait()

            text = self.text_queue.get()
            print(f">>>开始生成音频：{text}")
            
            # 为每个文本生成唯一标识
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            text_hash = hash(text) % 10000  # 简单的文本哈希
            
            generator = self.pipeline(
                text, voice='zf_xiaoxiao', model=self.kmodel,
                speed=0.95, split_pattern=r'[。！？,\.\!\?、\n]+'
            )
            
            for i, (gs, ps, audio) in enumerate(generator):
                print(f"生成音频: {gs} / {ps}")
                
                # 保存音频文件（如果启用）
                if self.save_audio:
                    filename = f"audio_{timestamp}_{text_hash}_{i}.wav"
                    filepath = os.path.join(self.output_dir, filename)
                    sf.write(filepath, audio, 24000)
                    print(f"💾 音频已保存: {filepath}")
                
                self.audio_queue.put((i, audio, text if i == 0 else None))  # 只在第一段保存文本
                self._play_pause_event.set()

    def play_audio(self, rate=24000):
        stream = sd.OutputStream(
            samplerate=rate,
            channels=1,
            blocksize=2048,
            dtype='float32'
        )
        stream.start()
        while not self._stop_event.is_set():
            if self.audio_queue.empty():
                self._play_pause_event.clear()
            self._play_pause_event.wait()
            i, audio, text = self.audio_queue.get()
            if audio is None:
                break
            print(f"▶ 正在播放第 {i} 段...")
            stream.write(audio)
            self.audio_queue.task_done()

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

    def start_with_text(self):
        self.start()
        self.push_text_manually()


if __name__ == '__main__':
    # 创建音频生成器，启用保存功能
    audio_generator = AudioGenerator(save_audio=True, output_dir="generated_audio")
    audio_generator.start_with_text()
    