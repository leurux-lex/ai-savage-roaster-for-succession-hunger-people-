import tkinter as tk
from tkinter import ttk, messagebox
import random
import numpy as np
from sklearn.linear_model import LinearRegression  # ML for predictions
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Task:
    def __init__(self, name, est_time, priority):
        self.name = name
        self.est_time = est_time
        self.priority = priority

class leurux_ai:
    def __init__(self):
        self.tasks = []
        self.roast_templates = [
            "You're slower than a {} in {} – hustle up!",
            "If {} was a sport, you'd be MVP. Now snap out of it!",
            "Your task list is mocking you like a {}. Prove it wrong.",
            "Even a {} finishes faster. Embarrassing.",
            "Procrastination alert: You're one {} away from failure."
        ]
        self.fillers = ['snail', 'dial-up modem', 'lazy sloth', 'broken robot', 'turtle race', 'Windows update']

        self.est_times = np.array([1, 2, 3, 4, 5, 6, 7, 8]).reshape(-1, 1)
        self.actual_times = np.array([1.4, 2.6, 3.2, 4.8, 5.5, 7.1, 8.3, 9.2])  
        self.model = LinearRegression()
        self.model.fit(self.est_times, self.actual_times)

    def add_task(self, task):
        self.tasks.append(task)

    def get_roast(self):

        template = random.choice(self.roast_templates)
        fillers = [random.choice(self.fillers) for _ in range(template.count('{}'))]
        return template.format(*fillers)

    def predict_with_margins(self, est):
        predicted = self.model.predict(np.array([[est]]))[0]
        margin = predicted * 0.25 
        return predicted, predicted - margin, predicted + margin

    def generate_plan(self):
        if not self.tasks:
            return "No tasks yet. Add some to get roasted!"

        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        sorted_tasks = sorted(self.tasks, key=lambda t: priority_order[t.priority])

        plan = "AI Powered Roast Plan:\n\n"
        total_est = 0
        total_pred = 0

        for i, t in enumerate(sorted_tasks, 1):
            pred, lower, upper = self.predict_with_margins(t.est_time)
            total_est += t.est_time
            total_pred += pred

            plan += f"{i}. {t.name} ({t.priority.upper()})\n"
            plan += f"   Est: {t.est_time}h → Predicted: {pred:.1f}h (Margins: {lower:.1f}-{upper:.1f}h)\n"
            if pred > t.est_time * 1.15:
                plan += f"   🔥 {self.get_roast()}\n"
            plan += "\n"

        plan += f"Total Est: {total_est:.1f}h | Realistic (ML): {total_pred:.1f}h\n"
        if total_pred > total_est * 1.2:
            plan += "\nYou're underestimating big time. AI says: Adjust or fail spectacularly."

        return plan

    def plot_chart(self, fig):
        if not self.tasks:
            return

        names = [t.name[:15] + '...' if len(t.name) > 15 else t.name for t in self.tasks]
        ests = [t.est_time for t in self.tasks]
        preds = [self.predict_with_margins(e)[0] for e in ests]
        lowers = [self.predict_with_margins(e)[1] for e in ests]
        uppers = [self.predict_with_margins(e)[2] for e in ests]

        x = np.arange(len(names))
        fig.clear()
        ax = fig.add_subplot(111)
        ax.plot(x, preds, label='Predicted', color='red', marker='o')
        ax.fill_between(x, lowers, uppers, color='red', alpha=0.2, label='Margins')
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha='right')
        ax.set_ylabel('Hours')
        ax.set_title('Predictive Margins')
        ax.legend()

class App:
    def __init__(self, root):
        self.planner = leurux_ai()
        self.root = root
        self.root.title("savage roast success failure with AI Edition")
        self.root.geometry("800x600")
        self.root.configure(bg='#0a0a0a')

        input_frame = ttk.Frame(root, padding=10)
        input_frame.pack(fill='x')

        ttk.Label(input_frame, text="Task:").grid(row=0, column=0, padx=5)
        self.name_entry = ttk.Entry(input_frame, width=40)
        self.name_entry.grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, text="Est Hours:").grid(row=0, column=2, padx=5)
        self.time_entry = ttk.Entry(input_frame, width=10)
        self.time_entry.grid(row=0, column=3, padx=5)

        ttk.Label(input_frame, text="Priority:").grid(row=0, column=4, padx=5)
        self.prio_var = tk.StringVar(value="medium")
        prio_menu = ttk.OptionMenu(input_frame, self.prio_var, "medium", "high", "medium", "low")
        prio_menu.grid(row=0, column=5, padx=5)

        add_btn = ttk.Button(input_frame, text="Add & Roast", command=self.add_task)
        add_btn.grid(row=0, column=6, padx=10)

        self.plan_text = tk.Text(root, height=15, bg='#111', fg='#ddd', font=('Consolas', 10))
        self.plan_text.pack(pady=10, padx=10, fill='both', expand=True)

        self.fig = plt.Figure(figsize=(7, 3), dpi=100, facecolor='#0a0a0a')
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(pady=10, padx=10, fill='both')

    def add_task(self):
        name = self.name_entry.get().strip()
        try:
            est = float(self.time_entry.get())
            if est <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Enter a valid positive number for hours.")
            return

        prio = self.prio_var.get()
        task = Task(name, est, prio)
        self.planner.add_task(task)

        self.update_ui()
        self.name_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)

    def update_ui(self):
        plan = self.planner.generate_plan()
        self.plan_text.delete(1.0, tk.END)
        self.plan_text.insert(tk.END, plan)
        self.planner.plot_chart(self.fig)
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()