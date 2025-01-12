"""
Module for handling running multiple portfolio combinations.
"""

import tkinter as tk
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class InteractivePieChartApp(ctk.CTk):
    """
    Class for creating the interactive portfolio backtesting.
    """
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.root.title("Interactive Pie Chart")
        self.root.geometry("1200x600")

        self.data = {"Category A": 40, "Category B": 30, "Category C": 20, "Category D": 10}

        self.create_layout()

        self.update_pie_chart()

    def create_layout(self):
        """
        Method to create the layout of the portfolio window.
        """
        # Frame for inputs
        self.input_frame = ctk.CTkFrame(self.root)
        self.input_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)

        self.name_entries = []
        self.value_entries = []
        self.remove_buttons = []

        self.row_count = 0  # Track the current row for dynamic layout
        for category, value in self.data.items():
            self.add_category_input(category, value)

        # Add button to add a new category
        self.add_button = ctk.CTkButton(self.input_frame, text="Add Category", command=self.add_category)
        self.add_button.grid(row=self.row_count, column=0, columnspan=3, pady=10)

        # Update button
        self.update_button = ctk.CTkButton(self.input_frame, text="Update Chart", command=self.update_pie_chart)
        self.update_button.grid(row=self.row_count + 1, column=0, columnspan=3, pady=10)

        # Frame for the pie chart
        self.chart_frame = ctk.CTkFrame(self.root)
        self.chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    def add_category_input(self, category, value):
        """
        Add input fields for a category.

        Parameters
        ----------
        category : str
            String representing the name of the category for the chart.
        value : int
            Integer representing the value for the pie chart.
        """
        current_index = self.row_count

        name_label = ctk.CTkLabel(self.input_frame, text=f"Category {current_index + 1}")
        name_label.grid(row=current_index, column=0, pady=5, padx=5, sticky="w")

        name_entry = ctk.CTkEntry(self.input_frame)
        name_entry.insert(0, category)
        name_entry.grid(row=current_index, column=1, pady=5, padx=5)

        value_entry = ctk.CTkEntry(self.input_frame)
        value_entry.insert(0, str(value))
        value_entry.grid(row=current_index, column=2, pady=5, padx=5)

        # Remove button for the category
        remove_button = ctk.CTkButton(
            self.input_frame,
            text="Remove",
            command=lambda idx=current_index: self.remove_category(idx)
        )
        remove_button.grid(row=current_index, column=3, pady=5, padx=5)

        self.name_entries.append(name_entry)
        self.value_entries.append(value_entry)
        self.remove_buttons.append(remove_button)

        self.row_count += 1  # Increment the row counter

    def add_category(self):
        """
        Add a new category input row and shift buttons down.
        """
        self.add_category_input(f"Category {self.row_count + 1}", 0)
        # Move the buttons down
        self.add_button.grid(row=self.row_count, column=0, columnspan=3, pady=10)
        self.update_button.grid(row=self.row_count + 1, column=0, columnspan=3, pady=10)

    def remove_category(self, index):
        """
        Remove a category input row.

        Parameters
        ----------
        index :
        """
        # Remove the widgets for the specified index
        self.name_entries[index].destroy()
        self.value_entries[index].destroy()
        self.remove_buttons[index].destroy()

        # Remove the items from the lists
        del self.name_entries[index]
        del self.value_entries[index]
        del self.remove_buttons[index]

        # Update row positions of all remaining categories
        for i in range(index, len(self.name_entries)):
            self.name_entries[i].grid(row=i, column=1, pady=5, padx=5)
            self.value_entries[i].grid(row=i, column=2, pady=5, padx=5)
            self.remove_buttons[i].grid(row=i, column=3, pady=5, padx=5)

        # Adjust Add and Update buttons
        self.row_count -= 1
        self.add_button.grid(row=self.row_count, column=0, columnspan=3, pady=10)
        self.update_button.grid(row=self.row_count + 1, column=0, columnspan=3, pady=10)

    def update_pie_chart(self):
        """
        Method to update the pie chart based on user adjustments.
        """
        # Get updated data
        new_data = {}
        for name_entry, value_entry in zip(self.name_entries, self.value_entries):
            try:
                category = name_entry.get()
                value = float(value_entry.get())
                new_data[category] = value
            except ValueError:
                error_label = tk.Label(self.input_frame, text="Invalid input. Enter valid numbers.", fg="red")
                error_label.grid(row=self.row_count + 2, column=0, columnspan=3, pady=5)
                return

        self.data = new_data

        # Clear the chart frame
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Create the pie chart
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(
            self.data.values(),
            labels=self.data.keys(),
            autopct='%1.1f%%',
            startangle=90,
            wedgeprops={"edgecolor": "black"}
        )
        ax.axis("equal")  # Equal aspect ratio ensures the pie chart is circular

        # Embed the chart in the Tkinter GUI
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    app = InteractivePieChartApp(root)
    root.mainloop()
