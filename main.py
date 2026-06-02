import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import sweetviz as sv
import os
import tkinter as tk
import webbrowser

df_fifa = pd.read_csv(os.path.join("data", "FIFA", "elo_ratings_wc2026.csv"))
df_movies = pd.read_csv(os.path.join("data", "Movie", "mymoviedb.csv"), engine="python", on_bad_lines="skip")
df_country_wise_social = pd.read_csv(os.path.join("data", "Social_Media_Addiction", "country_wise_analysis_addiction.csv"))

#Main Window
root = tk.Tk() 
root.title("Data Analysis Dashboard")
root.geometry("1000x600")

#Top area for dashboard buttons
top_bar = tk.Frame(root)
top_bar.pack(side='top',fill='x',pady=10)

#Label and Button for FIFA Dashboard
label = tk.Label(root, text="Welcome to the Data Analysis Dashboard!")
label.pack(pady=10)

#Create buttons for 3 datasets
button = tk.Button(
    top_bar,
    text="Fifa Dashboard", 
    command=lambda: webbrowser.open(os.path.join("html_reports", "fifa_dashboard.html")))
button.pack(side='left', padx=1)

button2 = tk.Button(
    top_bar,
    text="Movie Dashboard",
    command=lambda: webbrowser.open(os.path.join("html_reports", "movie_dashboard.html")))
button2.pack(side='left', padx=1)

button3 = tk.Button(
    top_bar,
    text="Social Media Addiction Dashboard",
    command=lambda: webbrowser.open(os.path.join("html_reports", "social_media_addiction_dashboard.html")))
button3.pack(side='left', padx=1)
root.mainloop()