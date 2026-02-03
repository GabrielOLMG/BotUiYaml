class BotMediaManager:
    def __init__(self, bot_driver, output_path, logger):
        self.bot_driver = bot_driver
        self.output_path = output_path
        self.logger = logger

        self.history = []
        self.last_path = None

    def capture(self, label: str | None = None):
        path, data = self.bot_driver.get_screenshot(self.output_path)

        self.last_path = path
        self.history.append(data)

        if label:
            self.logger.debug(f"📸 Screenshot capturado: {label}")

        return path, data

    def get_last(self):
        return self.last_path

    def get_history(self):
        return self.history





    # def _create_final_media(self, output_format="gif", fps=5):
    #     frames = []
    #     # 1️⃣ Normaliza tudo para PIL.Image (RGB)
    #     for screenshot in self.screenshots_history:

    #         if isinstance(screenshot, (bytes, bytearray)):
    #             img = Image.open(BytesIO(screenshot)).convert("RGB")

    #         elif isinstance(screenshot, np.ndarray):
    #             img = Image.fromarray(
    #                 cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
    #             )

    #         else:
    #             raise TypeError(
    #                 f"Tipo de screenshot não suportado: {type(screenshot)}"
    #             )

    #         frames.append(img)

    #     if not frames:
    #         return

    #     # 2️⃣ Decide formato de saída
    #     if output_format == "gif":
    #         output_path = os.path.join(self.screenshots_path, "media.gif")

    #         frames[0].save(
    #             output_path,
    #             format="GIF",
    #             save_all=True,
    #             append_images=frames[1:],
    #             duration=int(1000 / fps),
    #             loop=0
    #         )

    #     elif output_format == "mp4":
    #         output_path = os.path.join(self.screenshots_path, "media.mp4")

    #         # PIL -> OpenCV
    #         frame_np = np.array(frames[0])
    #         height, width, _ = frame_np.shape

    #         fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    #         video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    #         for frame in frames:
    #             video.write(
    #                 cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
    #             )

    #         video.release()

    #     else:
    #         raise ValueError("output_format deve ser 'gif' ou 'mp4'")
    #     return output_path