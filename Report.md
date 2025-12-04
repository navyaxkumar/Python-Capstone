Campus Energy Consumption Analysis – Capstone Project Report

Course: Programming for Problem Solving using Python
Student: Navya Kumar
Roll No.: 2501410054

1. Introduction

This capstone project focuses on analyzing electricity usage across various campus buildings using Python.
The goal was to design a complete workflow that reads multiple energy meter files, processes the data, performs time-based aggregation, organizes the logic using object-oriented programming, and generates useful visual summaries for campus administration.

The project demonstrates practical skills in Python programming, including data handling with Pandas, aggregation techniques, file management, and visualization using Matplotlib.

2. Objectives

The major objectives of this capstone project were:

Automatically read energy-use CSV files from multiple buildings

Clean and standardize meter data

Compute daily and weekly aggregates

Build a small object-oriented model representing buildings and their electricity consumption

Create a visualization dashboard combining multiple plots

Export cleaned data, building summaries, and a written summary report

These requirements align with the specifications provided in the assignment document.

3. Dataset Description

The dataset consists of hourly electricity consumption readings for three campus buildings:

Library

Admin

Hostel

Each file included the following fields:

timestamp – the date and hour of the reading

kwh – electricity consumption for that hour

building – the building’s name

These files were stored in the /data directory and processed automatically when the program was executed.

4. Data Ingestion and Cleaning
4.1 Ingestion Process

The system scans the /data folder for CSV files and attempts to read each one.
The ingestion logic includes:

Skipping unreadable rows

Handling inconsistent column names

Adding building metadata when missing

Merging all files into a single DataFrame

This ensures that even imperfect or inconsistent CSV files can still be processed.

4.2 Data Cleaning

The cleaning stage included:

Converting timestamps to proper datetime objects

Ensuring kWh values are numeric

Removing rows with missing essential values

Sorting the data chronologically

The resulting cleaned dataset was saved as cleaned_energy_data.csv.

5. Aggregation and Analysis
5.1 Daily Aggregation

Daily totals were calculated for each building.
This helps observe day-to-day fluctuations and highlights buildings with consistently high usage.

5.2 Weekly Aggregation

Weekly totals were computed using Pandas’ resampling functions.
This provides a broader view of overall building consumption trends.

5.3 Building Summary

A summary table was created that includes:

Total electricity consumed

Average hourly consumption

Minimum and maximum recorded values

Peak consumption hour

This summary was exported as building_summary.csv.

6. Object-Oriented Implementation

The OOP section consists of three classes:

Reading

Represents a single electricity reading (timestamp + kWh).

Block

Represents a building and includes methods to:

Add readings

Compute total consumption

Generate daily usage

Identify peak usage time

BlockManager

Handles multiple buildings at once, collects readings for each building, and produces a building-wise summary.

The OOP design keeps the logic organized and mirrors real-world modeling of buildings and meter readings.

7. Dashboard Visualization

A three-panel dashboard was produced and saved as dashboard.png.

7.1 Daily Consumption Line Plot

Shows daily energy usage trends for each building.
Admin consistently shows higher consumption compared to Library and Hostel.

7.2 Average Weekly Consumption Bar Chart

Illustrates the weekly average usage for each building.
This clearly highlights the highest-demand buildings.

7.3 Peak Hour Scatter Plot

Displays the maximum recorded kWh value for each building.
This helps identify which buildings experience sudden load spikes.

8. Key Findings

From the analysis:

Admin building shows the highest overall electricity consumption.

Library follows a steady pattern with moderate peaks in midday hours.

Hostel has the lowest overall consumption.

Peaks generally occur in the afternoon for all buildings.

The dataset, although simple, demonstrates clear differences in usage behaviors.

These findings can help campus authorities make informed decisions about energy distribution and load balancing.

9. Exported Outputs

The program generates the following files in the /output directory:

cleaned_energy_data.csv – full cleaned dataset

building_summary.csv – summary of each building

dashboard.png – visualization dashboard

summary.txt – executive summary

These outputs provide both visual and analytical insights.

10. Conclusion

This capstone project successfully demonstrates:

Automated file ingestion

Robust data cleaning

Time-series analysis using Pandas

Object-oriented modeling

Professional-style visualization

Creation of structured summaries

The project reinforces the importance of clean data pipelines and modular code structure.
Overall, it provides hands-on experience with real-world data processing tasks that are widely used in data analytics and engineering roles.
