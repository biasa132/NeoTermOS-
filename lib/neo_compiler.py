import os

class NeoCompiler:
    """
    NeoTermOS compiler: convert .neo scripts -> .py
    Bisa buat optimize eksekusi atau distribusi script
    """

    def __init__(self, src_path, output_dir="lib/compiled"):
        self.src_path = src_path
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def compile(self):
        if not os.path.exists(self.src_path):
            raise FileNotFoundError(f"{self.src_path} not found")

        out_name = os.path.basename(self.src_path).replace(".neo", ".py")
        out_path = os.path.join(self.output_dir, out_name)

        with open(self.src_path, "r") as src, open(out_path, "w") as out:
            for line in src:
                # skip comment lines
                if line.strip().startswith("#") or not line.strip():
                    continue
                out.write(line)

        print(f"[NEO COMPILER] Compiled {self.src_path} -> {out_path}")
        return out_path
