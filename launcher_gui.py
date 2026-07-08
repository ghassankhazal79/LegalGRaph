# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import threading
import webbrowser
import time
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PORT = "8765"
process = None

def run_command(cmd):
    def target():
        try:
            out.insert(tk.END, "\n> " + " ".join(cmd) + "\n")
            out.see(tk.END)
            p = subprocess.Popen(
                cmd,
                cwd=str(ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                shell=False
            )
            for line in p.stdout:
                out.insert(tk.END, line)
                out.see(tk.END)
            p.wait()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    threading.Thread(target=target, daemon=True).start()

def install_requirements():
    run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def rebuild_entities():
    run_command([sys.executable, "scripts/04_extract_entities_graph.py"])

def start_server():
    global process
    if process and process.poll() is None:
        messagebox.showinfo("Running", "Server is already running.")
        return

    env = os.environ.copy()
    env["PORT"] = PORT
    env["USE_FAISS"] = "0"
    env["DEVICE"] = "-1"

    out.insert(tk.END, "\nStarting server on http://127.0.0.1:" + PORT + "\n")
    out.see(tk.END)

    process = subprocess.Popen(
        [sys.executable, "app/app.py"],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env
    )

    def read_output():
        for line in process.stdout:
            out.insert(tk.END, line)
            out.see(tk.END)

    threading.Thread(target=read_output, daemon=True).start()
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:" + PORT)

def open_home():
    webbrowser.open("http://127.0.0.1:" + PORT)

def open_entities():
    webbrowser.open("http://127.0.0.1:" + PORT + "/entities")

def open_graph():
    webbrowser.open("http://127.0.0.1:" + PORT + "/entity-graph")

def stop_server():
    global process
    if process and process.poll() is None:
        process.terminate()
        out.insert(tk.END, "\nServer stopped.\n")
        out.see(tk.END)
    else:
        out.insert(tk.END, "\nServer is not running.\n")
        out.see(tk.END)

root = tk.Tk()
root.title("Higher Education Legal AI Launcher")
root.geometry("850x560")

title = tk.Label(root, text="Higher Education Legal AI Project", font=("Arial", 16, "bold"))
title.pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=8)

tk.Button(frame, text="Install Requirements", width=22, command=install_requirements).grid(row=0, column=0, padx=5, pady=5)
tk.Button(frame, text="Start Server", width=22, command=start_server).grid(row=0, column=1, padx=5, pady=5)
tk.Button(frame, text="Stop Server", width=22, command=stop_server).grid(row=0, column=2, padx=5, pady=5)

tk.Button(frame, text="Open Home", width=22, command=open_home).grid(row=1, column=0, padx=5, pady=5)
tk.Button(frame, text="Open Entities", width=22, command=open_entities).grid(row=1, column=1, padx=5, pady=5)
tk.Button(frame, text="Open Entity Graph", width=22, command=open_graph).grid(row=1, column=2, padx=5, pady=5)

tk.Button(frame, text="Rebuild Entity Graph", width=22, command=rebuild_entities).grid(row=2, column=1, padx=5, pady=5)

out = tk.Text(root, height=22, wrap="word")
out.pack(fill="both", expand=True, padx=12, pady=12)
out.insert(tk.END, "Ready. Recommended: click Install Requirements, then Start Server.\n")

root.protocol("WM_DELETE_WINDOW", lambda: (stop_server(), root.destroy()))
root.mainloop()
