sql_stmt_list = [%COMMAND_LIST%]
commandCount = 0
for sql in sql_stmt_list:
    print("Executing SQL command {commandCount}")
    try:
        spark.sql(sql)
    except Exception as e:
        print("Execution error: " + str(e))
    commandCount += 1
