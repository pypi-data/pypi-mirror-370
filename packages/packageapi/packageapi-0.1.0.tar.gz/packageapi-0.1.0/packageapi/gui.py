import sys
import subprocess
import threading
import tkinter as tk

def _show_gui(title, message, auto_close=2000):
    root = tk.Tk()
    root.title(title)
    label = tk.Label(root, text=message)
    label.pack(padx=20, pady=20)
    root.update()
    if auto_close:
        root.after(auto_close, root.destroy)
        root.mainloop()
    else:
        return root, label

def install_package(package):
    def do_install():
        root, label = _show_gui("Installer", f"Installing {package}...\nPlease wait.", auto_close=None)
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except Exception as e:
            label.config(text=f"Failed to install {package}:\n{e}")
            root.update()
            root.after(3000, root.destroy)
            root.mainloop()
        else:
            label.config(text=f"Successfully installed {package}!")
            root.update()
            root.after(1500, root.destroy)
            root.mainloop()
    t = threading.Thread(target=do_install)
    t.start()
    t.join()

def check_package(package):
    def do_check():
        try:
            __import__(package)
        except ImportError:
            _show_gui("Check Package", f"Package '{package}' is NOT installed.", auto_close=2500)
            raise
        else:
            _show_gui("Check Package", f"Package '{package}' is installed.", auto_close=1500)
    t = threading.Thread(target=do_check)
    t.start()
    t.join()

def check_and_install_package(package):
    try:
        __import__(package)
    except ImportError:
        install_package(package)

def gui_package_manager():
    def on_action(action):
        pkgs = entry.get().replace(',', ' ').split()
        if not pkgs:
            result_label.config(text="Please enter at least one package name.")
            return

        if mode_var.get() == "generate":
            # Generate packageapi command instead of running
            if action == "check":
                code = "\n".join([f"packageapi.check_package('{p}')" for p in pkgs])
            elif action == "install":
                code = "\n".join([f"packageapi.install_package('{p}')" for p in pkgs])
            elif action == "checkinstall":
                code = "\n".join([f"packageapi.check_and_install_package('{p}')" for p in pkgs])
            _show_gui("Generated packageapi Command", code, auto_close=None)
            result_label.config(text="Generated code only — not executed.")
            return

        # Normal execution
        for pkg in pkgs:
            if action == "check":
                try:
                    check_package(pkg)
                except ImportError:
                    pass
            elif action == "install":
                install_package(pkg)
            elif action == "checkinstall":
                check_and_install_package(pkg)
        result_label.config(text=f"Done: {', '.join(pkgs)}")

    root = tk.Tk()
    root.title("Python Package Manager")
    tk.Label(root, text="Enter package names (comma or space separated):").pack(padx=10, pady=5)
    entry = tk.Entry(root, width=40)
    entry.pack(padx=10, pady=5)

    # Mode toggle
    mode_var = tk.StringVar(value="run")
    tk.Radiobutton(root, text="Run Now", variable=mode_var, value="run").pack()
    tk.Radiobutton(root, text="Generate Code", variable=mode_var, value="generate").pack()

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=5)

    tk.Button(btn_frame, text="Check", width=12, command=lambda: on_action("check")).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Install", width=12, command=lambda: on_action("install")).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Check & Install", width=15, command=lambda: on_action("checkinstall")).pack(side=tk.LEFT, padx=5)

    result_label = tk.Label(root, text="", wraplength=400, fg="blue")
    result_label.pack(padx=10, pady=10)
    root.mainloop()
