import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import json
import os

# Define functions for 4PL model and fitting
def four_param_logistic(x, A, B, C, D):
    return D + (A - D) / (1 + (x / C)**B)

def inverse_four_param_logistic(OD, A, B, C, D):
    result = C * np.abs((A - OD) / (OD - D))**(1 / B)
    return result

def fit_and_plot(concentration, OD):
    params, _ = opt.curve_fit(four_param_logistic, concentration, OD)
    A, B, C, D = params
    return A, B, C, D

def plot_graph(A, B, C, D, OD, concentration, OD_sample=None, concentration_sample=None):
    fig, ax = plt.subplots(figsize=(10, 6))
    x_values = np.linspace(np.min(concentration), np.max(concentration), 500)
    y_values = four_param_logistic(x_values, A, B, C, D)
    
    ax.scatter(OD, concentration, color='red', label='Data Points')
    ax.plot(four_param_logistic(x_values, A, B, C, D), x_values, color='blue', label='Fitted 4PL Curve')

    if OD_sample is not None and concentration_sample is not None:
        ax.scatter(OD_sample, concentration_sample, color='green', label='Calculated Point', zorder=5)

    ax.set_yticks(np.arange(np.min(concentration), np.max(concentration) + 20, 20))
    ax.grid(True, which='major', linestyle='-', linewidth=0.7, color='black')
    ax.grid(True, which='minor', linestyle=':', linewidth=0.5, color='gray')
    ax.minorticks_on()
    ax.set_xlabel('OD')
    ax.set_ylabel('Concentration')
    ax.set_title('4PL Model Fitting (OD vs Concentration)' + (' with Calculated Point' if OD_sample else ''))
    ax.legend(loc='best')

    return fig

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("4PL Model Fitting")

        self.concentration = None
        self.OD = None
        self.A = self.B = self.C = self.D = None
        self.data_file = "data.json"

        # Load existing data if available
        self.load_data()

        tk.Label(root, text="Enter corresponding concentration values separated by commas:").pack()
        self.concentration_entry = tk.Entry(root)
        self.concentration_entry.pack()

        tk.Label(root, text="Enter OD values separated by commas:").pack()
        self.OD_entry = tk.Entry(root)
        self.OD_entry.pack()

        tk.Button(root, text="Fit Model", command=self.fit_model).pack()
        tk.Button(root, text="Calculate Concentration", command=self.calculate_concentration).pack()
        tk.Button(root, text="View Main Graph", command=self.view_main_graph).pack()

        self.table = ttk.Treeview(root, columns=("OD", "Concentration"), show='headings')
        self.table.heading("OD", text="OD")
        self.table.heading("Concentration", text="Concentration")
        self.table.pack()

        self.figure = plt.Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def fit_model(self):
        try:
            concentration_input = self.concentration_entry.get()
            OD_input = self.OD_entry.get()

            self.concentration = np.array([float(value) for value in concentration_input.split(',')])
            self.OD = np.array([float(value) for value in OD_input.split(',')])

            self.A, self.B, self.C, self.D = fit_and_plot(self.concentration, self.OD)
            self.plot_graph()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def calculate_concentration(self):
        try:
            OD_sample_input = simpledialog.askfloat("Input", "Enter the OD value for which you want to find the concentration:")
            if OD_sample_input is None:
                return

            concentration_sample = inverse_four_param_logistic(OD_sample_input, self.A, self.B, self.C, self.D)
            self.plot_graph(OD_sample=OD_sample_input, concentration_sample=concentration_sample)
            self.table.insert("", tk.END, values=(OD_sample_input, concentration_sample))

            # Save the new data
            self.save_data()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def view_main_graph(self):
        fig = plot_graph(self.A, self.B, self.C, self.D, self.OD, self.concentration)
        fig.canvas.draw()
        plt.show()

    def plot_graph(self, OD_sample=None, concentration_sample=None):
        self.figure.clear()
        fig = plot_graph(self.A, self.B, self.C, self.D, self.OD, self.concentration, OD_sample, concentration_sample)
        self.canvas.figure = fig
        self.canvas.draw()

    def save_data(self):
        data = []
        for row in self.table.get_children():
            data.append(self.table.item(row)["values"])

        with open(self.data_file, "w") as file:
            json.dump(data, file)

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as file:
                data = json.load(file)
                for row in data:
                    self.table.insert("", tk.END, values=row)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
