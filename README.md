# Student Group Assignment Optimizer

This repository contains a Mixed Integer Linear Programming (MILP) model to optimally assign students to groups while minimizing repeated pairings based on historical data.

## Table of Contents
- [Overview](#overview)
- [Requirements](#requirements)
- [Usage](#usage)
- [Input Data](#input-data)
- [Output](#output)
- [Example Usage](#example-usage)
- [MILP Formulation](#milp-formulation)

## Overview

This project uses the OR-Tools library to solve a student group assignment problem. The main goal is to create groups of students while minimizing the number of repeated pairings based on historical data. This can be useful for educational settings where you want to ensure students work with a variety of peers over time.

## Requirements

- Python 3.x
- pandas
- OR-Tools

You can install the required packages using pip:

```
pip install requirements.txt
```

## Usage

1. Prepare your input data in an Excel file following the format of `students_data_example.xlsx`.
2. Open `main.py` and adjust the parameters at the top of the file:
   - `session`: The session to solve (should match a column name in the 'attendance_list' sheet)
   - `number_of_groups_per_size`: A dictionary specifying the number of groups for each group size
   - `name_data_file`: Name of the input Excel file
   - `results_data_file`: Name of the output Excel file
3. Run the script:
   ```
   python main.py
   ```

## Input Data

The input Excel file should contain two sheets:

1. `attendance_list`: A matrix with students as rows and sessions as columns. Use 1 to indicate attendance, 0 for absence.
2. `historical_pairings`: A matrix showing how many times each pair of students has worked together previously.

## Output

The script generates two output files:

1. A text file (`results_{session}.txt`) containing:
   - The objective function value
   - Group assignments
   - Execution time
2. An Excel file (`students_group_assignments.xlsx`) containing:
   - A sheet with the new group assignments
   - An updated historical pairings matrix

## Example Usage

1. Input: (`students_data_example.xlsx`) 
2. In (`main.py`):
   ```python
   number_of_groups_per_size = {2: 5}  # 5 groups of 2 students
   ```
3. Run script
4. Output: 
   - (`results_S1.txt`): Group assignments and objective value
   - (`students_group_assignments.xlsx`): New groups and updated pairings

The optimizer minimizes repeated pairings based on historical data.

[Remaining sections of the README]

## MILP Formulation

The MILP problem is formulated as follows:

### Sets and Parameters

- $I$: Set of students
- $G$: Set of groups
- $P$: Set of student pairs $(i,j)$ where $i,j \in I$ and $i < j$
- $s_g$: Size of group $g \in G$
- $h_{ij}$: Historical number of pairings between students $i$ and $j$

### Decision Variables

- $x_{ig}$: Binary variable, 1 if student $i$ is assigned to group $g$, 0 otherwise
- $z_{ijg}$: Binary variable, 1 if both students $i$ and $j$ are assigned to group $g$, 0 otherwise

### Objective Function

Minimize the sum of squared historical pairings for students assigned to the same group:

$$
\text{Minimize} \sum_{(i,j) \in P} \sum_{g \in G} h_{ij}^2 \cdot z_{ijg}
$$

### Constraints

1. Each student is assigned to exactly one group:

   $$\sum_{g \in G} x_{ig} = 1 \quad \forall i \in I$$

2. Each group must have the specified number of students:

   $$\sum_{i \in I} x_{ig} = s_g \quad \forall g \in G$$

3. Ensure $z_{ijg}$ is 1 if both $i$ and $j$ are assigned to the same group:

   $$z_{ijg} \leq x_{ig} \quad \forall (i,j) \in P, g \in G$$
   $$z_{ijg} \leq x_{jg} \quad \forall (i,j) \in P, g \in G$$
   $$z_{ijg} \geq x_{ig} + x_{jg} - 1 \quad \forall (i,j) \in P, g \in G$$

4. Binary constraints:

   $$x_{ig} \in \{0,1\} \quad \forall i \in I, g \in G$$
   $$z_{ijg} \in \{0,1\} \quad \forall (i,j) \in P, g \in G$$

This formulation allows the solver to find an optimal assignment of students to groups while minimizing repeated pairings.
