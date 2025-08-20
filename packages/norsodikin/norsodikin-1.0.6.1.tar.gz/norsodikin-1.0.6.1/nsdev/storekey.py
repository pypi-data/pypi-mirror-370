class KeyManager:
    def __init__(self, filename: str = "temp_key.json"):
        self.os = __import__("os")
        self.sys = __import__("sys")
        self.json = __import__("json")
        self.argparse = __import__("argparse")
        self.tempfile = __import__("tempfile")

        nsdev = __import__("nsdev")
        self.logger = nsdev.logger.LoggerHandler()
        self.cipher = nsdev.encrypt.CipherHandler(method="bytes")
        self.gradient = nsdev.gradient.Gradient()

        self.temp_file = self.os.path.join(self.tempfile.gettempdir(), filename)

    def read_key(self):
        if not self.os.path.exists(self.temp_file):
            key = input(
                f"{self.gradient.rgb_to_ansi(*self.gradient.random_color())}Masukkan kunci Anda (bebas teks, simbol, angka):\033[0m "
            )
            env = input(
                f"{self.gradient.rgb_to_ansi(*self.gradient.random_color())}Masukkan nama file .env Anda:\033[0m "
            )
            try:
                data = {"key": self.cipher.encrypt(key), "env": self.cipher.encrypt(env)}
                with open(self.temp_file, "w") as file:
                    self.json.dump(data, file, indent=4)
            except OSError as e:
                self.logger.error(f"Kesalahan saat menyimpan key: {e}")
                self.sys.exit(1)

        try:
            with open(self.temp_file, "r") as file:
                data = self.json.load(file)
            return self.cipher.decrypt(data["key"]), self.cipher.decrypt(data["env"])
        except OSError as e:
            self.logger.error(f"Kesalahan saat membaca key: {e}")
            self.sys.exit(1)
        except self.json.JSONDecodeError:
            self.logger.error(f"File kunci '{self.temp_file}' rusak. Harap hapus file ini dan jalankan ulang skrip.")
            self.sys.exit(1)

    def handle_arguments(self):
        parser = self.argparse.ArgumentParser()
        parser.add_argument("--key", type=str, help="Key yang ingin disimpan atau digunakan.")
        parser.add_argument("--env", type=str, help="Nama file environment.")
        args = parser.parse_args()

        if args.key and args.env:
            try:
                data = {"key": self.cipher.encrypt(args.key), "env": self.cipher.encrypt(args.env)}
                with open(self.temp_file, "w") as file:
                    self.json.dump(data, file, indent=4)
                self.logger.info(f"Kunci baru telah disimpan ke {self.temp_file}")
            except OSError as e:
                self.logger.error(f"Kesalahan saat menyimpan key: {e}")
                self.sys.exit(1)

        return self.read_key()
