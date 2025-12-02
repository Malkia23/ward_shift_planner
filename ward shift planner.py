import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import csv
import json
from datetime import datetime
from typing import List, Dict, Tuple
import math
from collections import defaultdict
import random

class WardShiftPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Ward Shift Planner")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f8ff')
        
        # Initialize data
        self.nurses = []
        self.patients = []
        self.acuity_categories = ["High", "Moderate", "Low"]
        self.skill_levels = ["Senior", "Intermediate", "Junior"]
        self.tasks = ["Wound dressings", "Bed baths", "IV meds", "Post-ops", "Isolation cases"]
        
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title = tk.Label(title_frame, text="WARD SHIFT PLANNER", 
                        font=('Arial', 24, 'bold'), 
                        fg='white', bg='#2c3e50')
        title.pack(pady=20)
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg='#f0f8ff')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left panel - Inputs
        left_panel = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Right panel - Output/Preview
        right_panel = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(left_panel)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Basic Settings
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Basic Settings")
        self.create_basic_settings_tab(tab1)
        
        # Tab 2: Nurse Management
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Nurse Management")
        self.create_nurse_management_tab(tab2)
        
        # Tab 3: Patient Acuity
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="Patient Acuity")
        self.create_acuity_tab(tab3)
        
        # Tab 4: Tasks & Notes
        tab4 = ttk.Frame(notebook)
        notebook.add(tab4, text="Tasks & Notes")
        self.create_tasks_tab(tab4)
        
        # Output area
        self.create_output_panel(right_panel)
        
    def create_basic_settings_tab(self, parent):
        frame = tk.Frame(parent, bg='white')
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Total patients
        tk.Label(frame, text="Total Patients:", 
                font=('Arial', 11, 'bold'), bg='white').grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        self.patient_entry = tk.Entry(frame, font=('Arial', 11), width=10)
        self.patient_entry.grid(row=0, column=1, sticky=tk.W, pady=(0, 10))
        self.patient_entry.insert(0, "28")
        
        # Ratio settings
        tk.Label(frame, text="Nurse-to-Patient Ratio:", 
                font=('Arial', 11, 'bold'), bg='white').grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        ratio_frame = tk.Frame(frame, bg='white')
        ratio_frame.grid(row=1, column=1, sticky=tk.W, pady=(0, 10))
        
        tk.Label(ratio_frame, text="1:", bg='white').pack(side=tk.LEFT)
        self.ratio_entry = tk.Entry(ratio_frame, font=('Arial', 11), width=5)
        self.ratio_entry.pack(side=tk.LEFT)
        self.ratio_entry.insert(0, "6")
        
        # Generate button
        generate_btn = tk.Button(frame, text="🔧 Generate Allocation", 
                                font=('Arial', 11, 'bold'),
                                bg='#3498db', fg='white',
                                command=self.generate_allocation)
        generate_btn.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Validation info
        self.validation_label = tk.Label(frame, text="", 
                                        font=('Arial', 10), bg='white', fg='red')
        self.validation_label.grid(row=3, column=0, columnspan=2)
        
    def create_nurse_management_tab(self, parent):
        frame = tk.Frame(parent, bg='white')
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Nurse input fields
        input_frame = tk.Frame(frame, bg='white')
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(input_frame, text="Nurse Name:", bg='white').grid(row=0, column=0, padx=(0, 5))
        self.nurse_name_entry = tk.Entry(input_frame, width=20)
        self.nurse_name_entry.grid(row=0, column=1, padx=(0, 10))
        
        tk.Label(input_frame, text="Skill Level:", bg='white').grid(row=0, column=2, padx=(0, 5))
        self.skill_combo = ttk.Combobox(input_frame, values=self.skill_levels, width=15)
        self.skill_combo.grid(row=0, column=3)
        self.skill_combo.current(0)
        
        add_btn = tk.Button(input_frame, text="Add Nurse", 
                           command=self.add_nurse, bg='#2ecc71', fg='white')
        add_btn.grid(row=0, column=4, padx=(10, 0))
        
        # Nurse list
        list_frame = tk.Frame(frame, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(list_frame, text="Nurses on Duty:", 
                font=('Arial', 11, 'bold'), bg='white').pack(anchor=tk.W)
        
        # Treeview for nurses
        columns = ('Name', 'Skill Level')
        self.nurse_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.nurse_tree.heading(col, text=col)
            self.nurse_tree.column(col, width=150)
        
        self.nurse_tree.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # Control buttons
        btn_frame = tk.Frame(frame, bg='white')
        btn_frame.pack(fill=tk.X)
        
        tk.Button(btn_frame, text="Load from File", 
                 command=self.load_nurses_from_file).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Clear All", 
                 command=self.clear_nurses).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Save to File", 
                 command=self.save_nurses_to_file).pack(side=tk.LEFT, padx=5)
        
    def create_acuity_tab(self, parent):
        frame = tk.Frame(parent, bg='white')
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame, text="Patient Acuity Distribution", 
                font=('Arial', 11, 'bold'), bg='white').pack(anchor=tk.W)
        
        acuity_frame = tk.Frame(frame, bg='white')
        acuity_frame.pack(fill=tk.X, pady=10)
        
        self.acuity_vars = {}
        for i, acuity in enumerate(self.acuity_categories):
            tk.Label(acuity_frame, text=f"{acuity} Acuity:", bg='white').grid(row=i, column=0, sticky=tk.W, padx=(0, 10))
            var = tk.StringVar(value="0")
            self.acuity_vars[acuity] = var
            entry = tk.Entry(acuity_frame, textvariable=var, width=10)
            entry.grid(row=i, column=1, padx=(0, 20))
        
        # Auto-calculate button
        tk.Button(frame, text="Auto-calculate from Total", 
                 command=self.calculate_acuity).pack(pady=10)
        
        # Acuity explanation
        info_text = """High Acuity: Critically ill, frequent monitoring needed
Moderate Acuity: Stable but requires regular care
Low Acuity: Mostly independent, minimal intervention"""
        
        info_label = tk.Label(frame, text=info_text, 
                             justify=tk.LEFT, bg='white', fg='#555')
        info_label.pack(anchor=tk.W, pady=10)
        
    def create_tasks_tab(self, parent):
        frame = tk.Frame(parent, bg='white')
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame, text="Tasks to Distribute:", 
                font=('Arial', 11, 'bold'), bg='white').pack(anchor=tk.W)
        
        self.task_vars = {}
        for i, task in enumerate(self.tasks):
            var = tk.IntVar(value=1)
            self.task_vars[task] = var
            cb = tk.Checkbutton(frame, text=task, variable=var, 
                               bg='white', anchor=tk.W)
            cb.pack(fill=tk.X, pady=2)
        
        # Notes section
        tk.Label(frame, text="Shift Notes:", 
                font=('Arial', 11, 'bold'), bg='white').pack(anchor=tk.W, pady=(20, 5))
        
        self.notes_text = tk.Text(frame, height=6, width=40)
        self.notes_text.pack(fill=tk.BOTH, expand=True)
        
    def create_output_panel(self, parent):
        # Output header
        header_frame = tk.Frame(parent, bg='#34495e')
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame, text="Allocation Output", 
                font=('Arial', 14, 'bold'), 
                fg='white', bg='#34495e').pack(pady=10)
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(parent, 
                                                    font=('Courier', 10),
                                                    width=60, height=30)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Export buttons
        export_frame = tk.Frame(parent, bg='white')
        export_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(export_frame, text="📄 Export to TXT", 
                 command=self.export_to_txt).pack(side=tk.LEFT, padx=5)
        tk.Button(export_frame, text="📊 Export to CSV", 
                 command=self.export_to_csv).pack(side=tk.LEFT, padx=5)
        tk.Button(export_frame, text="🖨️ Print Preview", 
                 command=self.print_preview).pack(side=tk.LEFT, padx=5)
        
    def add_nurse(self):
        name = self.nurse_name_entry.get().strip()
        skill = self.skill_combo.get()
        
        if not name:
            messagebox.showwarning("Warning", "Please enter a nurse name")
            return
        
        self.nurses.append({"name": name, "skill": skill})
        self.nurse_tree.insert('', tk.END, values=(name, skill))
        self.nurse_name_entry.delete(0, tk.END)
        
    def clear_nurses(self):
        self.nurses = []
        for item in self.nurse_tree.get_children():
            self.nurse_tree.delete(item)
    
    def load_nurses_from_file(self):
        file_path = filedialog.askopenfilename(
            title="Select nurse file",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.clear_nurses()
                with open(file_path, 'r') as f:
                    for line in f:
                        if ',' in line:
                            parts = line.strip().split(',')
                            if len(parts) >= 2:
                                name, skill = parts[0], parts[1]
                                if skill not in self.skill_levels:
                                    skill = "Intermediate"
                        else:
                            name = line.strip()
                            skill = "Intermediate"
                        
                        if name:
                            self.nurses.append({"name": name, "skill": skill})
                            self.nurse_tree.insert('', tk.END, values=(name, skill))
                
                messagebox.showinfo("Success", f"Loaded {len(self.nurses)} nurses from file")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def save_nurses_to_file(self):
        if not self.nurses:
            messagebox.showwarning("Warning", "No nurses to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save nurses to file",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    for nurse in self.nurses:
                        f.write(f"{nurse['name']},{nurse['skill']}\n")
                messagebox.showinfo("Success", "Nurses saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def calculate_acuity(self):
        try:
            total = int(self.patient_entry.get())
            
            # Simple distribution: 20% high, 50% moderate, 30% low
            high = int(total * 0.2)
            moderate = int(total * 0.5)
            low = total - high - moderate
            
            self.acuity_vars["High"].set(str(high))
            self.acuity_vars["Moderate"].set(str(moderate))
            self.acuity_vars["Low"].set(str(low))
        except ValueError:
            messagebox.showwarning("Warning", "Please enter a valid total number of patients")
    
    def validate_ratio(self):
        try:
            total_patients = int(self.patient_entry.get())
            ratio = int(self.ratio_entry.get())
            required_nurses = math.ceil(total_patients / ratio)
            
            if len(self.nurses) < required_nurses:
                self.validation_label.config(
                    text=f"⚠️ Unsafe staffing: You need at least {required_nurses} nurses for a 1:{ratio} ratio."
                )
                return False
            else:
                self.validation_label.config(text="✓ Staffing ratio is safe")
                return True
        except ValueError:
            self.validation_label.config(text="Please enter valid numbers")
            return False
    
    def generate_allocation(self):
        if not self.validate_ratio():
            if not messagebox.askyesno("Warning", "Staffing ratio may be unsafe. Continue anyway?"):
                return
        
        if not self.nurses:
            messagebox.showwarning("Warning", "Please add at least one nurse")
            return
        
        try:
            total_patients = int(self.patient_entry.get())
            
            # Create patient list with acuity
            patients = []
            acuity_counts = {}
            
            for acuity in self.acuity_categories:
                count = int(self.acuity_vars[acuity].get() or 0)
                acuity_counts[acuity] = count
                patients.extend([{"id": i+1, "acuity": acuity} 
                               for i in range(len(patients), len(patients) + count)])
            
            # Adjust if total doesn't match
            if len(patients) != total_patients:
                messagebox.showwarning("Warning", 
                    f"Acuity distribution ({len(patients)}) doesn't match total patients ({total_patients}). Adjusting...")
                while len(patients) < total_patients:
                    patients.append({"id": len(patients)+1, "acuity": "Moderate"})
                patients = patients[:total_patients]
            
            # Distribute patients to nurses
            allocation = self.distribute_patients(patients, self.nurses)
            
            # Generate output
            self.display_allocation(allocation, acuity_counts)
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
    
    def distribute_patients(self, patients, nurses):
        # Sort nurses by skill (Senior first)
        sorted_nurses = sorted(nurses, 
                              key=lambda x: self.skill_levels.index(x['skill']))
        
        # Group patients by acuity
        high_acuity = [p for p in patients if p['acuity'] == 'High']
        moderate_acuity = [p for p in patients if p['acuity'] == 'Moderate']
        low_acuity = [p for p in patients if p['acuity'] == 'Low']
        
        # Initialize allocation
        allocation = {nurse['name']: {
            'nurse': nurse,
            'patients': [],
            'tasks': [],
            'justification': ''
        } for nurse in sorted_nurses}
        
        nurse_names = list(allocation.keys())
        nurse_index = 0
        
        # Distribute high acuity patients first (to senior nurses)
        for patient in high_acuity:
            # Find next available nurse (wrap around if needed)
            for _ in range(len(nurse_names)):
                current_nurse = nurse_names[nurse_index % len(nurse_names)]
                allocation[current_nurse]['patients'].append(patient)
                nurse_index += 1
                break
        
        # Distribute moderate acuity
        for patient in moderate_acuity:
            current_nurse = nurse_names[nurse_index % len(nurse_names)]
            allocation[current_nurse]['patients'].append(patient)
            nurse_index += 1
        
        # Distribute low acuity
        for patient in low_acuity:
            current_nurse = nurse_names[nurse_index % len(nurse_names)]
            allocation[current_nurse]['patients'].append(patient)
            nurse_index += 1
        
        # Add justification
        for nurse_name, data in allocation.items():
            patient_count = len(data['patients'])
            acuity_dist = {}
            for p in data['patients']:
                acuity_dist[p['acuity']] = acuity_dist.get(p['acuity'], 0) + 1
            
            justification = f"Assigned {patient_count} patients"
            if acuity_dist:
                acuity_desc = ', '.join([f"{v} {k.lower()}" for k, v in acuity_dist.items()])
                justification += f" ({acuity_desc})"
            
            skill = data['nurse']['skill']
            if skill == 'Senior' and acuity_dist.get('High', 0) > 0:
                justification += f". Senior nurse assigned high-acuity patients."
            elif skill == 'Junior' and acuity_dist.get('High', 0) == 0:
                justification += f". Junior nurse assigned appropriate lower-acuity patients."
            
            data['justification'] = justification
        
        return allocation
    
    def display_allocation(self, allocation, acuity_counts):
        output = "=" * 60 + "\n"
        output += "WARD SHIFT ALLOCATION REPORT\n"
        output += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        output += "=" * 60 + "\n\n"
        
        # Summary
        output += "📊 SUMMARY\n"
        output += f"Total Patients: {sum(acuity_counts.values())}\n"
        output += f"Nurses on Duty: {len(allocation)}\n"
        output += f"Patient Acuity: {acuity_counts}\n\n"
        
        # Individual allocations
        for nurse_name, data in allocation.items():
            output += f"\n{'='*40}\n"
            output += f"👩⚕️ NURSE: {nurse_name}\n"
            output += f"📋 Skill Level: {data['nurse']['skill']}\n"
            output += f"🛌 Patients Assigned: {len(data['patients'])}\n"
            
            # Group patients by bed ranges
            if data['patients']:
                patient_ids = sorted([p['id'] for p in data['patients']])
                # Create bed ranges
                ranges = []
                start = end = patient_ids[0]
                
                for pid in patient_ids[1:]:
                    if pid == end + 1:
                        end = pid
                    else:
                        ranges.append((start, end))
                        start = end = pid
                ranges.append((start, end))
                
                bed_ranges = ', '.join([f"{s}-{e}" if s != e else str(s) for s, e in ranges])
                output += f"📍 Bed Assignment: {bed_ranges}\n"
            
            # Acuity breakdown
            acuity_summary = {}
            for p in data['patients']:
                acuity_summary[p['acuity']] = acuity_summary.get(p['acuity'], 0) + 1
            
            if acuity_summary:
                output += f"📈 Acuity Breakdown: {acuity_summary}\n"
            
            # Justification
            output += f"💡 {data['justification']}\n"
        
        # Tasks distribution (simplified)
        output += "\n\n📝 TASKS DISTRIBUTION\n"
        output += "-" * 40 + "\n"
        
        # Distribute selected tasks
        selected_tasks = [task for task, var in self.task_vars.items() if var.get() == 1]
        if selected_tasks:
            for i, task in enumerate(selected_tasks):
                nurse_idx = i % len(allocation)
                nurse_name = list(allocation.keys())[nurse_idx]
                allocation[nurse_name]['tasks'].append(task)
        
        for nurse_name, data in allocation.items():
            if data['tasks']:
                output += f"\n{nurse_name}: {', '.join(data['tasks'])}"
        
        # Shift notes
        notes = self.notes_text.get("1.0", tk.END).strip()
        if notes:
            output += "\n\n📋 SHIFT NOTES\n"
            output += "-" * 40 + "\n"
            output += notes
        
        output += "\n\n" + "=" * 60
        output += "\n⚠️ REMINDER: This is a planning tool. Always use clinical judgment."
        
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(1.0, output)
    
    def export_to_txt(self):
        content = self.output_text.get(1.0, tk.END)
        if not content.strip():
            messagebox.showwarning("Warning", "No allocation to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export allocation",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(content)
                messagebox.showinfo("Success", f"Allocation exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def export_to_csv(self):
        # This would export structured data for analysis
        file_path = filedialog.asksaveasfilename(
            title="Export to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # In a real implementation, you would export the structured data
                messagebox.showinfo("Info", "CSV export would be implemented with structured data")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def print_preview(self):
        # Simple print preview
        content = self.output_text.get(1.0, tk.END)
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Print Preview")
        preview_window.geometry("800x600")
        
        text_widget = scrolledtext.ScrolledText(preview_window, font=('Courier', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(1.0, content)
        text_widget.config(state=tk.DISABLED)
        
        tk.Button(preview_window, text="Close", 
                 command=preview_window.destroy).pack(pady=10)

def main():
    root = tk.Tk()
    app = WardShiftPlanner(root)
    root.mainloop()

if __name__ == "__main__":
    main()
