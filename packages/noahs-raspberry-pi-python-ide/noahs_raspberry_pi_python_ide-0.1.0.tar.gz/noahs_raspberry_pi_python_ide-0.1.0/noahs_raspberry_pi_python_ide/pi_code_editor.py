#!/usr/bin/env python3
import os, json, threading, io, traceback
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from dataclasses import dataclass, asdict
import time, shlex
import stat, posixpath, datetime
import re
import tkinter.font as tkfont

# External dep: paramiko
try:
    import paramiko
except ImportError:
    raise SystemExit("Please install Paramiko first:  python3 -m pip install paramiko")

try:
    from idlelib.percolator import Percolator
    from idlelib.colorizer import ColorDelegator
except Exception:
    Percolator = None
    ColorDelegator = None


class LineNumbers(tk.Canvas):
    def __init__(self, master, textwidget, **kwargs):
        super().__init__(master, width=48, highlightthickness=0, takefocus=0, cursor="arrow", **kwargs)
        self.textwidget = textwidget

    def redraw(self):
        self.delete("all")
        i = self.textwidget.index("@0,0")
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = i.split(".")[0]
            self.create_text(44, y, anchor="ne", text=linenum, font=("Menlo", 12))
            i = self.textwidget.index(f"{i}+1line")


CONFIG_PATH = os.path.expanduser("~/.pi_editor_config.json")

@dataclass
class PiConfig:
    host: str = "raspberrypi.local"
    port: int = 22
    username: str = "pi"
    use_password: bool = False
    password: str = ""
    key_path: str = ""
    remote_path: str = "/home/pi/Desktop/main.py"
    python_path: str = ""   # optional fallback interpreter (e.g., "python3")
    venv_dir: str = ""      # optional venv directory on the Pi (e.g., "/home/robot/.venvs/myapp")


def load_config() -> PiConfig:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                data = json.load(f)
            return PiConfig(**data)
        except Exception:
            pass
    return PiConfig()

def save_config(cfg: PiConfig):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(asdict(cfg), f, indent=2)
    except Exception:
        pass

class PiEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pi Code Editor")
        self.cfg = load_config()

        self.client = None  # paramiko.SSHClient
        self.sftp = None    # paramiko.SFTPClient
        self.local_filepath = None
        self._cached_remote_home = None

        # State for run
        self._run_thread = None
        self._run_channel = None
        self._running = False

        # State for panels
        self.file_panel = None
        self.settings_frame = None
        self.center_frame = None

        # State for file panel widgets
        self.file_dir_var = None
        self.file_path_var = None
        self.file_tree = None
        self.file_preview = None
        self._file_rows = []
        self._file_selection = None

        # State for interactive terminal
        self._term_chan = None
        self._term_thread = None
        self._term_running = False
        self.term_text = None
        self._term_connected_var = tk.BooleanVar(value=False)
        # Strip most CSI sequences (we'll still manually handle CR + BS)
        self._ansi_re = re.compile(r'\x1b\[[0-9;?]*[A-Za-z]')
        # Strip xterm/OSC title sequences: ESC ] ... (ends with BEL or ST)
        self._osc_re = re.compile(r'\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)')
        self._term_pending_resize = False

        self._term_skip_lines = 0
        self._term_skip_buffer = ""

        # New-file mode (directory-only selection)
        self._newfile_mode = False
        self.newfile_name_var = None
        self.newfile_name_entry = None
        self.newfile_create_btn = None
        self.newfile_cancel_btn = None
        self.file_open_btn = None

        self.file_path_label = None
        self.file_path_entry = None

        self.file_panel_header = None

        self._build_ui()
        self._bind_shortcuts()
        self._status("Ready. Tip: File → Load from Pi to load any path on your Pi.")

    def runlog_clear(self):
        """Clear the Run log text area."""
        if not getattr(self, "log_text", None):
            return
        try:
            self.log_text.configure(state="normal")
            self.log_text.delete("1.0", "end")
            self.log_text.see("end")
        except Exception:
            pass

    def _term_skip_next_n_lines(self, n=4):
        self._term_skip_lines = max(0, int(n))
        self._term_skip_buffer = ""

    def _refresh_top_header(self):
        """Sync the top header labels with current settings."""
        try:
            if hasattr(self, "currently_editing_var") and self.currently_editing_var is not None:
                self.currently_editing_var.set(self.cfg.remote_path or "")
            if hasattr(self, "venv_display_var") and self.venv_display_var is not None:
                v = (self.cfg.venv_dir or "").strip()
                self.venv_display_var.set(v if v else "No virtual environment used")
        except Exception:
            pass


    # ---------- Editor theming + highlighting ----------
    def _apply_dark_theme_and_highlighting(self):
        """Apply Sublime/Monokai-like dark theme and Python syntax highlighting."""
        # Monokai-ish palette
        bg          = "#272822"
        fg          = "#f8f8f2"
        caret       = "#f8f8f0"
        selection   = "#49483E"
        gutter_bg   = bg
        gutter_fg   = "#8F908A"
        currentline = "#3e3d32"

        # Text widget visuals
        self.text.configure(
            background=bg,
            foreground=fg,
            insertbackground=caret,   # caret color
            selectbackground=selection,
            selectforeground=None,    # keep default logic
            highlightthickness=0,
            borderwidth=0,
        )

        # Line numbers (if present)
        if hasattr(self, "linenumbers") and self.linenumbers:
            self.linenumbers.configure(background=gutter_bg)
            self.linenumbers_redraw_scheduled = False

        # Current line highlight
        self.text.tag_configure("current_line", background=currentline)
        self._highlight_current_line()
        for seq in ("<KeyRelease>", "<ButtonRelease-1>", "<Motion>", "<Configure>", "<MouseWheel>"):
            self.text.bind(seq, lambda e: self._highlight_current_line(), add="+")
        self.text.bind("<<Modified>>", self._on_text_modified, add="+")

        # Syntax highlighting via idlelib (stdlib)
        if Percolator and ColorDelegator:
            cd = ColorDelegator()
            cd.tagdefs.update({
                "COMMENT":     {"foreground": "#75715E"},
                "KEYWORD":     {"foreground": "#F92672"},
                "BUILTIN":     {"foreground": "#66D9EF"},
                "STRING":      {"foreground": "#E6DB74"},
                "DEFINITION":  {"foreground": "#A6E22E"},
                "TODO":        {"foreground": "#CC7832"},
                "ERROR":       {"foreground": "#F44747", "underline": True},
            })
            Percolator(self.text).insertfilter(cd)

    def _highlight_current_line(self):
        self.text.tag_remove("current_line", "1.0", "end")
        self.text.tag_add("current_line", "insert linestart", "insert lineend+1c")

    def _on_text_modified(self, event=None):
        try:
            self.text.edit_modified(False)
        except Exception:
            pass
        if hasattr(self, "linenumbers") and self.linenumbers:
            self.linenumbers.redraw()

    # ---------- UI ----------
    def _build_ui(self):
        self.root.geometry("1500x900")

        # Menubar
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.new_file)
        filemenu.add_command(label="Open local…", command=self.open_local)
        filemenu.add_command(label="Save local", command=self.save_local)
        filemenu.add_separator()
        filemenu.add_command(label="Load from Pi", command=self.open_remote_prompt)
        filemenu.add_command(label="Reload", command=self.load_from_pi)
        filemenu.add_command(label="Save to Pi", command=self.save_to_pi)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        connmenu = tk.Menu(menubar, tearoff=0)
        connmenu.add_command(label="Settings…", command=self.edit_settings)
        connmenu.add_command(label="Test connection", command=self.test_connection)
        menubar.add_cascade(label="Connection", menu=connmenu)

        viewmenu = tk.Menu(menubar, tearoff=0)
        self.wrap_var = tk.BooleanVar(value=False)
        viewmenu.add_checkbutton(label="Word wrap", onvalue=True, offvalue=False,
                                 variable=self.wrap_var, command=self._toggle_wrap)
        # NEW: visibility toggles
        self.show_terminal_var = tk.BooleanVar(value=True)
        self.show_runlog_var   = tk.BooleanVar(value=True)
        viewmenu.add_checkbutton(label="Show SSH Terminal",
                                 variable=self.show_terminal_var,
                                 command=self.toggle_terminal_panel)
        viewmenu.add_checkbutton(label="Show Run Log",
                                 variable=self.show_runlog_var,
                                 command=self.toggle_runlog_panel)

        menubar.add_cascade(label="View", menu=viewmenu)
        self.root.config(menu=menubar)

        # # --- Header: shows the current remote file path ---
        # self.currently_editing_var = tk.StringVar(value=self.cfg.remote_path)
        # header = ttk.Frame(self.root, padding=(8, 4))
        # ttk.Label(header, text="Currently editing:", font=("Menlo", 11, "bold")).pack(side="left")
        # ttk.Label(header, textvariable=self.currently_editing_var, font=("Menlo", 11)).pack(
        #     side="left", fill="x", expand=True, padx=(6, 0)
        # )
        # header.pack(fill="x")


        # --- Header: shows current remote path + venv status ---
        self.currently_editing_var = tk.StringVar()
        self.venv_display_var = tk.StringVar()

        header = ttk.Frame(self.root, padding=(8, 4))
        # Row 1: Currently editing
        ttk.Label(header, text="Currently editing:", font=("Menlo", 11, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(header, textvariable=self.currently_editing_var, font=("Menlo", 11)).grid(
            row=0, column=1, sticky="w", padx=(6, 0)
        )
        # Row 2: Virtual environment
        ttk.Label(header, text="Currently using virtual environment:", font=("Menlo", 10, "bold")).grid(
            row=1, column=0, sticky="w", pady=(2, 0)
        )
        ttk.Label(header, textvariable=self.venv_display_var, font=("Menlo", 10)).grid(
            row=1, column=1, sticky="w", padx=(6, 0), pady=(2, 0)
        )

        header.columnconfigure(1, weight=1)
        header.pack(fill="x")

        # Initialize header values
        self._refresh_top_header()




        # Toolbar
        toolbar = ttk.Frame(self.root, padding=(8, 6))
        self.newfile_btn = ttk.Button(toolbar, text="New File on Pi", command=self.new_file_on_pi)
        self.newfile_btn.pack(side="left", padx=(0,6))
        ttk.Button(toolbar, text="Load from Pi", command=self.toggle_file_panel).pack(side="left", padx=(0,6))
        ttk.Button(toolbar, text="Refresh (⌘L)", command=self.load_from_pi).pack(side="left", padx=(0,6))
        ttk.Button(toolbar, text="Save to Pi (⌘S)", command=self.save_to_pi).pack(side="left", padx=(0,6))
        ttk.Button(toolbar, text="Settings", command=self.toggle_settings_panel).pack(side="left", padx=(0,6))
        ttk.Button(toolbar, text="Test Connection", command=self.test_connection).pack(side="left", padx=(0,6))
        self.run_btn = ttk.Button(toolbar, text="Run on Pi (⌘R)", command=self.run_on_pi)
        self.run_btn.pack(side="left", padx=(0,6))
        self.stop_btn = ttk.Button(toolbar, text="Stop", command=self.stop_remote, state="disabled")
        self.stop_btn.pack(side="left", padx=(0,6))
        self.shutdown_btn = ttk.Button(toolbar, text="Shut Down Pi", command=self.shutdown_pi)
        self.shutdown_btn.pack(side="left", padx=(0,6))
        toolbar.pack(fill="x")

        # Main panes
        self.paned = ttk.Panedwindow(self.root, orient="horizontal")

        self.file_panel = ttk.Frame(self.paned, width=360)
        self._build_file_panel(self.file_panel)

        self.center_frame = ttk.Frame(self.paned)
        self._build_center(self.center_frame)

        self.settings_frame = ttk.Frame(self.paned, width=360)
        self._build_settings_panel(self.settings_frame)

        self.paned.add(self.center_frame, weight=3)
        self.paned.pack(fill="both", expand=True)

        self.status_var = tk.StringVar(value="")
        status = ttk.Label(self.root, textvariable=self.status_var, anchor="w", relief="sunken")
        status.pack(fill="x", side="bottom")


    def shutdown_pi(self):
        """Send a shutdown command to the connected Raspberry Pi."""
        if not messagebox.askyesno(
            "Shut down Raspberry Pi?",
            "This will shut down the remote Pi now.\n\nProceed?"
        ):
            return

        def work():
            try:
                # Ensure SSH is up
                self._connect()
                self._status("Sending shutdown command…")

                # Try passwordless sudo first (no prompt); include common paths/fallbacks
                try_cmds = [
                    "sudo -n /sbin/shutdown -h now",
                    "sudo -n shutdown -h now",
                    "/sbin/shutdown -h now",
                    "shutdown -h now",
                ]

                def _exec_cmd(cmd, with_pty=True, send_pw=None):
                    stdin, stdout, stderr = self.client.exec_command(cmd, get_pty=with_pty)
                    if send_pw is not None:
                        try:
                            stdin.write(send_pw + "\n")
                            stdin.flush()
                        except Exception:
                            pass
                    rc = stdout.channel.recv_exit_status()
                    return rc, stdout.read().decode("utf-8", "ignore"), stderr.read().decode("utf-8", "ignore")

                # 1) No-password attempt
                rc = 1
                for c in try_cmds:
                    rc, _, _ = _exec_cmd(c, with_pty=True)
                    if rc == 0:
                        break

                # 2) If sudo demanded a password, try again with -S.
                if rc != 0:
                    # Prefer stored SSH password if using password auth; otherwise prompt.
                    pw = self.cfg.password if self.cfg.use_password and self.cfg.password else None
                    if pw is None:
                        # Ask the user for a sudo password once (hidden)
                        pw = simpledialog.askstring(
                            "Sudo password required",
                            f"Enter sudo password for {self.cfg.username}@{self.cfg.host}:",
                            show="•"
                        )

                    if pw:
                        sudo_pw_cmds = [
                            "sudo -S -p '' /sbin/shutdown -h now",
                            "sudo -S -p '' shutdown -h now",
                        ]
                        for c in sudo_pw_cmds:
                            rc, _, _ = _exec_cmd(c, with_pty=True, send_pw=pw)
                            if rc == 0:
                                break

                # Let the user know what happened
                if rc == 0:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Shutdown command sent",
                        "The Pi is shutting down. It should power off shortly."
                    ))
                    self._status("Shutdown command sent. Disconnecting…")
                else:
                    self.root.after(0, lambda: messagebox.showwarning(
                        "Shutdown not permitted",
                        "Could not execute shutdown (missing sudo permission or wrong password)."
                    ))
                    self._status("Shutdown was not permitted by the remote system.")

            except Exception as e:
                self._err("Failed to shut down Pi", e)
            finally:
                # Close any running processes/terminal and SSH cleanly
                try:
                    self.stop_remote()
                except Exception:
                    pass
                try:
                    self._close()
                except Exception:
                    pass

        threading.Thread(target=work, daemon=True).start()



    def _on_linenumber_click(self, event):
        idx = self.text.index(f"@0,{event.y} linestart")
        self.text.mark_set("insert", idx)
        self.text.see("insert")
        self.text.focus_set()
        self._highlight_current_line()
        if hasattr(self, "linenumbers") and self.linenumbers:
            self.linenumbers.redraw()


    def _build_runlog(self, parent):
        # LabelFrame inside the right pane
        self.runlog_frame = ttk.LabelFrame(parent, text="Run log")
        self.runlog_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # NEW: toolbar with Clear
        bar = ttk.Frame(self.runlog_frame)
        bar.pack(fill="x", pady=(6, 4))
        ttk.Button(bar, text="Clear", command=self.runlog_clear).pack(side="left")

        self.log_text = tk.Text(self.runlog_frame, height=18, wrap="word", font=("Menlo", 11))
        log_scroll = ttk.Scrollbar(self.runlog_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scroll.pack(side="right", fill="y")
        self.log_text.tag_config("stderr", foreground="red")



    def _build_center(self, parent):
        container = ttk.Frame(parent)
        container.pack(fill="both", expand=True, padx=8, pady=(0,8))

        # ---- Editor (unchanged) ----
        self.text = tk.Text(container, wrap="none", undo=True, font=("Menlo", 12))
        xscroll = ttk.Scrollbar(container, orient="horizontal")
        yscroll = ttk.Scrollbar(container, orient="vertical")

        self.linenumbers = LineNumbers(container, self.text)
        self.linenumbers.grid(row=0, column=0, sticky="ns")

        self.text.grid(row=0, column=1, sticky="nsew")
        yscroll.grid(row=0, column=2, sticky="ns")
        xscroll.grid(row=1, column=1, sticky="ew")

        def _on_yscroll(first, last):
            yscroll.set(first, last)
            if getattr(self, "linenumbers", None):
                self.linenumbers.redraw()

        yscroll.config(command=self.text.yview)
        xscroll.config(command=self.text.xview)
        self.text.configure(xscrollcommand=xscroll.set, yscrollcommand=_on_yscroll)

        container.rowconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)

        # ---- NEW: IO area (Terminal ⟷ Run log) in a horizontal Panedwindow ----
        self.io_paned = ttk.Panedwindow(parent, orient="horizontal")
        self.io_paned.pack(fill="both", expand=False, padx=8, pady=(0,8))

        # Left: Terminal container
        self.term_container = ttk.Frame(self.io_paned)
        self._build_terminal(self.term_container)
        self.io_paned.add(self.term_container, weight=3)

        # Right: Run log container
        self.runlog_container = ttk.Frame(self.io_paned)
        self._build_runlog(self.runlog_container)
        self.io_paned.add(self.runlog_container, weight=2)

        # Dark theme + highlight
        self._apply_dark_theme_and_highlighting()

        # Line number clicks & refreshes (unchanged)
        def _on_linenumber_click(event):
            idx = self.text.index(f"@0,{event.y} linestart")
            self.text.mark_set("insert", idx)
            self.text.see("insert")
            self.text.focus_set()
            self._highlight_current_line()
            if getattr(self, "linenumbers", None):
                self.linenumbers.redraw()
        self.linenumbers.bind("<Button-1>", _on_linenumber_click)

        def _post_click_refresh():
            self._highlight_current_line()
            if getattr(self, "linenumbers", None):
                self.linenumbers.redraw()
        self.text.bind("<Button-1>",  lambda e: (self.text.focus_set(), self.root.after_idle(_post_click_refresh)), add="+")
        self.text.bind("<ButtonRelease-1>", lambda e: self.root.after_idle(_post_click_refresh), add="+")
        for seq in ("<KeyRelease>", "<Configure>", "<MouseWheel>", "<FocusIn>"):
            self.text.bind(seq, lambda e: self.root.after_idle(_post_click_refresh), add="+")
        for seq in ("<Button-4>", "<Button-5>"):
            self.text.bind(seq, lambda e: self.root.after_idle(_post_click_refresh), add="+")


    def _update_io_paned_visibility(self):
        """Hide the entire io_paned if it has no panes; show it otherwise."""
        try:
            panes = self.io_paned.panes()
        except Exception:
            panes = []
        if panes:
            # ensure it's packed
            if not self.io_paned.winfo_manager():
                self.io_paned.pack(fill="both", expand=False, padx=8, pady=(0,8))
        else:
            # hide the whole bar if both are off
            try:
                self.io_paned.pack_forget()
            except Exception:
                pass

        # Keep the View menu checkboxes in sync
        present = set(map(str, panes))
        self.show_terminal_var.set(str(self.term_container) in present)
        self.show_runlog_var.set(str(self.runlog_container) in present)

    def toggle_terminal_panel(self):
        """Show/hide terminal pane based on the View menu checkbox."""
        try:
            panes = list(map(str, self.io_paned.panes()))
        except Exception:
            panes = []
        want_show = self.show_terminal_var.get()
        if want_show and str(self.term_container) not in panes:
            # Put terminal on the left
            if panes:
                self.io_paned.insert(0, self.term_container, weight=3)
            else:
                self.io_paned.add(self.term_container, weight=3)
            self._status("Terminal shown.")
        elif (not want_show) and str(self.term_container) in panes:
            self.io_paned.forget(self.term_container)
            self._status("Terminal hidden.")
        self._update_io_paned_visibility()

    def toggle_runlog_panel(self):
        """Show/hide run log pane based on the View menu checkbox."""
        try:
            panes = list(map(str, self.io_paned.panes()))
        except Exception:
            panes = []
        want_show = self.show_runlog_var.get()
        if want_show and str(self.runlog_container) not in panes:
            # Keep run log to the right
            self.io_paned.add(self.runlog_container, weight=2)
            self._status("Run log shown.")
        elif (not want_show) and str(self.runlog_container) in panes:
            self.io_paned.forget(self.runlog_container)
            self._status("Run log hidden.")
        self._update_io_paned_visibility()


    def _build_terminal(self, parent):
        self.term_frame = ttk.LabelFrame(parent, text="SSH Terminal")
        self.term_frame.pack(fill="both", expand=True, padx=0, pady=0)

        bar = ttk.Frame(self.term_frame)
        bar.pack(fill="x", pady=(6, 4))
        ttk.Button(bar, text="Connect", command=self.term_connect).pack(side="left")
        ttk.Button(bar, text="Disconnect", command=self.term_disconnect).pack(side="left", padx=(6, 0))
        ttk.Button(bar, text="Clear", command=self.term_clear).pack(side="left", padx=(6, 0))

        wrap = ttk.Frame(self.term_frame)
        wrap.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        self.term_text = tk.Text(
            wrap, wrap="none", undo=False, font=("Menlo", 12), height=18,
            background="#111111", foreground="#f0f0f0",
            insertbackground="#f0f0f0", highlightthickness=1, borderwidth=1,
        )
        vsb = ttk.Scrollbar(wrap, orient="vertical", command=self.term_text.yview)
        self.term_text.configure(yscrollcommand=vsb.set)
        self.term_text.pack(side="left", fill="both", expand=True)
        vsb.pack(side="left", fill="y")

        self.term_text.bind("<Key>", self._term_on_key)
        self.term_text.bind("<<Paste>>", self._term_paste)
        self.term_text.bind("<Button-1>", lambda e: self.term_text.focus_set())
        self.term_text.bind("<Configure>", lambda e: self._term_schedule_resize())

        # --- Copy / Paste shortcuts (work across platforms) ---
        # macOS
        self.term_text.bind("<Command-c>", self._term_copy)
        self.term_text.bind("<Command-x>", self._term_copy)   # same as copy (read-only)
        self.term_text.bind("<Command-v>", self._term_paste)

        # Linux/Windows-style terminal shortcuts (so Ctrl-C still sends SIGINT)
        self.term_text.bind("<Control-Shift-C>", self._term_copy)
        self.term_text.bind("<Control-Shift-V>", self._term_paste)

        # Optional: Select all
        self.term_text.bind("<Command-a>", self._term_select_all)
        self.term_text.bind("<Control-Shift-A>", self._term_select_all)

        # Optional: right-click context menu
        self.term_text.bind("<Button-3>", self._term_context_menu)



    def _term_copy(self, event=None):
        try:
            text = self.term_text.get("sel.first", "sel.last")
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
        except Exception:
            pass
        return "break"

    def _term_paste(self, event=None):
        try:
            data = self.root.clipboard_get()
        except Exception:
            return "break"
        # Normalize newlines for shells
        data = data.replace("\r\n", "\n").replace("\r", "\n")
        self._term_send(data)
        return "break"

    def _term_select_all(self, event=None):
        try:
            self.term_text.tag_add("sel", "1.0", "end-1c")
            self.term_text.see("insert")
        except Exception:
            pass
        return "break"

    def _term_context_menu(self, event):
        m = tk.Menu(self.term_text, tearoff=0)
        m.add_command(label="Copy", command=lambda: self._term_copy())
        m.add_command(label="Paste", command=lambda: self._term_paste())
        m.add_separator()
        m.add_command(label="Select All", command=lambda: self._term_select_all())
        try:
            m.tk_popup(event.x_root, event.y_root)
        finally:
            m.grab_release()





    def _build_settings_panel(self, parent):
        self.auth_var = tk.StringVar(value=("password" if self.cfg.use_password else "key"))
        self.host_var = tk.StringVar(value=self.cfg.host)
        self.port_var = tk.StringVar(value=str(self.cfg.port))
        self.user_var = tk.StringVar(value=self.cfg.username)
        self.key_path_var = tk.StringVar(value=self.cfg.key_path)
        self.password_var = tk.StringVar(value=self.cfg.password)
        self.remote_path_var = tk.StringVar(value=self.cfg.remote_path)
        self.python_path_var = tk.StringVar(value=self.cfg.python_path)
        self.venv_dir_var = tk.StringVar(value=self.cfg.venv_dir)

        pad = {"padx": 8, "pady": 6}

        header = ttk.Label(parent, text="Connection Settings", font=("Menlo", 13, "bold"))
        header.grid(row=0, column=0, columnspan=3, sticky="w", **pad)

        ttk.Label(parent, text="Host").grid(row=1, column=0, sticky="e", **pad)
        ttk.Entry(parent, textvariable=self.host_var).grid(row=1, column=1, columnspan=2, sticky="we", **pad)

        ttk.Label(parent, text="Port").grid(row=2, column=0, sticky="e", **pad)
        ttk.Entry(parent, textvariable=self.port_var, width=8).grid(row=2, column=1, sticky="w", **pad)

        ttk.Label(parent, text="Username").grid(row=3, column=0, sticky="e", **pad)
        ttk.Entry(parent, textvariable=self.user_var).grid(row=3, column=1, columnspan=2, sticky="we", **pad)

        ttk.Label(parent, text="Auth").grid(row=4, column=0, sticky="ne", **pad)
        auth_frame = ttk.Frame(parent)
        ttk.Radiobutton(auth_frame, text="SSH key / agent (recommended)", variable=self.auth_var, value="key",
                        command=self._update_auth_state).pack(anchor="w")
        ttk.Radiobutton(auth_frame, text="Password", variable=self.auth_var, value="password",
                        command=self._update_auth_state).pack(anchor="w")
        auth_frame.grid(row=4, column=1, columnspan=2, sticky="we", **pad)

        ttk.Label(parent, text="Key file").grid(row=5, column=0, sticky="e", **pad)
        key_entry = ttk.Entry(parent, textvariable=self.key_path_var)
        key_entry.grid(row=5, column=1, sticky="we", **pad)
        ttk.Button(parent, text="Browse…", command=lambda: self._browse_key_to_var(self.key_path_var)).grid(row=5, column=2, sticky="w", **pad)

        ttk.Label(parent, text="Password").grid(row=6, column=0, sticky="e", **pad)
        self.password_entry = ttk.Entry(parent, textvariable=self.password_var, show="•")
        self.password_entry.grid(row=6, column=1, columnspan=2, sticky="we", **pad)

        ttk.Label(parent, text="Remote file path").grid(row=7, column=0, sticky="e", **pad)
        ttk.Entry(parent, textvariable=self.remote_path_var).grid(row=7, column=1, columnspan=2, sticky="we", **pad)

        ttk.Label(parent, text="Python interpreter (on Pi)").grid(row=8, column=0, sticky="e", **pad)
        ttk.Entry(parent, textvariable=self.python_path_var).grid(row=8, column=1, columnspan=2, sticky="we", **pad)

        ttk.Label(parent, text="Virtualenv directory (on Pi)").grid(row=9, column=0, sticky="e", **pad)
        ttk.Entry(parent, textvariable=self.venv_dir_var).grid(row=9, column=1, columnspan=2, sticky="we", **pad)

        btns = ttk.Frame(parent)
        ttk.Button(btns, text="Apply", command=self.apply_settings_and_hide).pack(side="left", padx=4)
        ttk.Button(btns, text="Test Connection", command=self.test_connection).pack(side="left", padx=4)
        ttk.Button(btns, text="Hide", command=self.toggle_settings_panel).pack(side="left", padx=4)
        btns.grid(row=10, column=0, columnspan=3, pady=8)

        parent.columnconfigure(1, weight=1)
        self._update_auth_state()

    def _hide_remote_path_row(self):
        """Temporarily hide the Remote path row while creating a new file."""
        try:
            if self.file_path_label:
                self.file_path_label.grid_remove()
            if self.file_path_entry:
                self.file_path_entry.grid_remove()
        except Exception:
            pass

    def _show_remote_path_row(self):
        """Restore the Remote path row."""
        try:
            if self.file_path_label:
                self.file_path_label.grid()
            if self.file_path_entry:
                self.file_path_entry.grid()
        except Exception:
            pass


    def _build_file_panel(self, parent):
        padx = 8
        pady = 6

        # Header (dynamic: "Load from Pi" or "New File on Pi")
        self.file_panel_header = ttk.Label(parent, text="Load from Pi", font=("Menlo", 13, "bold"))
        self.file_panel_header.grid(row=0, column=0, columnspan=4, sticky="w", padx=padx, pady=(pady, 0))

        # Remote path row (saved refs so we can hide/show in new-file mode)
        self.file_path_var = tk.StringVar(value=self.cfg.remote_path)
        self.file_path_label = ttk.Label(parent, text="Remote path")
        self.file_path_label.grid(row=1, column=0, sticky="e", padx=padx, pady=pady)

        self.file_path_entry = ttk.Entry(parent, textvariable=self.file_path_var)
        self.file_path_entry.grid(row=1, column=1, columnspan=3, sticky="we", padx=padx, pady=pady)

        ttk.Separator(parent, orient="horizontal").grid(row=2, column=0, columnspan=4, sticky="ew", padx=padx, pady=(0, 6))

        # Top controls: directory field + nav buttons
        top = ttk.Frame(parent)
        top.grid(row=3, column=0, columnspan=4, sticky="ew", padx=padx, pady=(0, 6))
        ttk.Label(top, text="Current directory:").pack(side="left")

        self.file_dir_var = tk.StringVar(value="~")
        dir_entry = ttk.Entry(top, textvariable=self.file_dir_var)
        dir_entry.pack(side="left", fill="x", expand=True, padx=(6, 6))

        ttk.Button(top, text="Go", command=lambda: self._filepanel_populate(self.file_dir_var.get())).pack(side="left")
        ttk.Button(top, text="Back", command=self._filepanel_up).pack(side="left", padx=(6, 0))
        ttk.Button(top, text="Home", command=lambda: self._filepanel_populate("~")).pack(side="left", padx=(6, 0))
        ttk.Button(top, text="Refresh", command=lambda: self._filepanel_populate(self.file_dir_var.get())).pack(side="left", padx=(6, 0))
        ttk.Button(top, text="Hide", command=self.toggle_file_panel).pack(side="right")

        # Split: file list (left) + preview (right)
        paned = ttk.Panedwindow(parent, orient="horizontal")
        left = ttk.Frame(paned)
        right = ttk.Frame(paned)
        paned.grid(row=4, column=0, columnspan=4, sticky="nsew", padx=padx, pady=(0, 6))
        paned.add(left, weight=3)
        paned.add(right, weight=2)

        cols = ("name", "size", "mtime", "kind")
        self.file_tree = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse")
        for c, w in [("name", 320), ("size", 90), ("mtime", 160), ("kind", 80)]:
            self.file_tree.heading(c, text=c.title())
            self.file_tree.column(c, width=w, anchor=("e" if c == "size" else "w"))
        vsb = ttk.Scrollbar(left, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=vsb.set)
        self.file_tree.pack(side="left", fill="both", expand=True, padx=(0, 6))
        vsb.pack(side="left", fill="y")

        ttk.Label(right, text="Preview").pack(anchor="w")
        self.file_preview = tk.Text(right, wrap="word", font=("Menlo", 11), height=10, state="disabled")
        pv_scroll = ttk.Scrollbar(right, orient="vertical", command=self.file_preview.yview)
        self.file_preview.configure(yscrollcommand=pv_scroll.set)
        self.file_preview.pack(side="left", fill="both", expand=True)
        pv_scroll.pack(side="left", fill="y")

        # Footer: normal "Open" OR new-file controls (shown/hidden dynamically)
        btns = ttk.Frame(parent)
        btns.grid(row=5, column=0, columnspan=4, sticky="e", padx=padx, pady=(0, 8))

        # Normal mode: Open
        self.file_open_btn = ttk.Button(btns, text="Open", command=self._filepanel_open_selected)
        self.file_open_btn.pack(side="right")

        # New-file mode widgets (hidden by default)
        self.newfile_name_var = tk.StringVar(value="")
        self.newfile_cancel_btn = ttk.Button(btns, text="Cancel", command=self._exit_newfile_mode)
        self.newfile_create_btn = ttk.Button(btns, text="Create", command=self._filepanel_create_newfile)
        self.newfile_name_entry = ttk.Entry(btns, textvariable=self.newfile_name_var, width=28)

        # Start hidden
        for w in (self.newfile_cancel_btn, self.newfile_create_btn, self.newfile_name_entry):
            w.pack_forget()

        # Layout weights
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(4, weight=1)

        # Init browser state + bindings
        self._file_rows = []
        self._file_selection = None
        self.file_tree.bind("<<TreeviewSelect>>", self._filepanel_on_select)
        self.file_tree.bind("<Double-1>", self._filepanel_on_double_click)









    def new_file_on_pi(self):
        """
        If the file explorer panel is visible, hide it.
        Otherwise, open it in 'new file' mode.
        """
        try:
            panes = self.paned.panes()
            # If the file panel is currently shown, hide it
            if str(self.file_panel) in panes:
                self.paned.forget(self.file_panel)
                self._status("File panel hidden.")
                return

            # Not visible: show panel and switch to 'new file' mode
            self.toggle_file_panel()  # shows the panel + starts population
            self._enter_newfile_mode()
            self._status("Choose a directory on the left, then enter a filename to create.")
        except Exception as e:
            self._err("Open New File panel failed", e)


    def _enter_newfile_mode(self):
        """Switch the footer to 'Create <name>.py' controls and prevent file-open."""
        self._newfile_mode = True
        if self.file_panel_header:
            self.file_panel_header.configure(text="New File on Pi")
        self._hide_remote_path_row()

        if self.file_open_btn:
            try:
                self.file_open_btn.pack_forget()
            except Exception:
                pass
        # Show: [Filename entry] [Create] [Cancel]
        try:
            self.newfile_name_var.set("")
            self.newfile_name_entry.pack(side="right", padx=(0,6))
            self.newfile_create_btn.pack(side="right", padx=(0,6))
            self.newfile_cancel_btn.pack(side="right", padx=(0,6))
            self.newfile_name_entry.focus_set()
        except Exception:
            pass

    def _exit_newfile_mode(self):
        """Restore the footer back to normal 'Open' button."""
        self._newfile_mode = False
        if self.file_panel_header:
            self.file_panel_header.configure(text="Load from Pi")
        self._show_remote_path_row()
        # Hide new-file widgets
        for w in (self.newfile_cancel_btn, self.newfile_create_btn, self.newfile_name_entry):
            try:
                w.pack_forget()
            except Exception:
                pass
        # Restore Open
        try:
            if self.file_open_btn:
                self.file_open_btn.pack(side="right")
        except Exception:
            pass
        self._status("New file action cancelled.")

    def _filepanel_create_newfile(self):
        """Create an empty .py in the current directory shown by the browser, then open it."""
        name = (self.newfile_name_var.get() or "").strip()
        if not name:
            messagebox.showinfo("Filename required", "Please enter a filename (e.g., my_script.py).")
            return
        if "/" in name or "\\" in name:
            messagebox.showwarning("Invalid filename", "Please enter a name without any slashes.")
            return
        if not name.lower().endswith(".py"):
            name += ".py"

        dir_path = (self.file_dir_var.get() or "~").strip()
        # Create in the CURRENT DIRECTORY field (directory-only selection)
        full_path = self._remote_join(self._expand_remote_path(dir_path), name)

        def work():
            try:
                self._connect()
                # Abort if already exists
                try:
                    self.sftp.stat(full_path)
                    self.root.after(0, lambda: messagebox.showwarning(
                        "File already exists",
                        f"{full_path}\n\nChoose a different name."
                    ))
                    return
                except IOError:
                    pass  # does not exist, good

                # Ensure directory exists (should already), then create empty file
                parent = posixpath.dirname(full_path) or "/"
                try:
                    self.sftp.stat(parent)
                except IOError:
                    # If user typed a path that doesn't exist in the dir field, create it
                    self._ensure_remote_dir(parent)

                with self.sftp.open(full_path, "wb") as f:
                    f.write(b"")  # empty file
                try:
                    self.sftp.chmod(full_path, 0o644)
                except Exception:
                    pass

                # Set as target & open in editor
                def after():
                    self._set_remote_path(full_path)
                    self._status(f"Created: {full_path}")
                    # Hide the panel and load the (empty) file
                    try:
                        self.toggle_file_panel()
                    except Exception:
                        pass
                    self.load_from_pi()
                    # Exit new-file mode in case panel is shown again later
                    self._exit_newfile_mode()
                self.root.after(0, after)

            except Exception as e:
                self._err("Failed to create file on Pi", e)

        threading.Thread(target=work, daemon=True).start()




    # ---------- Panel toggles ----------
    def toggle_settings_panel(self):
        try:
            panes = self.paned.panes()
            if str(self.settings_frame) in panes:
                self.paned.forget(self.settings_frame)
            else:
                self.paned.add(self.settings_frame, weight=1)
                self.settings_frame.focus_set()
            self._status("Settings panel toggled.")
        except Exception as e:
            self._err("Toggle settings failed", e)

    def toggle_file_panel(self):
        """Show/hide the 'Load from Pi' / 'New File on Pi' browser panel."""
        try:
            panes = self.paned.panes()
            # Hide if already visible
            if str(self.file_panel) in panes:
                self.paned.forget(self.file_panel)
                self._status("File panel hidden.")
                return

            # Show (insert at the left of the main paned window)
            try:
                self.paned.insert(0, self.file_panel, weight=1)
            except Exception:
                # Fallback: rebuild ordering if needed
                current = list(panes)
                for p in current:
                    self.paned.forget(p)
                self.paned.add(self.file_panel, weight=1)
                self.paned.add(self.center_frame, weight=3)
                if str(self.settings_frame) in panes:
                    self.paned.add(self.settings_frame, weight=1)

            # If this toggle came from the regular "Load from Pi" flow,
            # ensure we are NOT in new-file mode (reset header + show remote path row).
            if self._newfile_mode:
                self._exit_newfile_mode()

            # Focus and populate starting directory
            self.file_panel.focus_set()
            threading.Thread(
                target=lambda: self._filepanel_populate("~"),
                daemon=True
            ).start()
            self._status("File panel opened.")
        except Exception as e:
            self._err("Toggle file panel failed", e)


    def edit_settings(self):
        try:
            if str(self.settings_frame) not in self.paned.panes():
                self.paned.add(self.settings_frame, weight=1)
            self.settings_frame.focus_set()
            self._status("Settings panel opened.")
        except Exception as e:
            self._err("Open settings failed", e)

    def open_remote_prompt(self):
        try:
            if str(self.file_panel) not in self.paned.panes():
                self.toggle_file_panel()
            else:
                self.file_panel.focus_set()
                self._status("File panel already open.")
        except Exception as e:
            self._err("Open file panel failed", e)

    def _bind_shortcuts(self):
        self.root.bind_all("<Command-s>", lambda e: self.save_to_pi())
        self.root.bind_all("<Command-l>", lambda e: self.load_from_pi())
        self.root.bind_all("<Control-s>", lambda e: self.save_to_pi())
        self.root.bind_all("<Control-l>", lambda e: self.load_from_pi())
        self.root.bind_all("<Command-r>", lambda e: self.run_on_pi())
        self.root.bind_all("<Control-r>", lambda e: self.run_on_pi())

    # ---------- Helpers: status & errors ----------
    def _toggle_wrap(self):
        self.text.config(wrap="word" if self.wrap_var.get() else "none")

    def _status(self, msg):
        self.status_var.set(msg)

    def _err(self, title, exc):
        tb = traceback.format_exc()
        messagebox.showerror(title, f"{exc}\n\nDetails:\n{tb}")
        self._status(f"Error: {exc}")

    # ---------- File actions ----------
    def new_file(self):
        if self._maybe_discard_changes():
            self.text.delete("1.0", "end")
            self.local_filepath = None
            self._status("New buffer.")

    def open_local(self):
        path = filedialog.askopenfilename(
            title="Open local file",
            filetypes=[("Python", "*.py"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = f.read()
            self.text.delete("1.0", "end")
            self.text.insert("1.0", data)
            self.local_filepath = path
            self._status(f"Opened local: {os.path.basename(path)}")
        except Exception as e:
            self._err("Failed to open local file", e)

    def save_local(self):
        if not self.local_filepath:
            path = filedialog.asksaveasfilename(
                title="Save local file as…",
                defaultextension=".py",
                filetypes=[("Python", "*.py"), ("All files", "*.*")]
            )
            if not path:
                return
            self.local_filepath = path
        try:
            with open(self.local_filepath, "w", encoding="utf-8") as f:
                f.write(self.text.get("1.0", "end-1c"))
            self._status(f"Saved locally: {os.path.basename(self.local_filepath)}")
        except Exception as e:
            self._err("Failed to save to Pi", e)

    def _maybe_discard_changes(self):
        if self.text.get("1.0", "end-1c").strip():
            return messagebox.askyesno("Discard changes?", "Discard current buffer?")
        return True

    # ---------- SSH / SFTP ----------
    def _connect(self, fresh=False):
        if (not fresh) and self.client and self.sftp:
            return
        self._close()

        self._status("Connecting to Pi…")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            client.connect(
                hostname=self.cfg.host,
                port=self.cfg.port,
                username=self.cfg.username,
                password=self.cfg.password if self.cfg.use_password else None,
                key_filename=self.cfg.key_path or None,
                allow_agent=True,
                look_for_keys=True,
                timeout=10
            )
            transport = client.get_transport()
            if transport:
                transport.set_keepalive(30)
            sftp = client.open_sftp()
            self.client = client
            self.sftp = sftp
            self._cached_remote_home = None
            self._status(f"Connected to {self.cfg.username}@{self.cfg.host}")
        except Exception:
            self._close()
            raise

    def _close(self):
        try:
            if self.sftp:
                self.sftp.close()
        except Exception:
            pass
        try:
            if self.client:
                self.client.close()
        except Exception:
            pass
        self.client = None
        self.sftp = None

    def test_connection(self):
        def work():
            try:
                self._connect(fresh=True)
                stdin, stdout, stderr = self.client.exec_command("whoami && uname -a")
                out = stdout.read().decode("utf-8", "ignore").strip()
                self._status(f"Connected OK. Remote says: {out.splitlines()[0] if out else 'OK'}")
                messagebox.showinfo("Connection OK", out or "Connected.")
            except Exception as e:
                self._err("Connection failed", e)
        threading.Thread(target=work, daemon=True).start()

    def _remote_home(self):
        if self._cached_remote_home:
            return self._cached_remote_home
        try:
            stdin, stdout, stderr = self.client.exec_command("printf %s \"$HOME\"")
            home = stdout.read().decode("utf-8", "ignore").strip()
            if not home:
                home = f"/home/{self.cfg.username}"
            self._cached_remote_home = home
        except Exception:
            self._cached_remote_home = f"/home/{self.cfg.username}"
        return self._cached_remote_home

    def _expand_remote_path(self, path: str) -> str:
        path = (path or "").strip()
        if not path:
            return path
        if path.startswith("~"):
            return path.replace("~", self._remote_home(), 1)
        if not path.startswith("/"):
            return f"{self._remote_home().rstrip('/')}/{path}"
        return path

    # ---------- Remote file ops ----------
    def load_from_pi(self):
        def work():
            try:
                self._connect()
                rp = self._expand_remote_path(self.cfg.remote_path)
                with self.sftp.open(rp, "r") as f:
                    data = f.read().decode("utf-8", "ignore")
                self.root.after(0, lambda: self._load_into_editor(data))
                self._status(f"Loaded from Pi: {rp}")
            except FileNotFoundError:
                self._status("Remote file not found. Creating a new buffer.")
                self.root.after(0, lambda: self.text.delete("1.0", "end"))
                messagebox.showwarning("Not found",
                    f"Remote file not found:\n{self.cfg.remote_path}\n\n"
                    "You can start editing and Save to Pi to create it.")
            except Exception as e:
                self._err("Failed to Reload", e)
        threading.Thread(target=work, daemon=True).start()

    def _load_into_editor(self, data):
        if self._maybe_discard_changes():
            self.text.delete("1.0", "end")
            self.text.insert("1.0", data)

    def save_to_pi(self):
        def work():
            try:
                self._connect()
                rp_cfg = self.cfg.remote_path
                rp = self._expand_remote_path(rp_cfg)
                remote_dir = os.path.dirname(rp).replace("\\", "/") or "."
                self._ensure_remote_dir(remote_dir)
                try:
                    self.sftp.remove(rp + ".tmp")
                except IOError:
                    pass
                data = self.text.get("1.0", "end-1c").encode("utf-8")
                with self.sftp.open(rp, "wb") as f:
                    f.write(data)
                    f.flush()
                self._status(f"Saved to Pi: {rp}")
            except Exception as e:
                self._err("Failed to save to Pi", e)
        threading.Thread(target=work, daemon=True).start()

    def _ensure_remote_dir(self, remote_dir):
        parts = remote_dir.strip("/").split("/")
        cur = ""
        for p in parts:
            cur = f"{cur}/{p}" if cur else f"/{p}"
            try:
                self.sftp.stat(cur)
            except IOError:
                self.sftp.mkdir(cur)

    # ---------- Settings apply ----------
    def _browse_key_to_var(self, var: tk.StringVar):
        path = filedialog.askopenfilename(title="Choose private key",
                                          filetypes=[("Private key", "*"), ("All files", "*.*")])
        if path:
            var.set(path)

    def _update_auth_state(self):
        mode = self.auth_var.get()
        if mode == "password":
            self.password_entry.configure(state="normal")
        else:
            self.password_entry.configure(state="disabled")

    def apply_settings(self):
        try:
            self.cfg.host = self.host_var.get().strip()
            self.cfg.port = int(self.port_var.get().strip() or "22")
            self.cfg.username = self.user_var.get().strip()
            self.cfg.use_password = (self.auth_var.get() == "password")
            self.cfg.password = self.password_var.get() if self.cfg.use_password else ""
            self.cfg.key_path = self.key_path_var.get().strip() if not self.cfg.use_password else ""
            self.cfg.remote_path = self.remote_path_var.get().strip().replace("\\", "/")
            self.cfg.python_path = self.python_path_var.get().strip()
            self.cfg.venv_dir = self.venv_dir_var.get().strip().replace("\\", "/")
            save_config(self.cfg)
            if self.file_path_var is not None:
                self.file_path_var.set(self.cfg.remote_path)
            if hasattr(self, "currently_editing_var") and self.currently_editing_var is not None:
                self.currently_editing_var.set(self.cfg.remote_path)
            self._refresh_top_header()
            self._status("Settings applied.")
            return True
        except Exception as e:
            self._err("Invalid settings", e)
            return False
            
    def apply_settings_and_hide(self):
        if self.apply_settings():
            try:
                # Only hide if the panel is currently shown
                if str(self.settings_frame) in self.paned.panes():
                    self.toggle_settings_panel()
                self._status("Settings applied. Settings panel hidden.")
            except Exception:
                pass


    # ---------- File panel logic ----------
    def _set_remote_path(self, path: str):
        self.cfg.remote_path = path
        save_config(self.cfg)
        if self.remote_path_var is not None:
            self.remote_path_var.set(path)
        if self.file_path_var is not None:
            self.file_path_var.set(path)
        if hasattr(self, "currently_editing_var") and self.currently_editing_var is not None:
            self.currently_editing_var.set(path)
        self._refresh_top_header()

    def _filepanel_up(self):
        cur = self.file_dir_var.get()
        if not cur:
            return
        expanded = self._expand_remote_path(cur)
        parent = posixpath.dirname(expanded.rstrip("/")) or "/"
        self._filepanel_populate(parent)


    def _filepanel_populate(self, path):
        try:
            self._connect()
        except Exception as e:
            self._err("Failed to connect", e)
            return

        path = self._expand_remote_path(path or "~")
        self.file_dir_var.set(path)

        for r in self.file_tree.get_children():
            self.file_tree.delete(r)
        self._file_rows = []
        self._file_selection = None
        self._filepanel_clear_preview()

        try:
            entries = self.sftp.listdir_attr(path)
        except FileNotFoundError:
            messagebox.showerror("Not found", f"Directory not found:\n{path}")
            return
        except Exception as e:
            self._err("Failed to list directory", e)
            return

        def is_dir(attr):
            return stat.S_ISDIR(attr.st_mode)

        entries.sort(key=lambda a: (0 if is_dir(a) else 1, a.filename.lower()))

        def human_size(n):
            try:
                n = int(n)
            except Exception:
                return "-"
            units = ["B","KB","MB","GB","TB","PB"]
            i = 0
            while n >= 1024 and i < len(units)-1:
                n //= 1024
                i += 1
            return f"{n} {units[i]}"

        def human_time(ts):
            try:
                return datetime.datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
            except Exception:
                return "-"

        rows = []
        for a in entries:
            kind = "dir" if is_dir(a) else "file"
            rows.append((a.filename, a.st_size, a.st_mtime, kind))
        self._file_rows = rows

        for name, size, mtime, kind in rows:
            self.file_tree.insert("", "end", values=(name, human_size(size), human_time(mtime), kind))

    def _filepanel_clear_preview(self):
        self.file_preview.configure(state="normal")
        self.file_preview.delete("1.0", "end")
        self.file_preview.configure(state="disabled")

    def _filepanel_on_select(self, event=None):
        sel = self.file_tree.focus()
        if not sel:
            return
        vals = self.file_tree.item(sel, "values")
        if not vals:
            return
        name, _, _, kind = vals
        cwd = self.file_dir_var.get()
        full = self._remote_join(cwd, name)
        self._file_selection = (name, full, kind)
        if kind == "file":
            self.file_path_var.set(full)
            self._filepanel_load_preview(full)
        else:
            self._filepanel_clear_preview()

    def _filepanel_on_double_click(self, event=None):
        sel = self.file_tree.focus()
        if not sel:
            return
        vals = self.file_tree.item(sel, "values")
        if not vals:
            return
        name, _, _, kind = vals
        cwd = self.file_dir_var.get()
        full = self._remote_join(cwd, name)
        if kind == "dir":
            self._filepanel_populate(full)

    def _filepanel_set_selected_only(self):
        if not self._file_selection:
            messagebox.showinfo("Select a file", "Please select a file in the browser.")
            return
        name, full, kind = self._file_selection
        if kind != "file":
            messagebox.showinfo("Select a file", "Please select a file (not a directory).")
            return
        self._set_remote_path(full)
        self._status(f"Target set: {full}")


    def _filepanel_open_selected(self):
        if self._file_selection and self._file_selection[2] == "file":
            _, full, _ = self._file_selection
            self._set_remote_path(full)
            self.load_from_pi()
            # Hide the Load from Pi panel after starting the load
            self.root.after(0, self.toggle_file_panel)
        else:
            p = (self.file_path_var.get() or "").strip()
            if not p:
                messagebox.showinfo("Nothing selected", "Select a file or enter a path to open.")
                return
            self._set_remote_path(p)
            self.load_from_pi()
            # Hide the Load from Pi panel after starting the load
            self.root.after(0, self.toggle_file_panel)


    def _filepanel_load_preview(self, fullpath, limit=128*1024):
        self.file_preview.configure(state="normal")
        self.file_preview.delete("1.0", "end")
        try:
            with self.sftp.open(fullpath, "rb") as f:
                data = f.read(limit)
            TEXTY_EXT = {".txt",".py",".log",".md",".json",".yaml",".yml",".ini",".cfg",".conf",".sh",
                         ".c",".h",".cpp",".hpp",".js",".ts",".html",".css",".xml",".toml",".csv",".sql"}
            if b"\x00" in data and posixpath.splitext(fullpath.lower())[1] not in TEXTY_EXT:
                self.file_preview.insert("1.0", "[binary file — preview disabled]")
            else:
                try:
                    txt = data.decode("utf-8", "ignore")
                except Exception:
                    txt = data.decode("latin-1", "ignore")
                self.file_preview.insert("1.0", txt)
        except Exception as e:
            self.file_preview.insert("1.0", f"[preview error] {e}")
        self.file_preview.configure(state="disabled")

    def _remote_join(self, a, b):
        a = (a or "/")
        if not a or a == "/":
            return f"/{b}".replace("//", "/")
        return f"{a.rstrip('/')}/{b}".replace("//", "/")

    # ---------- Run on Pi ----------
    def _exec(self, cmd: str, get_pty: bool = False):
        stdin, stdout, stderr = self.client.exec_command(cmd, get_pty=get_pty)
        out = stdout.read().decode("utf-8", "ignore")
        err = stderr.read().decode("utf-8", "ignore")
        rc = stdout.channel.recv_exit_status()
        return rc, out, err

    def _ensure_remote_venv(self, venv_dir: str) -> str:
        venv_dir = self._expand_remote_path(venv_dir)
        quoted = shlex.quote(venv_dir)

        rc, _, _ = self._exec(f"test -x {quoted}/bin/python")
        if rc == 0:
            return venv_dir

        self._append_log(f"[venv] Creating virtual environment at {venv_dir} …")
        self._exec(f"mkdir -p {quoted}")

        rc, _, err1 = self._exec(f"python3 -m venv {quoted}")
        if rc != 0:
            rc2, _, err2 = self._exec(f"virtualenv {quoted}")
            if rc2 != 0:
                raise RuntimeError(
                    "Failed to create virtual environment on the Pi.\n"
                    "Try installing one of:\n"
                    "  sudo apt-get update && sudo apt-get install -y python3-venv\n"
                    "  pip3 install --user virtualenv\n\n"
                    f"python3 -m venv error:\n{err1}\n\nvirtualenv error:\n{err2}"
                )

        rc, _, _ = self._exec(f"test -x {quoted}/bin/python")
        if rc != 0:
            raise RuntimeError("Virtual environment was created, but bin/python is missing.")
        self._append_log("[venv] Virtual environment ready.")
        return venv_dir

    def _append_log(self, text, kind="stdout"):
        def do():
            tag = "stderr" if kind == "stderr" else None
            if tag:
                self.log_text.insert("end", text, tag)
            else:
                self.log_text.insert("end", text)
            if not text.endswith("\n"):
                self.log_text.insert("end", "\n", tag)
            self.log_text.see("end")
        self.root.after(0, do)

    def _set_running(self, running: bool):
        self._running = running
        def do():
            self.run_btn.config(state="disabled" if running else "normal")
            self.stop_btn.config(state="normal" if running else "disabled")
            if running:
                self._status("Running on Pi… (watch the log)")
            else:
                self._status("Finished.")
        self.root.after(0, do)

    def run_on_pi(self):
        if self._running:
            return
        self._set_running(True)

        def work():
            try:
                self._connect()
                rp = self._expand_remote_path(self.cfg.remote_path)
                script_dir = posixpath.dirname(rp) or self._remote_home()
                script_base = posixpath.basename(rp)

                if self.cfg.venv_dir.strip():
                    try:
                        venv_path = self._ensure_remote_venv(self.cfg.venv_dir.strip())
                        activate_path = f"{venv_path}/bin/activate"
                        rc, _, _ = self._exec(f"test -r {shlex.quote(activate_path)}")
                        if rc != 0:
                            raise RuntimeError(f"Virtualenv activation script not found: {activate_path}")
                        py_after_activate = (self.cfg.python_path.strip() or "python")
                        inner_cmd = (
                            f"cd {shlex.quote(script_dir)} && "
                            f"source {shlex.quote(activate_path)} && "
                            f"{shlex.quote(py_after_activate)} -u {shlex.quote(script_base)}"
                        )
                    except Exception as ve:
                        self._append_log(f"[venv error] {ve}", "stderr")
                        self._set_running(False)
                        return
                else:
                    python_cmd = (self.cfg.python_path.strip() or "python3")
                    inner_cmd = f"cd {shlex.quote(script_dir)} && {shlex.quote(python_cmd)} -u {shlex.quote(script_base)}"

                cmd = f"bash -lc {shlex.quote(inner_cmd)}"
                self._append_log(f"$ {inner_cmd}")

                stdin, stdout, stderr = self.client.exec_command(cmd, get_pty=True)
                chan = stdout.channel
                self._run_channel = chan

                while True:
                    if chan.recv_ready():
                        out = chan.recv(4096)
                        if out:
                            self._append_log(out.decode("utf-8", "ignore"), "stdout")
                    if chan.recv_stderr_ready():
                        err = chan.recv_stderr(4096)
                        if err:
                            self._append_log(err.decode("utf-8", "ignore"), "stderr")
                    if chan.exit_status_ready() and not chan.recv_ready() and not chan.recv_stderr_ready():
                        break
                    time.sleep(0.05)

                code = chan.recv_exit_status()
                self._append_log(f"[process exited with code {code}]")

            except Exception as e:
                self._append_log(f"[run error] {e}", "stderr")
                self._err("Run failed", e)
            finally:
                self._run_channel = None
                self._set_running(False)

        self._run_thread = threading.Thread(target=work, daemon=True)
        self._run_thread.start()

    def stop_remote(self):
        if self._run_channel is not None:
            try:
                self._run_channel.close()
                self._append_log("[process terminated]")
            except Exception:
                pass
        self._set_running(False)

        # Also stop the interactive terminal if running
        if self._term_chan is not None:
            try:
                self._term_chan.close()
            except Exception:
                pass
        self._term_running = False
        self._term_chan = None
        self._term_connected_var.set(False)

    # ---------- Terminal helpers ----------
    def term_connect(self):
        """Open an interactive PTY shell on the Pi and start streaming."""
        if self._term_running:
            self._status("Terminal already connected.")
            return
        try:
            self._connect()
        except Exception as e:
            self._err("Terminal connect failed", e)
            return

        cols, rows = self._term_measure_size()
        try:
            chan = self.client.invoke_shell(term='xterm-256color', width=cols, height=rows)
            chan.settimeout(0.0)  # non-blocking
        except Exception as e:
            self._err("Failed to start remote shell", e)
            return

        self._term_chan = chan
        self._term_running = True
        self._term_connected_var.set(True)
        self.term_text.focus_set()
        self._status("Terminal connected. Type commands here.")

        # Make Backspace map to DEL and prevent XON/XOFF from hijacking Ctrl-S/Q
        # self._term_send("stty -ixon erase ^?\r")

        # Show a tidy context line instead of echoing init commands
        self.term_clear(initial=True)


        # Reader thread
        def reader():
            try:
                while self._term_running and self._term_chan is not None and not self._term_chan.closed:
                    try:
                        if self._term_chan.recv_ready():
                            data = self._term_chan.recv(4096)
                            if data:
                                self._term_write_bytes(data)
                        if self._term_chan.recv_stderr_ready():
                            data = self._term_chan.recv_stderr(4096)
                            if data:
                                self._term_write_bytes(data)
                        if self._term_chan.exit_status_ready():
                            break
                    except Exception:
                        pass
                    time.sleep(0.01)
            finally:
                self.root.after(0, lambda: self._status("Terminal closed."))
                self._term_running = False
                self._term_chan = None
                self._term_connected_var.set(False)

        self._term_thread = threading.Thread(target=reader, daemon=True)
        self._term_thread.start()
        self._term_schedule_resize(delay_ms=10)

    def term_disconnect(self):
        if self._term_chan is not None:
            try:
                self._term_chan.close()
            except Exception:
                pass
        self._term_running = False
        self._term_chan = None
        self._term_connected_var.set(False)
        self._status("Terminal disconnected.")


    def term_clear(self, *, initial=False):
        """Clear local view but keep user@host:cwd visible."""
        if not self.term_text:
            return

        # Local clear
        self.term_text.configure(state="normal")
        self.term_text.delete("1.0", "end")
        self.term_text.configure(state="normal")

        # Skip the echoed command line only (or 4 lines on first clear after connect)
        if initial:
            self._term_skip_next_n_lines()
        else:
            self._term_skip_next_n_lines(2)

        # Print user@host:cwd and a blank line; shell then shows a fresh prompt
        self._term_send("printf '%s@%s:%s\\n\\n' \"$USER\" \"$(hostname)\" \"$PWD\"\r")




    def _term_write_bytes(self, data: bytes):
        try:
            text = data.decode("utf-8", "ignore")
        except Exception:
            text = data.decode("latin-1", "ignore")

        text = text.replace("\r\n", "\n")
        parts = text.split("\r")

        def ui():
            self.term_text.configure(state="normal")
            for i, part in enumerate(parts):
                if i > 0:
                    self.term_text.delete("end-1c linestart", "end-1c")

                clean = self._ansi_re.sub("", part)
                clean = self._osc_re.sub("", clean).replace("\x07", "")

                j = 0
                while j < len(clean):
                    ch = clean[j]

                    # --- SKIP FIRST N LINES AFTER CONNECT/CLEAR ---
                    if self._term_skip_lines > 0:
                        if ch == "\n":
                            self._term_skip_lines -= 1
                        j += 1
                        continue
                    # ------------------------------------------------

                    if ch == "\x08":  # Backspace
                        try:
                            prev = self.term_text.get("end-2c", "end-1c")
                        except Exception:
                            prev = ""
                        if prev and prev != "\n":
                            try:
                                self.term_text.delete("end-2c", "end-1c")
                            except Exception:
                                pass
                    else:
                        self.term_text.insert("end", ch)
                    j += 1

            self.term_text.see("end")
            self.term_text.configure(state="normal")

        self.root.after(0, ui)


    def _term_send(self, s: str):
        if self._term_chan is None or self._term_chan.closed:
            return
        try:
            self._term_chan.send(s)
        except Exception:
            pass

    def _term_on_paste(self, event=None):
        try:
            data = self.root.clipboard_get()
        except Exception:
            return "break"
        data = data.replace("\r\n", "\n").replace("\r", "\n")
        self._term_send(data)
        return "break"

    def _term_on_key(self, event):
        """Capture keystrokes and forward raw bytes / escape sequences to PTY."""
        if self._term_chan is None:
            return "break"

        ks = event.keysym
        ch = event.char
        ctrl = bool(event.state & 0x0004)

        # Printable chars
        if ch and ord(ch) >= 32 and ch != "\x7f":
            self._term_send(ch)
            return "break"

        # Enter / Backspace / Tab
        if ks in ("Return", "KP_Enter"):
            self._term_send("\r"); return "break"
        if ks == "BackSpace":
            # Send DEL (0x7f); stty erase ^? on connect makes this work
            self._term_send("\x7f"); return "break"
        if ks == "Tab":
            self._term_send("\t"); return "break"

        # Ctrl-H fallback behaves like backspace on many setups
        if ctrl and ks.lower() == "h":
            self._term_send("\x08"); return "break"  # BS

        # Ctrl-C / Ctrl-D / Ctrl-Z / Ctrl-L etc.
        if ctrl and ks.lower() == "c":
            self._term_send("\x03"); return "break"
        if ctrl and ks.lower() == "d":
            self._term_send("\x04"); return "break"
        if ctrl and ks.lower() == "z":
            self._term_send("\x1a"); return "break"
        if ctrl and ks.lower() == "l":
            self._term_send("\x0c"); return "break"  # remote 'clear'

        # Arrows & navigation (VT100 sequences)
        esc_map = {
            # "Up":    "\x1b[A",
            # "Down":  "\x1b[B",
            # "Right": "\x1b[C",
            # "Left":  "\x1b[D",
            "Home":  "\x1b[H",
            "End":   "\x1b[F",
            "Delete": "\x1b[3~",   # Forward delete
            "Insert": "\x1b[2~",
            "Prior":  "\x1b[5~",   # PageUp
            "Next":   "\x1b[6~",   # PageDown
        }
        if ks in esc_map:
            self._term_send(esc_map[ks]); return "break"

        return "break"

    def _term_measure_size(self):
        if not self.term_text:
            return (80, 24)
        try:
            f = tkfont.Font(font=self.term_text["font"])
            cw = max(1, f.measure("M"))
            ch = max(1, f.metrics("linespace"))
            w = max(1, self.term_text.winfo_width())
            h = max(1, self.term_text.winfo_height())
            cols = max(20, int(w / cw))
            rows = max(5, int(h / ch))
            return (cols, rows)
        except Exception:
            return (80, 24)

    def _term_schedule_resize(self, delay_ms=150):
        if self._term_chan is None:
            return
        if self._term_pending_resize:
            return
        self._term_pending_resize = True
        def do():
            self._term_pending_resize = False
            cols, rows = self._term_measure_size()
            try:
                self._term_chan.resize_pty(width=cols, height=rows)
            except Exception:
                pass
        self.root.after(delay_ms, do)


def run():
    root = tk.Tk()
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass
    app = PiEditorApp(root)
    root.mainloop()

if __name__ == "__main__":
    run()
