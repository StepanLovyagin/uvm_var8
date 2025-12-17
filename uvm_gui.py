import tkinter as tk
from tkinter import messagebox, scrolledtext
import os
import assembler
import interpreter

TEMP_SRC = "temp_src.csv"
TEMP_BIN = "temp_prog.bin"
TEMP_RES = "temp_res.xml"

class UVMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UVM IDE")
        self.root.geometry("1000x600")

        ctrl = tk.Frame(root, pady=5)
        ctrl.pack(fill=tk.X)
        tk.Label(ctrl, text="Диапазон (start:end):").pack(side=tk.LEFT, padx=5)
        self.range_ent = tk.Entry(ctrl, width=10)
        self.range_ent.insert(0, "0:15")
        self.range_ent.pack(side=tk.LEFT)
        tk.Button(ctrl, text="▶ RUN", bg="#4CAF50", fg="white", command=self.run).pack(side=tk.LEFT, padx=10)

        paned = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        self.editor = scrolledtext.ScrolledText(paned, font=("Consolas", 11))
        paned.add(self.editor)
        
        self.output = scrolledtext.ScrolledText(paned, font=("Consolas", 11), bg="#eee")
        paned.add(self.output)

        try:
            with open("vector_mul_5x6.csv", "r", encoding="utf-8") as f:
                self.editor.insert(tk.END, f.read())
        except FileNotFoundError:
            self.editor.insert(
                tk.END,
                "Command,Operand\n; vector_mul_5x6.csv not found\n"
            )


    def run(self):
        code = self.editor.get("1.0", tk.END).strip()
        if not code: return
        
        try:
            with open(TEMP_SRC, 'w', encoding='utf-8') as f: f.write(code)
            
            ir = assembler.parse_csv_to_ir(TEMP_SRC)
            assembler.write_binary_file(TEMP_BIN, assembler.generate_binary(ir))
            
            start, end = interpreter.parse_range(self.range_ent.get())
            vm = interpreter.VirtualMachine()
            vm.load_program(TEMP_BIN)
            vm.execute()
            vm.dump_memory(TEMP_RES, start, end)
            
            with open(TEMP_RES, 'r', encoding='utf-8') as f:
                self.output.delete("1.0", tk.END)
                self.output.insert(tk.END, f.read())
                
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    UVMApp(root)
    root.mainloop()