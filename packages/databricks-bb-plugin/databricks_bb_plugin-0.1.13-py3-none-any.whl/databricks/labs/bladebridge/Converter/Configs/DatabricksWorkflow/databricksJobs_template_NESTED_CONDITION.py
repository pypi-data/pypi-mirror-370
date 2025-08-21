XRUNID = "12345"  # Replace with logic to fetch or compute XRUNID dynamically

# Evaluate the complex condition
if %CONDITION%:
    dbutils.jobs.taskValues.set("is_true", "true")
    print("Condition met: Proceeding with 'TaskIfTrue'")
else:
    dbutils.jobs.taskValues.set("is_true", "false")

