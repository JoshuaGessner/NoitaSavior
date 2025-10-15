# nsav.py
# Noita Savior
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import shutil
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog, PhotoImage
import os
from datetime import datetime
import json

# Try to import psutil, with fallback if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available. Game protection will be disabled.")

# Constants
NOITA_SAVE_PATH = os.path.expandvars(r"%AppData%\LocalLow\Nolla_Games_Noita\save00")

# Use proper paths that work both in development and as executable
if getattr(sys, 'frozen', False):
    # Running as executable
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running as script
    BASE_DIR = os.path.dirname(__file__)

BACKUP_DIR = os.path.join(BASE_DIR, "backups")
SLOTS_FILE = os.path.join(BASE_DIR, "slots.json")

# Alternative save paths to check
ALTERNATIVE_PATHS = [
    os.path.expandvars(r"%AppData%\LocalLow\Nolla_Games_Noita\save00"),
    os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Nolla_Games_Noita\save00"),
    os.path.expandvars(r"%LOCALAPPDATA%\..\LocalLow\Nolla_Games_Noita\save00"),
    os.path.join(os.path.expanduser("~"), "AppData", "LocalLow", "Nolla_Games_Noita", "save00")
]

# Simple tooltip helper
class ToolTip:
    """Display a tooltip with the full slot name when hovering over a widget."""
    def __init__(self, widget, text=""):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.enter)
        widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        if self.tipwindow or not self.text:
            return
        # Position the tooltip just below the widget
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(tw, text=self.text, background="#ffffe0",
                          relief='solid', borderwidth=1, padding=2)
        label.pack()

    def leave(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

class NoitaSaveManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.iconbitmap("icon.ico")
        self.root.title("Noita Savior")
        self.root.geometry("600x450")
        self.root.resizable(True, True)
        self.root.minsize(500, 400)
        
        # Create backup directory if it doesn't exist
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        # Find the correct Noita save folder
        self.noita_save_path = self.find_noita_save_folder()
        self.noita_folder_exists = self.noita_save_path is not None
        
        # Load slot data
        self.slots_data = self.load_slots_data()
        self.slot_tooltips = []          # <-- new list to hold tooltip objects

        # Store references to rename buttons
        self.rename_buttons = []
        
        # Debug: Print file paths
        print(f"Base directory: {BASE_DIR}")
        print(f"Backup directory: {BACKUP_DIR}")
        print(f"Slots file: {SLOTS_FILE}")
        
        self.setup_ui()

        # After UI is laid out, let Tk compute the needed size
        self.root.update_idletasks()
        req_w = self.root.winfo_reqwidth()
        req_h = self.root.winfo_reqheight()
        self.root.geometry(f"{req_w}x{req_h}")
        
        # Update initial status
        self.update_initial_status()
        
        # Set up cleanup on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def find_noita_save_folder(self):
        """Find the correct Noita save folder by checking multiple possible paths"""
        for path in ALTERNATIVE_PATHS:
            if os.path.exists(path):
                print(f"Found Noita save folder at: {path}")
                return path
        
        # If not found, print debug information
        print("Noita save folder not found. Checked paths:")
        for i, path in enumerate(ALTERNATIVE_PATHS, 1):
            print(f"  {i}. {path} - {'EXISTS' if os.path.exists(path) else 'NOT FOUND'}")
        
        # Check if the parent directory exists
        parent_dir = os.path.dirname(ALTERNATIVE_PATHS[0])
        if os.path.exists(parent_dir):
            print(f"Parent directory exists: {parent_dir}")
            print("Contents:")
            try:
                for item in os.listdir(parent_dir):
                    print(f"  - {item}")
            except Exception as e:
                print(f"  Error listing contents: {e}")
        else:
            print(f"Parent directory does not exist: {parent_dir}")
        
        return None
    
    def is_noita_running(self):
        """Check if Noita game process is currently running"""
        if not PSUTIL_AVAILABLE:
            # Fallback: try using tasklist command on Windows
            try:
                import subprocess
                result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq noita.exe'], 
                                      capture_output=True, text=True, timeout=5)
                return 'noita.exe' in result.stdout
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                # If tasklist fails, assume game is not running to be safe
                return False
        
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and proc.info['name'].lower() == 'noita.exe':
                    return True
            return False
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return False
        
    def load_slots_data(self):
        """Load slot metadata from JSON file"""
        if os.path.exists(SLOTS_FILE):
            try:
                with open(SLOTS_FILE, 'r') as f:
                    data = json.load(f)
                    # Update exists status based on actual backup folders
                    for i in range(8):
                        slot_dir = os.path.join(BACKUP_DIR, f"slot_{i}")
                        if str(i) in data:
                            data[str(i)]["exists"] = os.path.exists(slot_dir)
                        else:
                            data[str(i)] = {"name": f"Slot {i+1}", "date": "", "exists": os.path.exists(slot_dir)}
                    return data
            except:
                pass
        
        # Initialize with actual folder status
        data = {}
        for i in range(8):
            slot_dir = os.path.join(BACKUP_DIR, f"slot_{i}")
            exists = os.path.exists(slot_dir)
            data[str(i)] = {
                "name": f"Slot {i+1}", 
                "date": "", 
                "exists": exists
            }
            # If folder exists but no metadata, try to get creation date
            if exists and not data[str(i)]["date"]:
                try:
                    timestamp = os.path.getctime(slot_dir)
                    data[str(i)]["date"] = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
                except:
                    data[str(i)]["date"] = "Unknown date"
        return data
    
    def save_slots_data(self):
        """Save slot metadata to JSON file"""
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(SLOTS_FILE), exist_ok=True)
            
            with open(SLOTS_FILE, 'w') as f:
                json.dump(self.slots_data, f, indent=2)
            
            print(f"Slot data saved to: {SLOTS_FILE}")
            return True
        except Exception as e:
            print(f"Error saving slot data: {e}")
            self.update_status(f"Error saving slot data: {e}")
            return False
    
    def backup_current_save(self):
        """Backup the current save folder"""
        if not self.noita_folder_exists or not self.noita_save_path:
            return False, "Noita save folder not found"
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(BACKUP_DIR, f"auto_backup_{timestamp}")
            shutil.copytree(self.noita_save_path, backup_path)
            return True, f"Auto-backup created: {timestamp}"
        except Exception as e:
            return False, f"Backup failed: {e}"
    
    def save_to_slot(self, slot_num):
        """Save current game state to specified slot"""
        if not self.noita_folder_exists or not self.noita_save_path:
            self.set_temporary_status("Noita save folder not found!")
            return
        
        # Check if Noita is running
        if self.is_noita_running():
            messagebox.showwarning(
                "Noita is Running", 
                "Cannot save while Noita is running!\n\nPlease close Noita first, then try again."
            )
            self.set_temporary_status("Save blocked - Noita is running")
            return
        
        slot_dir = os.path.join(BACKUP_DIR, f"slot_{slot_num}")
        
        try:
            # Remove existing slot if it exists
            if os.path.exists(slot_dir):
                shutil.rmtree(slot_dir)
            
            # Copy current save to slot
            shutil.copytree(self.noita_save_path, slot_dir)
            
            # Update slot metadata (keep user‑defined name if present)
            slot_data = self.slots_data.get(str(slot_num), {})
            slot_data["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            slot_data["exists"] = True
            # Ensure a default name if none was set
            if "name" not in slot_data:
                slot_data["name"] = f"Slot {slot_num + 1}"
            self.slots_data[str(slot_num)] = slot_data
            
            self.save_slots_data()
            self.update_slot_display(slot_num)
            self.set_temporary_status(f"Saved to Slot {slot_num + 1}")
            
        except Exception as e:
            self.set_temporary_status(f"Save failed: {e}")

    def rename_slot(self, slot_num):
        """Prompt user to rename a slot"""
        current_name = self.slots_data[str(slot_num)].get("name", f"Slot {slot_num + 1}")
        new_name = simpledialog.askstring(
            "Rename Slot",
            f"Enter new name for Slot {slot_num + 1}:",
            initialvalue=current_name
        )
        if new_name:
            self.slots_data[str(slot_num)]["name"] = new_name
            self.save_slots_data()
            self.update_slot_display(slot_num)
            self.set_temporary_status(f"Slot {slot_num + 1} renamed to \"{new_name}\"")

    def load_from_slot(self, slot_num):
        """Load game state from specified slot"""
        slot_dir = os.path.join(BACKUP_DIR, f"slot_{slot_num}")
        
        if not os.path.exists(slot_dir):
            self.set_temporary_status(f"Slot {slot_num + 1} is empty!")
            return
        
        # Check if Noita is running
        if self.is_noita_running():
            messagebox.showwarning(
                "Noita is Running", 
                "Cannot load while Noita is running!\n\nPlease close Noita first, then try again."
            )
            self.set_temporary_status("Load blocked - Noita is running")
            return
        
        try:
            # Backup current save first
            success, message = self.backup_current_save()
            if not success:
                self.set_temporary_status(f"Auto-backup failed: {message}")
                return
            
            # Remove current save
            if self.noita_save_path and os.path.exists(self.noita_save_path):
                shutil.rmtree(self.noita_save_path)
            
            # Restore from slot
            shutil.copytree(slot_dir, self.noita_save_path)
            self.set_temporary_status(f"Loaded Slot {slot_num + 1} (auto-backup created)")
            
        except Exception as e:
            self.set_temporary_status(f"Load failed: {e}")

    def delete_slot(self, slot_num):
        """Delete specified slot"""
        slot_dir = os.path.join(BACKUP_DIR, f"slot_{slot_num}")
        
        if not os.path.exists(slot_dir):
            self.set_temporary_status(f"Slot {slot_num + 1} is already empty!")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Slot {slot_num + 1}?"):
            try:
                shutil.rmtree(slot_dir)
                self.slots_data[str(slot_num)] = {
                    "name": f"Slot {slot_num + 1}",
                    "date": "",
                    "exists": False
                }
                self.save_slots_data()
                self.update_slot_display(slot_num)
                self.set_temporary_status(f"Deleted Slot {slot_num + 1}")
            except Exception as e:
                self.set_temporary_status(f"Delete failed: {e}")
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create slots (2 rows of 4)
        self.slot_frames = []
        self.slot_labels = []
        self.slot_buttons = []
        
        for i in range(8):
            row = 2 + (i // 4)
            col = i % 4
            
            # Slot frame
            slot_frame = ttk.LabelFrame(main_frame, text=f"Slot {i+1}", padding="8")
            slot_frame.grid(row=row, column=col, padx=3, pady=3, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Configure slot frame to expand
            slot_frame.columnconfigure(0, weight=1)
            slot_frame.rowconfigure(0, weight=1)
            slot_frame.rowconfigure(1, weight=1)
            
            self.slot_frames.append(slot_frame)
            
            # Slot info label
            slot_label = ttk.Label(slot_frame, text="Empty", font=("Arial", 9), justify="center")
            slot_label.grid(row=0, column=0, columnspan=3, pady=(0, 8))
            self.slot_labels.append(slot_label)
            
            # Create tooltip for this label
            tooltip = ToolTip(slot_label, "")
            self.slot_tooltips.append(tooltip)

            # Buttons frame
            btn_frame = ttk.Frame(slot_frame)
            btn_frame.grid(row=1, column=0, columnspan=3, pady=(5, 0), sticky=(tk.W, tk.E))
            
            # Configure button frame
            btn_frame.columnconfigure(0, weight=1)
            
            # Save button
            save_btn = ttk.Button(btn_frame, text="Save",
                                command=lambda i=i: self.save_to_slot(i))
            save_btn.grid(row=0, column=0, pady=2, sticky=(tk.W, tk.E))
            
            # Load button
            load_btn = ttk.Button(btn_frame, text="Load",
                                command=lambda i=i: self.load_from_slot(i))
            load_btn.grid(row=1, column=0, pady=2, sticky=(tk.W, tk.E))
            
            # Delete button
            delete_btn = ttk.Button(btn_frame, text="Delete",
                                  command=lambda i=i: self.delete_slot(i))
            delete_btn.grid(row=2, column=0, pady=2, sticky=(tk.W, tk.E))
            
            self.slot_buttons.append([save_btn, load_btn, delete_btn])

            # Rename button
            rename_btn = ttk.Button(btn_frame, text="Rename",
                                   command=lambda i=i: self.rename_slot(i))
            rename_btn.grid(row=3, column=0, pady=2, sticky=(tk.W, tk.E))
            # Keep a reference to this button
            self.rename_buttons.append(rename_btn)
            
            # Update slot display
            self.update_slot_display(i)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(20, 0))
        
        # Configure grid weights for proper autoscaling
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Configure main frame grid weights
        main_frame.columnconfigure((0, 1, 2, 3), weight=1)
        main_frame.rowconfigure(2, weight=1)  # First row of slots
        main_frame.rowconfigure(3, weight=1)  # Second row of slots
        
        # Configure slot frames to expand
        for i in range(8):
            row = 2 + (i // 4)
            col = i % 4
            main_frame.rowconfigure(row, weight=1)
            main_frame.columnconfigure(col, weight=1)
    
    def update_slot_display(self, slot_num):
        """Update the display for a specific slot"""
        slot_data = self.slots_data[str(slot_num)]
        if slot_data["exists"]:
            name = slot_data.get("name", f"Slot {slot_num + 1}")
            date = slot_data.get("date", "")

            # Truncate long names to keep the slot size unchanged
            display_name = name
            if len(name) > 15:                     # 15‑char limit (adjust if needed)
                display_name = name[:12] + "..."

            self.slot_labels[slot_num].config(text=display_name)

            # Update tooltip with the full name (and date if present)
            tooltip_text = name
            if date:
                tooltip_text += f"\n{date}"
            self.slot_tooltips[slot_num].text = tooltip_text
            # Enable rename button when slot has data
            self.rename_buttons[slot_num].config(state='normal')
        else:
            self.slot_labels[slot_num].config(text="Empty")
            self.slot_tooltips[slot_num].text = ""
            # Disable rename button when slot is empty
            self.rename_buttons[slot_num].config(state='disabled')
    
    def update_initial_status(self):
        """Update initial status on startup"""
        if self.noita_folder_exists and self.noita_save_path:
            self.status_var.set("Ready - Noita save folder detected")
        else:
            self.status_var.set("Warning - Noita save folder not found")
    
    def update_status(self, message):
        """Update the status bar"""
        self.status_var.set(message)
        self.root.update_idletasks()

    # Set a temporary status that reverts after a delay
    def set_temporary_status(self, message, delay=3000):
        """Display a temporary status message for `delay` ms before restoring the default."""
        self.update_status(message)
        self.root.after(delay, self.update_initial_status)
    
    def on_closing(self):
        """Handle application closing - save data before exit"""
        try:
            # Save slot data before closing
            self.save_slots_data()
            print("Slot data saved successfully")
        except Exception as e:
            print(f"Error saving slot data on exit: {e}")
        
        # Destroy the window
        self.root.destroy()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

# Create and run the application
if __name__ == "__main__":
    app = NoitaSaveManager()
    app.run()

