import pulp

hours = float(input("Enter the number of free hours you have today \n"))
subjects = int(input("Enter the number of subjects you wish to cover \n"))

names = []
priorities = []
for i in range(subjects):
    print(f"\nEnter the details for subject {i+1}:")
    n = input("Subject Name: ")
    p = int(input("Enter priority points (1-5): "))
    while p < 1 or p > 5:
        print("Invalid input. Please enter a value between 1 and 5.")
        p = int(input("Enter priority points (1-5): "))
    names.append(n)
    priorities.append(p)

M = float(hours)  # safe upper bound for any single x[i]

# Stage 1: maximize number of chosen subjects 
prob1 = pulp.LpProblem("stage1_max_count", pulp.LpMaximize)

x1 = {i: pulp.LpVariable(f"x1_{i}", lowBound=0) for i in range(subjects)}
y1 = {i: pulp.LpVariable(f"y1_{i}", cat="Binary") for i in range(subjects)}
t1 = pulp.LpVariable("t1", lowBound=0)

prob1 += pulp.lpSum(y1[i] for i in range(subjects))

prob1 += pulp.lpSum(x1[i] for i in range(subjects)) <= hours

for i in range(subjects):
    prob1 += x1[i] >= 0.5 * y1[i]
    prob1 += x1[i] <= hours * y1[i]

for i in range(subjects):
    p = priorities[i]
    prob1 += x1[i] - p * t1 <= M * (1 - y1[i])
    prob1 += -(x1[i] - p * t1) <= M * (1 - y1[i])

prob1.solve(pulp.PULP_CBC_CMD(msg=0))

k = int(round(sum(pulp.value(y1[i]) for i in range(subjects))))
if k == 0:
    print("\nNot enough time to allocate at least 0.5 hour to any subject proportionally.")
    raise SystemExit

# Stage 2: fix count k, maximize total allocated hours (tie-break) 
prob2 = pulp.LpProblem("stage2_max_time_given_k", pulp.LpMaximize)

x2 = {i: pulp.LpVariable(f"x2_{i}", lowBound=0) for i in range(subjects)}
y2 = {i: pulp.LpVariable(f"y2_{i}", cat="Binary") for i in range(subjects)}
t2 = pulp.LpVariable("t2", lowBound=0)

prob2 += pulp.lpSum(x2[i] for i in range(subjects))

# total hours cap
prob2 += pulp.lpSum(x2[i] for i in range(subjects)) <= hours

prob2 += pulp.lpSum(y2[i] for i in range(subjects)) == k

for i in range(subjects):
    prob2 += x2[i] >= 0.5 * y2[i]
    prob2 += x2[i] <= hours * y2[i]

for i in range(subjects):
    p = priorities[i]
    prob2 += x2[i] - p * t2 <= M * (1 - y2[i])
    prob2 += -(x2[i] - p * t2) <= M * (1 - y2[i])

prob2.solve(pulp.PULP_CBC_CMD(msg=0))

print("\nOptimal Study Plan:")
for i in range(subjects):
    if pulp.value(y2[i]) is not None and pulp.value(y2[i]) > 0.5:
        x = pulp.value(x2[i])
        x = round(x * 2) / 2
        print(f"Study {names[i]} for {x} hours (Priority {priorities[i]})")
