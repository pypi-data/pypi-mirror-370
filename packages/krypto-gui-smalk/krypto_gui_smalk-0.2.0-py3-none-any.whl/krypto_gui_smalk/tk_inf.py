# coding: utf-8

import os
import tkinter as tk
from tkinter import ttk, messagebox

from krypto_gui_smalk.resource_manager import ResourceManager
from alerk_pack.crypto import str2bytes, bytes2str
from alerk_pack.crypto import gen_sym_key, sym_key_to_str, str_to_sym_key, sym_encrypt, sym_decrypt
from alerk_pack.crypto import gen_asym_keys, asym_key_to_str, str_to_asym_key, asym_encrypt, asym_decrypt
from alerk_pack.message import MessageEn, MessageContainer


class App(tk.Tk):
    def __init__(self, rm: ResourceManager):
        super().__init__()

        self.title("krypto_gui_smalk")
        self.iconphoto(False, tk.PhotoImage(file=rm.ico_path()))

        self.geometry("700x500")
        self.minsize(700, 500)

        # Sym vars
        self.sym_key_entry: ttk.Entry | None = None
        self.generate_sym_key_btn: ttk.Button | None = None
        self.sym_input_text: tk.Text | None = None
        self.sym_output_text: tk.Text | None = None
        self.sym_encrypt_btn: ttk.Button | None = None
        self.sym_decrypt_btn: ttk.Button | None = None

        # Asym vars
        self.private_key_entry: ttk.Entry | None = None
        self.public_key_entry: ttk.Entry | None = None
        self.generate_keypair_btn: ttk.Button | None = None
        self.asym_input_text: tk.Text | None = None
        self.asym_output_text: tk.Text | None = None
        self.asym_encrypt_btn: ttk.Button | None = None
        self.asym_decrypt_btn: ttk.Button | None = None

        # File vars
        self.file_key_entry: ttk.Entry | None = None
        self.generate_file_key_btn: ttk.Button | None = None
        self.file_in_entry: ttk.Entry | None = None
        self.file_out_entry: ttk.Entry | None = None
        self.file_encrypt_btn: ttk.Button | None = None
        self.file_decrypt_btn: ttk.Button | None = None
        self.file_progress_label: ttk.Label | None = None

        # Tabs
        self.tab_control = ttk.Notebook(self)
        self.tab_symmetric = ttk.Frame(self.tab_control)
        self.tab_asymmetric = ttk.Frame(self.tab_control)
        self.tab_file = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_symmetric, text="Symmetric")
        self.tab_control.add(self.tab_asymmetric, text="Asymmetric")
        self.tab_control.add(self.tab_file, text="     File     ")
        self.tab_control.pack(fill=tk.BOTH, expand=True)

        self.setup_symmetric_tab()
        self.setup_asymmetric_tab()
        self.setup_file_tab()

    def setup_symmetric_tab(self):
        tab = self.tab_symmetric

        # Key section
        key_frame = ttk.Frame(tab, padding=5)
        key_frame.pack(fill=tk.X)

        ttk.Label(key_frame, text="Key:").pack(side=tk.LEFT)
        self.sym_key_entry = ttk.Entry(key_frame, width=55)
        self.sym_key_entry.pack(side=tk.LEFT, padx=5)

        self.sym_key_entry.bind("<Control-a>", lambda e: self._select_all_entry(self.sym_key_entry))
        self.sym_key_entry.bind("<Control-A>", lambda e: self._select_all_entry(self.sym_key_entry))
        self.sym_key_entry.bind("<Control-v>", lambda e: self._paste_over_selection_entry(self.sym_key_entry))
        self.sym_key_entry.bind("<Control-V>", lambda e: self._paste_over_selection_entry(self.sym_key_entry))

        self.generate_sym_key_btn = ttk.Button(
            key_frame,
            text="Generate",
            command=self.generate_sym_key,
            width=10
        )
        self.generate_sym_key_btn.pack(side=tk.LEFT)

        # Input and Output texts
        text_frame = ttk.Frame(tab, padding=5)
        text_frame.pack(fill=tk.BOTH, expand=True)

        # Input (left)
        input_frame = ttk.Frame(text_frame)
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        ttk.Label(input_frame, text="Input:").pack(anchor=tk.W)
        self.sym_input_text = tk.Text(input_frame, height=8, width=30, wrap=tk.WORD)
        self.sym_input_text.pack(fill=tk.BOTH, expand=True)

        self.sym_input_text.bind("<Control-a>", self._select_all_text)
        self.sym_input_text.bind("<Control-A>", self._select_all_text)
        self.sym_input_text.bind("<Control-v>", self._paste_over_selection_text)
        self.sym_input_text.bind("<Control-V>", self._paste_over_selection_text)

        # Output (right)
        output_frame = ttk.Frame(text_frame)
        output_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(output_frame, text="Output:").pack(anchor=tk.W)
        self.sym_output_text = tk.Text(output_frame, height=8, width=30, wrap=tk.WORD, state="disabled")
        self.sym_output_text.pack(fill=tk.BOTH, expand=True)

        self.sym_output_text.bind("<Control-a>", self._select_all_text)
        self.sym_output_text.bind("<Control-A>", self._select_all_text)

        # Buttons
        button_frame = ttk.Frame(tab, padding=5)
        button_frame.pack(fill=tk.X)

        self.sym_encrypt_btn = ttk.Button(
            button_frame,
            text="Encrypt",
            command=self.sym_encrypt_text,
            width=10
        )
        self.sym_encrypt_btn.pack(side=tk.LEFT, padx=2)

        self.sym_decrypt_btn = ttk.Button(
            button_frame,
            text="Decrypt",
            command=self.sym_decrypt_text,
            width=10
        )
        self.sym_decrypt_btn.pack(side=tk.LEFT)

    def setup_asymmetric_tab(self):
        tab = self.tab_asymmetric

        key_frame = ttk.Frame(tab, padding=5)
        key_frame.pack(fill=tk.X)

        # Private Key
        ttk.Label(key_frame, text="Private Key:").pack(anchor=tk.W)
        self.private_key_entry = ttk.Entry(key_frame, width=50)
        self.private_key_entry.pack(fill=tk.X, padx=5)

        # Public Key
        ttk.Label(key_frame, text="Public Key:").pack(anchor=tk.W)
        self.public_key_entry = ttk.Entry(key_frame, width=50)
        self.public_key_entry.pack(fill=tk.X, padx=5, pady=(0, 10))

        self.private_key_entry.bind("<Control-a>", lambda e: self._select_all_entry(self.private_key_entry))
        self.private_key_entry.bind("<Control-A>", lambda e: self._select_all_entry(self.private_key_entry))
        self.private_key_entry.bind("<Control-v>", lambda e: self._paste_over_selection_entry(self.private_key_entry))
        self.private_key_entry.bind("<Control-V>", lambda e: self._paste_over_selection_entry(self.private_key_entry))

        self.public_key_entry.bind("<Control-a>", lambda e: self._select_all_entry(self.public_key_entry))
        self.public_key_entry.bind("<Control-A>", lambda e: self._select_all_entry(self.public_key_entry))
        self.public_key_entry.bind("<Control-v>", lambda e: self._paste_over_selection_entry(self.public_key_entry))
        self.public_key_entry.bind("<Control-V>", lambda e: self._paste_over_selection_entry(self.public_key_entry))


        self.generate_keypair_btn = ttk.Button(
            key_frame,
            text="Generate Key Pair",
            command=self.generate_asym_key_pair,
            width=15
        )
        self.generate_keypair_btn.pack(pady=5)

        # Text fields
        text_frame = ttk.Frame(tab, padding=5)
        text_frame.pack(fill=tk.BOTH, expand=True)

        # Input
        input_frame = ttk.Frame(text_frame)
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        ttk.Label(input_frame, text="Input:").pack(anchor=tk.W)
        self.asym_input_text = tk.Text(input_frame, height=8, width=30, wrap=tk.WORD)
        self.asym_input_text.pack(fill=tk.BOTH, expand=True)

        # Output
        output_frame = ttk.Frame(text_frame)
        output_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(output_frame, text="Output:").pack(anchor=tk.W)
        self.asym_output_text = tk.Text(output_frame, height=8, width=30, wrap=tk.WORD)
        self.asym_output_text.pack(fill=tk.BOTH, expand=True)

        for text_widget in [self.asym_input_text, self.asym_output_text]:
            text_widget.bind("<Control-a>", self._select_all_text)
            text_widget.bind("<Control-A>", self._select_all_text)
        self.asym_input_text.bind("<Control-v>", self._paste_over_selection_text)
        self.asym_input_text.bind("<Control-V>", self._paste_over_selection_text)

        # Buttons
        button_frame = ttk.Frame(tab, padding=5)
        button_frame.pack(fill=tk.X)

        self.asym_encrypt_btn = ttk.Button(
            button_frame,
            text="Encrypt",
            command=self.asym_encrypt_text,
            width=10
        )
        self.asym_encrypt_btn.pack(side=tk.LEFT, padx=2)

        self.asym_decrypt_btn = ttk.Button(
            button_frame,
            text="Decrypt",
            command=self.asym_decrypt_text,
            width=10
        )
        self.asym_decrypt_btn.pack(side=tk.LEFT)

    def setup_file_tab(self):
        tab = self.tab_file

        # Key section
        key_frame = ttk.Frame(tab, padding=5)
        key_frame.pack(fill=tk.X)

        ttk.Label(key_frame, text="Key:").pack(side=tk.LEFT)
        self.file_key_entry = ttk.Entry(key_frame, width=55)
        self.file_key_entry.pack(side=tk.LEFT, padx=5)

        self.file_key_entry.bind("<Control-a>", lambda e: self._select_all_entry(self.file_key_entry))
        self.file_key_entry.bind("<Control-A>", lambda e: self._select_all_entry(self.file_key_entry))
        self.file_key_entry.bind("<Control-v>", lambda e: self._paste_over_selection_entry(self.file_key_entry))
        self.file_key_entry.bind("<Control-V>", lambda e: self._paste_over_selection_entry(self.file_key_entry))

        self.generate_file_key_btn = ttk.Button(
            key_frame,
            text="Generate",
            command=self.generate_file_key,
            width=10
        )
        self.generate_file_key_btn.pack(side=tk.LEFT)

        # File fields section
        file_frame = ttk.Frame(tab, padding=5)
        file_frame.pack(fill=tk.X)

        ttk.Label(file_frame, text="File in:").pack(anchor=tk.W)
        self.file_in_entry = ttk.Entry(file_frame, width=55)
        self.file_in_entry.pack(fill=tk.X, padx=5)

        ttk.Label(file_frame, text="File out:").pack(anchor=tk.W)
        self.file_out_entry = ttk.Entry(file_frame, width=55)
        self.file_out_entry.pack(fill=tk.X, padx=5)

        self.file_in_entry.bind("<Control-a>", lambda e: self._select_all_entry(self.file_in_entry))
        self.file_in_entry.bind("<Control-A>", lambda e: self._select_all_entry(self.file_in_entry))
        self.file_in_entry.bind("<Control-v>", lambda e: self._paste_over_selection_entry(self.file_in_entry))
        self.file_in_entry.bind("<Control-V>", lambda e: self._paste_over_selection_entry(self.file_in_entry))

        self.file_out_entry.bind("<Control-a>", lambda e: self._select_all_entry(self.file_out_entry))
        self.file_out_entry.bind("<Control-A>", lambda e: self._select_all_entry(self.file_out_entry))
        self.file_out_entry.bind("<Control-v>", lambda e: self._paste_over_selection_entry(self.file_out_entry))
        self.file_out_entry.bind("<Control-V>", lambda e: self._paste_over_selection_entry(self.file_out_entry))

        # Buttons
        button_frame = ttk.Frame(tab, padding=5)
        button_frame.pack(fill=tk.X)

        self.file_encrypt_btn = ttk.Button(
            button_frame,
            text="Encrypt",
            command=self.sym_encrypt_file,
            width=10
        )
        self.file_encrypt_btn.pack(side=tk.LEFT, padx=2)

        self.file_decrypt_btn = ttk.Button(
            button_frame,
            text="Decrypt",
            command=self.sym_decrypt_file,
            width=10
        )
        self.file_decrypt_btn.pack(side=tk.LEFT)

        # Progress
        progress_frame = ttk.Frame(tab, padding=5)
        progress_frame.pack(fill=tk.X)
        self.file_progress_label = ttk.Label(progress_frame, text="")
        self.file_progress_label.pack(side=tk.LEFT)

    def _select_all_entry(self, entry_widget):
        entry_widget.select_range(0, tk.END)
        return "break"

    def _select_all_text(self, event):
        event.widget.tag_add("sel", "1.0", "end")
        return "break"

    def _paste_over_selection_entry(self, entry_widget):
        # entry_widget.delete(0, tk.END)
        # entry_widget.insert(0, self.clipboard_get())

        # cursor_position = entry_widget.index(tk.INSERT)
        # clipboard_text = self.clipboard_get()
        # entry_widget.insert(cursor_position, clipboard_text)

        cursor_position = entry_widget.index(tk.INSERT)
        clipboard_text = self.clipboard_get()
        selected_text = entry_widget.selection_get() if entry_widget.selection_present() else ""
        if selected_text:
            start_index = entry_widget.index(tk.SEL_FIRST)
            end_index = entry_widget.index(tk.SEL_LAST)
            entry_widget.delete(start_index, end_index)
        entry_widget.insert(cursor_position, clipboard_text)

        return "break"

    def _paste_over_selection_text(self, event):
        text_widget = event.widget
        if text_widget.tag_ranges("sel"):
            text_widget.delete("sel.first", "sel.last")
        text_widget.insert("insert", self.clipboard_get())
        return "break"

    def paste_text_to_output(self, output_text: tk.Text, text: str):
        output_text.config(state="normal")
        output_text.delete("1.0", tk.END)
        output_text.insert("1.0", text)
        output_text.config(state="disabled")

    def generate_sym_key(self):
        try:
            key = gen_sym_key()
            key_str = sym_key_to_str(key)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot generate key: {e}")
            return

        self.sym_key_entry.delete(0, tk.END)
        self.sym_key_entry.insert(0, f"{key_str}")

    def sym_encrypt_text(self):
        text = self.sym_input_text.get("1.0", tk.END).strip()
        key_str = self.sym_key_entry.get().strip()
        if key_str == "":
            messagebox.showerror("Error", "Input or generate key first")
            return
        if text == "":
            messagebox.showerror("Error", "Input text to encrypt (left)")
            return
        try:
            key = str_to_sym_key(key_str)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot form key: {e}")
            return

        try:
            text_b: bytes = text.encode(encoding="utf-8")
            text_en: bytes = sym_encrypt(text_b, key)
            text_en_coded: str = bytes2str(text_en)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot encrypt: {e}")
            return

        self.paste_text_to_output(self.sym_output_text, f"{text_en_coded}")

    def sym_decrypt_text(self):
        text = self.sym_input_text.get("1.0", tk.END).strip()
        key_str = self.sym_key_entry.get().strip()

        if key_str == "":
            messagebox.showerror("Error", "Input or generate key first")
            return
        if text == "":
            messagebox.showerror("Error", "Input text to decrypt (left)")
            return

        try:
            key = str_to_sym_key(key_str)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot form key: {e}")
            return

        text_en_coded = text
        try:
            text_en: bytes = str2bytes(text_en_coded)
            text_b: bytes = sym_decrypt(text_en, key)
            text: str = text_b.decode(encoding="utf-8")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot decrypt: {e}")
            return

        self.paste_text_to_output(self.sym_output_text, f"{text}")

    def generate_asym_key_pair(self):
        try:
            priv_key, pub_key = gen_asym_keys()
            priv_key_str = asym_key_to_str(priv_key)
            pub_key_str = asym_key_to_str(pub_key)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot generate key: {e}")
            return

        self.private_key_entry.delete(0, tk.END)
        self.private_key_entry.insert(0, f"{priv_key_str}")
        self.public_key_entry.delete(0, tk.END)
        self.public_key_entry.insert(0, f"{pub_key_str}")

    def asym_encrypt_text(self):
        text = self.asym_input_text.get("1.0", tk.END).strip()
        public_key_str = self.public_key_entry.get().strip()

        if public_key_str == "":
            messagebox.showerror("Error", "Input or generate keys first (public)")
            return
        if text == "":
            messagebox.showerror("Error", "Input text to encrypt (left)")
            return

        try:
            pub_key = str_to_asym_key(public_key_str, True)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot form public key: {e}")
            return

        try:
            mc: MessageContainer = MessageContainer({"m": text})
            mc_en: MessageContainer = mc.encrypt(pub_key)
            men: MessageEn = mc_en.get_data()
            text_en_coded: str = men.to_json()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot encrypt: {e}")
            return

        self.paste_text_to_output(self.asym_output_text, f"{text_en_coded}")

    def asym_decrypt_text(self):

        text_en_coded = self.asym_input_text.get("1.0", tk.END).strip()
        priv_key_str = self.private_key_entry.get().strip()

        if priv_key_str == "":
            messagebox.showerror("Error", "Input or generate keys first (private)")
            return
        if text_en_coded == "":
            messagebox.showerror("Error", "Input text to encrypt (left)")
            return

        try:
            priv_key = str_to_asym_key(priv_key_str, False)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot form private key: {e}")
            return

        try:
            men: MessageEn = MessageEn.from_json(text_en_coded)
            mc_en: MessageContainer = MessageContainer(men)
            mc: MessageContainer = mc_en.decrypt(priv_key)
            d: dict[str: str] = mc.get_data()
            text = d["m"]
        except Exception as e:
            messagebox.showerror("Error", f"Cannot decrypt: {e}")
            return

        self.paste_text_to_output(self.asym_output_text, f"{text}")

    def generate_file_key(self):
        try:
            file_key = gen_sym_key()
            file_key_str = sym_key_to_str(file_key)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot generate key: {e}")
            return

        self.file_key_entry.delete(0, tk.END)
        self.file_key_entry.insert(0, f"{file_key_str}")

    def sym_encrypt_file(self):
        key_str = self.file_key_entry.get().strip()
        file_in_path = self.file_in_entry.get().strip()
        file_out_path = self.file_out_entry.get().strip()
        if key_str == "":
            messagebox.showerror("Error", "Input or generate key first")
            return
        if file_in_path == "":
            messagebox.showerror("Error", "Input file in")
            return
        if file_out_path == "":
            messagebox.showerror("Error", "Input file out")
            return
        if not os.path.isfile(file_in_path):
            messagebox.showerror("Error", f"No such file: \"{file_in_path}\"")
            return
        elif os.path.isdir(file_in_path):
            messagebox.showerror("Error", f"File \"{file_in_path}\" is directory. ")
            return

        try:
            key = str_to_sym_key(key_str)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot form key: {e}")
            return

        self.file_progress_label.config(text="Encrypting...")
        self.update_idletasks()

        try:
            with open(file_in_path, 'rb') as fd:
                bs = fd.read()
            bs_en: bytes = sym_encrypt(bs, key)
            with open(file_out_path, 'wb') as fd:
                fd.write(bs_en)
                fd.flush()
        except Exception as e:
            self.file_progress_label.config(text="Error")
            self.update_idletasks()
            messagebox.showerror("Error", f"Cannot encrypt: {e}")
            return

        self.file_progress_label.config(text="Done!")
        self.update_idletasks()

    def sym_decrypt_file(self):
        key_str = self.file_key_entry.get().strip()
        file_in_path = self.file_in_entry.get().strip()
        file_out_path = self.file_out_entry.get().strip()
        if key_str == "":
            messagebox.showerror("Error", "Input or generate key first")
            return
        if file_in_path == "":
            messagebox.showerror("Error", "Input file in")
            return
        if file_out_path == "":
            messagebox.showerror("Error", "Input file out")
            return
        if not os.path.isfile(file_in_path):
            messagebox.showerror("Error", f"No such file: \"{file_in_path}\"")
            return
        elif os.path.isdir(file_in_path):
            messagebox.showerror("Error", f"File \"{file_in_path}\" is directory. ")
            return

        try:
            key = str_to_sym_key(key_str)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot form key: {e}")
            return

        self.file_progress_label.config(text="Decrypting...")
        self.update_idletasks()

        try:
            with open(file_in_path, 'rb') as fd:
                bs_en = fd.read()
            bs: bytes = sym_decrypt(bs_en, key)
            with open(file_out_path, 'wb') as fd:
                fd.write(bs)
                fd.flush()
        except Exception as e:
            self.file_progress_label.config(text="Error")
            self.update_idletasks()
            messagebox.showerror("Error", f"Cannot decrypt: {e}")
            return

        self.file_progress_label.config(text="Done!")
        self.update_idletasks()
