current_iteration = dbutils.jobs.taskValues.get(taskKey = "%TASK_KEY%", key = "iteration")

# Define the maximum number of iterations
max_iteration = %MAX_ITERATION%
dbutils.jobs.taskValues.set("max_iteration", max_iteration)

# Determine next step
if current_iteration < max_iteration - %STEP%:
    current_iteration += 1
    dbutils.jobs.taskValues.set("iteration", current_iteration)
    dbutils.notebook.exit(current_iteration)  # Pass next iteration