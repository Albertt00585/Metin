"""Aplicatie desktop: adaugi un nume, apoi scrii pe pagina acelui nume.

Porneste cu dublu-click pe "Organizare Metin.pyw" (sau: python "Organizare Metin.pyw").
Necesita: pip install customtkinter
Textele se salveaza automat in %APPDATA%\\Metin\\note.json.
Installer + update-uri: vezi build.ps1 si README.md.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import urllib.request

import customtkinter as ctk

APP_NAME = "Organizare Metin"
APP_VERSION = "1.0.1"
# Repository-ul GitHub de unde aplicatia instalata isi ia update-urile ("utilizator/repo").
UPDATE_REPO = "Albertt00585/Metin"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# folderul de date ramane "Metin" si dupa redenumire, ca notitele existente sa fie gasite
DATA_DIR = os.path.join(os.environ.get("APPDATA") or BASE_DIR, "Metin")
DATA_PATH = os.path.join(DATA_DIR, "note.json")
UPDATE_DIR = os.path.join(os.environ.get("LOCALAPPDATA") or BASE_DIR, "Metin", "updates")
FROZEN = getattr(sys, "frozen", False)  # True cand ruleaza ca aplicatie instalata (.exe)
ICON_PATH = os.path.join(getattr(sys, "_MEIPASS", BASE_DIR), "assets", "metin.ico")

# Tema "Ametist"
BG = "#141022"
CARD = "#1d182f"
BORDER = "#2e2648"
INPUT = "#141022"
INPUT_BORDER = "#352c52"
ROW = "#251f3a"
ROW_HOVER = "#2e2648"
TEXT = "#ece8f7"
TEXT_SOFT = "#d6cff0"
MUTED = "#9a90b8"
ACCENT = "#9b7cf6"
ACCENT_HOVER = "#8a68ef"
DANGER = "#f07a9a"
DANGER_HOVER = "#3a1f33"

FAMILY = "Segoe UI"
RADIUS = 14


def load_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    old_path = os.path.join(BASE_DIR, "note.json")  # locatia veche, langa fisierul .pyw
    if not os.path.exists(DATA_PATH) and os.path.exists(old_path):
        shutil.copy2(old_path, DATA_PATH)
    try:
        with open(DATA_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_data(data):
    # scriere atomica: fisierul vechi e inlocuit doar dupa ce cel nou e scris complet pe disc
    tmp = DATA_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, DATA_PATH)


def parse_version(text):
    return tuple(int(n) for n in re.findall(r"\d+", text)[:3])


def fetch_latest_release():
    """Intoarce (versiune, url_installer, marime) daca pe GitHub exista o versiune mai noua, altfel None."""
    url = f"https://api.github.com/repos/{UPDATE_REPO}/releases/latest"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "Metin"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        release = json.load(resp)
    version = release.get("tag_name", "")
    if parse_version(version) <= parse_version(APP_VERSION):
        return None
    for asset in release.get("assets", []):
        if asset["name"].lower().endswith(".exe"):
            return version.lstrip("v"), asset["browser_download_url"], asset["size"]
    return None


def download_update(version, url, size):
    """Descarca installer-ul in UPDATE_DIR; intoarce calea doar daca fisierul e complet."""
    os.makedirs(UPDATE_DIR, exist_ok=True)
    path = os.path.join(UPDATE_DIR, f"OrganizareMetinSetup-{version}.exe")
    if os.path.exists(path) and os.path.getsize(path) == size:
        return path  # descarcat deja la o pornire anterioara
    for name in os.listdir(UPDATE_DIR):  # curatam versiunile/descarcarile vechi
        os.remove(os.path.join(UPDATE_DIR, name))
    urllib.request.urlretrieve(url, path + ".part")
    if os.path.getsize(path + ".part") != size:
        os.remove(path + ".part")
        return None
    os.replace(path + ".part", path)
    return path


def backup_data():
    if os.path.exists(DATA_PATH):
        shutil.copy2(DATA_PATH, os.path.join(DATA_DIR, "note.backup.json"))


def font(size, bold=False):
    return ctk.CTkFont(family=FAMILY, size=size, weight="bold" if bold else "normal")


class ConfirmDialog(ctk.CTkToplevel):
    """Fereastra de confirmare in tema aplicatiei (in locul celei albe din Windows)."""

    def __init__(self, master, title, message, confirm_text):
        super().__init__(master, fg_color=BG)
        self.result = False
        self.title(title)
        self.resizable(False, False)
        self.transient(master)

        card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=RADIUS, border_width=1, border_color=BORDER)
        card.pack(padx=16, pady=16, fill="both", expand=True)
        ctk.CTkLabel(card, text=title, font=font(16, True), text_color=TEXT).pack(anchor="w", padx=20, pady=(18, 4))
        ctk.CTkLabel(card, text=message, font=font(13), text_color=MUTED, wraplength=320, justify="left"
                     ).pack(anchor="w", padx=20)

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(18, 18))
        ctk.CTkButton(row, text=confirm_text, command=self.confirm, font=font(13, True), height=36,
                      corner_radius=10, fg_color=DANGER, hover_color="#e0607f", text_color="#2a0f1a"
                      ).pack(side="right")
        ctk.CTkButton(row, text="Anulează", command=self.destroy, font=font(13), height=36, corner_radius=10,
                      fg_color=ROW, hover_color=ROW_HOVER, text_color=TEXT_SOFT).pack(side="right", padx=(0, 8))

        self.bind("<Escape>", lambda _e: self.destroy())
        self.after(50, self.grab_set)

    def confirm(self):
        self.result = True
        self.destroy()


class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=BG)
        self.title(APP_NAME)
        self.geometry("760x560")
        self.minsize(460, 400)
        if os.path.exists(ICON_PATH):
            # customtkinter isi pune propria iconita dupa ~200 ms, asa ca o punem pe a noastra dupa
            self.after(300, lambda: self.iconbitmap(ICON_PATH))
        self.data = load_data()
        self.current = None
        self.frame = None
        self.save_job = None
        self.pending_update = None
        self.update_result = None
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.show_names()
        if FROZEN and UPDATE_REPO:
            threading.Thread(target=self.check_for_update, daemon=True).start()
            self.poll_update()

    # ---------- update-uri ----------
    # Versiunea noua se descarca in fundal; se instaleaza abia cand inchizi aplicatia,
    # dupa ce tot textul a fost salvat. Nu se reporneste nimic si nu apare nicio fereastra.
    def check_for_update(self):
        # ruleaza pe alt thread: nu atinge fereastra, doar lasa rezultatul pentru poll_update
        try:
            found = fetch_latest_release()
            path = download_update(*found) if found else None
        except Exception:
            return  # fara internet / GitHub indisponibil -> incercam la urmatoarea pornire
        if path:
            self.update_result = (found[0], path)

    def poll_update(self):
        if self.update_result:
            self.update_ready(*self.update_result)
        else:
            self.after(1000, self.poll_update)

    def update_ready(self, version, path):
        self.pending_update = path
        note = ctk.CTkLabel(self, text=f"Versiunea {version} e pregătită · se instalează când închizi aplicația",
                            font=font(11), text_color=MUTED, height=22)
        note.pack(side="bottom", anchor="e", padx=22, pady=(0, 6), before=self.frame)

    def install_pending_update(self):
        if not self.pending_update or not os.path.exists(self.pending_update):
            return
        backup_data()
        try:
            subprocess.Popen([self.pending_update, "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART",
                              "/norelaunch=1"])
        except OSError:
            pass  # incercam din nou la urmatoarea inchidere

    def swap(self, frame):
        if self.frame:
            self.frame.destroy()
        self.frame = frame
        frame.pack(fill="both", expand=True)

    # ---------- ecranul cu nume ----------
    def show_names(self):
        self.current = None
        self.title(APP_NAME)
        outer = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        card = ctk.CTkFrame(outer, fg_color=CARD, corner_radius=RADIUS + 4, border_width=1, border_color=BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center")
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=28, pady=26)

        ctk.CTkLabel(inner, text="Adaugă un nume", font=font(22, True), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(inner, text="După ce adaugi numele, se deschide pagina unde poți scrie.",
                     font=font(12), text_color=MUTED).pack(anchor="w", pady=(2, 16))

        entry = ctk.CTkEntry(inner, width=340, height=42, corner_radius=12, font=font(14),
                             fg_color=INPUT, border_color=INPUT_BORDER, border_width=1, text_color=TEXT,
                             placeholder_text="Ex: Ion Popescu", placeholder_text_color=MUTED)
        entry.pack(fill="x")
        error = ctk.CTkLabel(inner, text="", font=font(12), text_color=DANGER, height=18)
        error.pack(anchor="w", pady=(4, 0))

        def add(_event=None):
            name = entry.get().strip()
            if not name:
                error.configure(text="Scrie un nume înainte să apeși Adaugă.")
                entry.configure(border_color=DANGER)
                return
            if name not in self.data:
                self.data[name] = ""
                save_data(self.data)
            self.show_editor(name)

        def clear_error(_event=None):
            if error.cget("text"):
                error.configure(text="")
                entry.configure(border_color=INPUT_BORDER)

        entry.bind("<Return>", add)
        entry.bind("<Key>", clear_error)
        ctk.CTkButton(inner, text="Adaugă", command=add, height=42, corner_radius=12, font=font(14, True),
                      fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color="#ffffff").pack(fill="x", pady=(2, 0))

        if self.data:
            ctk.CTkLabel(inner, text="NUMELE TALE", font=font(11, True), text_color=MUTED
                         ).pack(anchor="w", pady=(22, 6))
            if len(self.data) <= 4:
                listing = ctk.CTkFrame(inner, fg_color="transparent")
            else:
                listing = ctk.CTkScrollableFrame(inner, fg_color="transparent", height=4 * 50, corner_radius=0,
                                                 scrollbar_button_color=ROW, scrollbar_button_hover_color=ROW_HOVER)
            listing.pack(fill="x")
            for name in self.data:
                self.name_row(listing, name)

        self.after(100, entry.focus_set)
        self.swap(outer)

    def name_row(self, master, name):
        row = ctk.CTkFrame(master, fg_color=ROW, corner_radius=12, border_width=1, border_color=BORDER)
        row.pack(fill="x", pady=(0, 6))
        words = len(self.data[name].split())
        ctk.CTkButton(row, text=f"{name}", anchor="w", command=lambda: self.show_editor(name),
                      font=font(14), height=38, corner_radius=10, fg_color="transparent",
                      hover_color=ROW_HOVER, text_color=TEXT).pack(side="left", fill="x", expand=True, padx=(4, 0), pady=3)
        ctk.CTkLabel(row, text=f"{words} cuvinte", font=font(11), text_color=MUTED).pack(side="left", padx=6)
        ctk.CTkButton(row, text="✕", width=32, height=32, corner_radius=10, font=font(13),
                      fg_color="transparent", hover_color=DANGER_HOVER, text_color=MUTED,
                      command=lambda: self.delete_name(name)).pack(side="right", padx=(0, 6))

    def delete_name(self, name):
        dialog = ConfirmDialog(self, "Șterge numele",
                               f"Ștergi \"{name}\" și tot ce ai scris pentru el? Nu se mai poate recupera.",
                               "Șterge")
        self.wait_window(dialog)
        if dialog.result:
            del self.data[name]
            save_data(self.data)
            self.show_names()

    # ---------- pagina de scris ----------
    def show_editor(self, name):
        self.current = name
        self.title(f"{APP_NAME} · {name}")
        outer = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        pad = ctk.CTkFrame(outer, fg_color="transparent")
        pad.pack(fill="both", expand=True, padx=20, pady=16)

        top = ctk.CTkFrame(pad, fg_color="transparent")
        top.pack(fill="x", pady=(0, 12))
        ctk.CTkButton(top, text="←  Înapoi", command=self.back, width=96, height=34, corner_radius=10,
                      font=font(13), fg_color=ROW, hover_color=ROW_HOVER, text_color=TEXT_SOFT,
                      border_width=1, border_color=BORDER).pack(side="left")
        ctk.CTkLabel(top, text=name, font=font(20, True), text_color=TEXT).pack(side="left", padx=14)
        self.status = ctk.CTkLabel(top, text="", font=font(12), text_color=MUTED)
        self.status.pack(side="right")

        self.text = ctk.CTkTextbox(pad, corner_radius=RADIUS + 2, border_width=1, border_color=BORDER,
                                   fg_color=CARD, text_color=TEXT_SOFT, font=font(15), wrap="word",
                                   border_spacing=18, undo=True, spacing1=2, spacing3=6,
                                   scrollbar_button_color=ROW, scrollbar_button_hover_color=ROW_HOVER)
        self.text.pack(fill="both", expand=True)
        self.text._textbox.configure(insertbackground=ACCENT, insertwidth=2, selectbackground="#4a3a80")
        self.text.insert("1.0", self.data.get(name, ""))
        self.text.edit_modified(False)
        self.text.bind("<<Modified>>", self.on_modified)
        self.text._textbox.bind("<Return>", self.on_enter)
        self.update_status("Salvat")

        self.swap(outer)
        self.after(100, self.text.focus_set)

    # Un rand care incepe cu "1" / "1." / "1)" sau cu "- " + Enter -> randul urmator incepe cu "- ".
    # Enter pe o liniuta goala (doar "- ") opreste lista.
    LIST_ITEM = re.compile(r"^(\s*)(\d{1,3}[.)]?|-)(\s.*|)$")

    def on_enter(self, _event=None):
        box = self.text._textbox
        line = box.get("insert linestart", "insert lineend")
        match = self.LIST_ITEM.match(line)
        if not match:
            return None
        indent, marker, rest = match.groups()
        box.edit_separator()
        if marker == "-" and not rest.strip():
            # liniuta goala -> iesire din lista
            box.delete("insert linestart", "insert lineend")
        else:
            box.insert("insert", f"\n{indent}- ")
        box.see("insert")
        return "break"

    def update_status(self, state):
        words = len(self.text.get("1.0", "end-1c").split())
        self.status.configure(text=f"{words} cuvinte  ·  {state}")

    def on_modified(self, _event=None):
        if not self.text.edit_modified():
            return
        self.text.edit_modified(False)
        self.update_status("Se salvează…")
        if self.save_job:
            self.after_cancel(self.save_job)
        self.save_job = self.after(600, self.save_now)

    def save_now(self):
        if self.save_job:
            self.after_cancel(self.save_job)
        self.save_job = None
        if self.current is None:
            return
        self.data[self.current] = self.text.get("1.0", "end-1c")
        save_data(self.data)
        self.update_status("Salvat")

    def back(self):
        self.save_now()
        self.show_names()

    def on_close(self):
        # ordinea conteaza: intai salvam tot textul, abia apoi pornim update-ul
        if self.current is not None:
            self.save_now()
        self.install_pending_update()
        self.destroy()


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    App().mainloop()
