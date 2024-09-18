'''
MILP model to assign students to groups while minimizing repeated pairings.
Data: excel file following the format of the example file 'students_data_example.xlsx'
Results: excel file with the group assignments and the objective function value 
'''
import pandas as pd
import os
import time
from itertools import combinations
from ortools.sat.python import cp_model

####################################################################################################
# Parameters (customize these)
session = 'S1'  # Session to solve (should match the column name in the sheet 'attendance_list')
number_of_groups_per_size = {2: 5}  # {size: number_of_groups} (ensure that the sum of number_of_groups * size equals the number of students)
name_data_file = 'students_data_example.xlsx'  # Name of the Excel file with the data
results_data_file = 'students_group_assignments.xlsx'  # Name of the Excel file with the results
####################################################################################################

# Start the timer
start_time = time.time()

# Load data
project_dir = os.getcwd()
data_file_path = os.path.join(project_dir, name_data_file)
df_attendance = pd.read_excel(data_file_path, sheet_name='attendance_list', index_col=0)
df_historical = pd.read_excel(data_file_path, sheet_name='historical_pairings', index_col=0)

# Preprocess (formatting data to be used in the model)
students = df_attendance[df_attendance[session] == 1].index.tolist()
df_historical_filtered = df_historical.loc[students, students]

historical_data = {
    (row.name, col): int(row[col])
    for _, row in df_historical_filtered.iterrows()
    for col in df_historical_filtered.columns
    if pd.notna(row[col])
}

group_size = {} # Required size of each group
group_counter = 1
for size, count in number_of_groups_per_size.items():
    for _ in range(count):
        group_size[group_counter] = size
        group_counter += 1

students_pairs = list(historical_data.keys())
groups = list(group_size.keys())

# MILP Model
# Create the model
model = cp_model.CpModel()

# Decision Variables
# x[i, g]: 1 if student i is assigned to group g, 0 otherwise
x = {}
for i in students:
    for g in groups:
        x[i, g] = model.NewBoolVar(f'x_{i}_{g}')

# z[i, j, g]: 1 if both students i and j are assigned to the same group g, 0 otherwise
z = {}
for (i, j) in students_pairs:
    for g in groups:
        z[i, j, g] = model.NewBoolVar(f'z_{i}_{j}_{g}')

# Objective: Minimize repeated pairings
objective_terms = []
for (i, j) in students_pairs:
    for g in groups:
        objective_terms.append(historical_data.get((i, j), 0)**2 * z[i, j, g])
model.Minimize(sum(objective_terms))

# Constraints

# 1. Each student is assigned to exactly one group
for i in students:
    model.Add(sum(x[i, g] for g in groups) == 1)

# 2. Each group must have the specified number of students
for g in groups:
    model.Add(sum(x[i, g] for i in students) == group_size[g])

# 3. Ensure z[i, j, g] is 1 if both i and j are assigned to the same group
for (i, j) in students_pairs:
    for g in groups:
        model.Add(z[i, j, g] <= x[i, g])
        model.Add(z[i, j, g] <= x[j, g])
        model.Add(z[i, j, g] >= x[i, g] + x[j, g] - 1)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Calculate the execution time
execution_time = time.time() - start_time

# Save the results to a text file
results_file_path = os.path.join(project_dir, f'results_{session}.txt')
with open(results_file_path, 'w') as file:
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        file.write(f"Objective function value is {solver.ObjectiveValue()}\n\n")
        
        # Create a dictionary to store the students in each group
        group_assignments = {g: [] for g in groups}
        
        # Fill the dictionary with the assigned students
        for i in students:
            for g in groups:
                if solver.Value(x[i, g]) > 0.5:  # Check if student i is assigned to group g
                    group_assignments[g].append(i)
        
        # Write the group assignments to the file
        for g in groups:
            file.write(f"Group {g} is formed by:\n")
            for student in group_assignments[g]:
                file.write(f"{student}\n")
            file.write("\n")  # Newline between groups
    else:
        file.write("No solution found.\n")
    file.write(f"Execution time: {execution_time:.2f} seconds\n")

# Create a DataFrame to store the results
results = []
for group, students in group_assignments.items():
    for student in sorted(students):  # Sort students alphabetically
        results.append({'Student': student, 'Group': group})

df_results = pd.DataFrame(results)

# Create a copy of df_historical to modify
df_new_historical = df_historical.copy()

# Update the historical data with the new assignments
for _, row in df_results.iterrows():
    student = row['Student']
    group = row['Group']
    for other_student in group_assignments[group]:
        if student != other_student:
            df_new_historical.loc[student, other_student] += 1


# Save the results to a new Excel file
results_file_path = os.path.join(project_dir, results_data_file)
with pd.ExcelWriter(results_file_path) as writer:
    df_results.to_excel(writer, sheet_name=f'groups_{session}', index=False)
    df_new_historical.to_excel(writer, sheet_name='new_historical')