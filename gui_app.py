from __future__ import annotations

import csv
import re
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from detector import PlateDetection, detect_plates


UK_PLATE_PATTERN = re.compile(r"^[A-Z]{2}[0-9]{2}[A-Z]{3}$")


class PlatePatrolApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("PlatePatrol - UK Plate Review")
        self.root.geometry("980x560")

        self.video_path_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Select a video and click Run Detection.")
        self.selected_plate_var = tk.StringVar(value="-- ---- ---")

        self.plates: list[dict] = []

        self._build_ui()

    def _build_ui(self) -> None:
        controls = ttk.Frame(self.root, padding=12)
        controls.pack(fill="x")

        ttk.Label(controls, text="Video:").pack(side="left")
        ttk.Entry(controls, textvariable=self.video_path_var, width=70).pack(side="left", padx=6)
        ttk.Button(controls, text="Browse", command=self.browse_video).pack(side="left")
        ttk.Button(controls, text="Run Detection", command=self.run_detection).pack(side="left", padx=6)
        ttk.Button(controls, text="Load CSV", command=self.load_csv).pack(side="left", padx=6)
        ttk.Button(controls, text="Save Corrections", command=self.save_csv).pack(side="left", padx=6)

        content = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        content.pack(fill="both", expand=True, padx=12, pady=12)

        left = ttk.Frame(content)
        right = ttk.Frame(content)
        content.add(left, weight=3)
        content.add(right, weight=2)

        columns = ("car_id", "plate", "confidence")
        self.table = ttk.Treeview(left, columns=columns, show="headings", height=20)
        self.table.heading("car_id", text="Car ID")
        self.table.heading("plate", text="Detected Plate")
        self.table.heading("confidence", text="OCR Confidence")
        self.table.column("car_id", width=100, anchor="center")
        self.table.column("plate", width=220, anchor="center")
        self.table.column("confidence", width=120, anchor="center")
        self.table.pack(fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.on_select)

        plate_frame = tk.Frame(right, bd=2, relief="groove", bg="#f4c300", width=330, height=150)
        plate_frame.pack(pady=20)
        plate_frame.pack_propagate(False)

        blue_strip = tk.Frame(plate_frame, width=36, bg="#1b3f8b")
        blue_strip.pack(side="left", fill="y")
        tk.Label(blue_strip, text="UK", bg="#1b3f8b", fg="white", font=("Segoe UI", 10, "bold")).pack(
            pady=8
        )

        plate_label = tk.Label(
            plate_frame,
            textvariable=self.selected_plate_var,
            bg="#f4c300",
            fg="black",
            font=("Consolas", 36, "bold"),
        )
        plate_label.pack(side="left", fill="both", expand=True)

        editor = ttk.LabelFrame(right, text="Correct selected plate", padding=12)
        editor.pack(fill="x", padx=6, pady=8)

        self.correct_var = tk.StringVar()
        ttk.Entry(editor, textvariable=self.correct_var, width=24).grid(row=0, column=0, padx=4)
        ttk.Button(editor, text="Apply Correction", command=self.apply_correction).grid(row=0, column=1, padx=4)
        ttk.Label(editor, text="Format: AA00AAA").grid(row=1, column=0, columnspan=2, pady=6)

        ttk.Label(self.root, textvariable=self.status_var, padding=(12, 0, 12, 10)).pack(fill="x")

    def browse_video(self) -> None:
        path = filedialog.askopenfilename(
            title="Choose video",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")],
        )
        if path:
            self.video_path_var.set(path)

    def run_detection(self) -> None:
        video_path = self.video_path_var.get().strip()
        if not video_path:
            messagebox.showwarning("Missing video", "Please choose a video file first.")
            return

        self.status_var.set("Detecting plates... this can take several minutes.")
        threading.Thread(target=self._detect_worker, args=(video_path,), daemon=True).start()

    def _detect_worker(self, video_path: str) -> None:
        try:
            detections = detect_plates(video_path, output_csv_path="test.csv")
            self.root.after(0, lambda: self._set_detections(detections))
        except Exception as exc:
            self.root.after(0, lambda: messagebox.showerror("Detection failed", str(exc)))
            self.root.after(0, lambda: self.status_var.set("Detection failed."))

    def _set_detections(self, detections: list[PlateDetection]) -> None:
        self.plates = [
            {
                "car_id": d.car_id,
                "plate": d.plate_text,
                "confidence": d.text_score,
                "frame": d.frame_number,
            }
            for d in detections
        ]
        self._refresh_table()
        self.status_var.set(f"Detection complete: {len(self.plates)} unique vehicles.")

    def _refresh_table(self) -> None:
        self.table.delete(*self.table.get_children())
        for row in self.plates:
            self.table.insert(
                "",
                "end",
                values=(row["car_id"], self._format_plate(row["plate"]), f"{row['confidence']:.2f}"),
            )

    def on_select(self, _event=None) -> None:
        sel = self.table.selection()
        if not sel:
            return
        item = self.table.item(sel[0])
        plate = item["values"][1].replace(" ", "")
        self.correct_var.set(plate)
        self.selected_plate_var.set(self._format_plate(plate))

    def apply_correction(self) -> None:
        sel = self.table.selection()
        if not sel:
            messagebox.showwarning("No selection", "Select a row to correct.")
            return

        corrected = self.correct_var.get().upper().replace(" ", "")
        if not UK_PLATE_PATTERN.match(corrected):
            messagebox.showwarning("Invalid plate", "Please enter a UK plate in format AA00AAA.")
            return

        index = self.table.index(sel[0])
        self.plates[index]["plate"] = corrected
        self._refresh_table()
        self.table.selection_set(self.table.get_children()[index])
        self.selected_plate_var.set(self._format_plate(corrected))
        self.status_var.set(f"Updated car {self.plates[index]['car_id']} plate to {corrected}.")

    def load_csv(self) -> None:
        path = filedialog.askopenfilename(title="Load detection CSV", filetypes=[("CSV", "*.csv")])
        if not path:
            return

        with open(path, newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)

        best_by_car: dict[int, dict] = {}
        for row in rows:
            try:
                car_id = int(float(row["car_id"]))
                score = float(row.get("license_number_score") or 0)
                plate = (row.get("license_number") or "").upper().replace(" ", "")
                frame = int(float(row.get("frame_nmr") or 0))
            except (TypeError, ValueError):
                continue
            if not plate or plate == "0":
                continue
            if car_id not in best_by_car or score > best_by_car[car_id]["confidence"]:
                best_by_car[car_id] = {
                    "car_id": car_id,
                    "plate": plate,
                    "confidence": score,
                    "frame": frame,
                }

        self.plates = sorted(best_by_car.values(), key=lambda x: x["car_id"])
        self._refresh_table()
        self.status_var.set(f"Loaded {len(self.plates)} vehicles from CSV.")

    def save_csv(self) -> None:
        if not self.plates:
            messagebox.showwarning("Nothing to save", "No detections to save.")
            return

        path = filedialog.asksaveasfilename(
            title="Save corrected results",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="corrected_plates.csv",
        )
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["car_id", "plate", "confidence", "frame"])
            writer.writeheader()
            for row in self.plates:
                writer.writerow(row)

        self.status_var.set(f"Saved corrections to {Path(path).name}.")

    @staticmethod
    def _format_plate(text: str) -> str:
        t = text.replace(" ", "")
        return f"{t[:4]} {t[4:]}" if len(t) >= 5 else t


def main() -> None:
    root = tk.Tk()
    PlatePatrolApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
