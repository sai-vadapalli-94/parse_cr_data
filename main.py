# TODO: segregate function into their py files and import them into main, keeps the code neat and tidy
# TODO: take input from user to write to files for varying query states
# TODO: build a easy to use front end UI
# TODO: added the following graphs
"""
1. **Request latency distribution**: Create a histogram or a density plot to show the distribution of the `elapsedTime` field. This can help us understand the typical latencies for requests and identify any outliers or long-tail latencies.

2. **Request rate over time**: Plot the number of requests per unit time (e.g., per second, minute, or hour) to visualize the request rate trends and patterns. 
This can help us identify peak usage times, potential capacity issues, and seasonality in the request volume.

3. **Error count and types**: If the JSON file contains requests with errors (i.e., `errorCount` > 0), create a bar chart to show the distribution of error types. This can help us identify the most common errors and prioritize debugging and fixes.

4. **Phase-wise latencies**: Break down the `elapsedTime` field into phase-wise latencies using the `phaseTimes` field. Create a stacked bar chart or a heatmap to visualize the contribution of each phase (e.g., `authorize`, `delete`, `fetch`, `filter`, `primaryScan`) to the overall request latency. This can help you identify potential bottlenecks and optimize the system's performance.

5. **Client context and user agent distribution**: Create a pie chart or a bar chart to show the distribution of the `clientContextID` and `userAgent` fields. This can help us understand the different clients and user agents that are accessing the Couchbase server and their relative request volumes.

6. **Request type and keyspace distribution**: Create a bar chart or a treemap to show the distribution of the `statementType` (e.g., `DELETE`) and `namespace` (e.g., `#system:prepareds`) fields. This can help us understand the types of requests and the keyspaces that are being accessed, and identify any potential capacity or load balancing issues.
"""

# imports
import sys
from functions import *

def main():
    cmdArgs = sys.argv
    try:
        if len(cmdArgs) < 2:
            raise ValueError(
                "Error: No command line arguments provided. Please provide the completed_reque sts file name as an argument."
            )
        fileName = cmdArgs[1]
        print(f"\nProcessing file: {fileName}")
        createProcessedFilesFolder()
        with open(fileName, "r") as file:
            data = json.load(file)
            plotNodeRequests(data)
            countErrors(data)
            print(f"the errors and no errors query statement are: {countErrors(data)}\n")
            plotPieGraphOfErrors(countErrors(data))
            unpackAndDumpData(data)
            # create a list of query state names and their corresponding counts
            countUniqueStatements(data)
            print(f"Count and query state: {countQuerieState(data)}\n")
            plotBarGraphStatesVCounts(
                timeoutQueries=countQuerieState(data)["timeout"],
                completedQueries=countQuerieState(data)["completed"],
                closedQueries=countQuerieState(data)["closed"],
                fatalQueries=countQuerieState(data)["fatal"],
            )
            print(f"The total number of queries are: {sum(countErrors(data).values())}\n")
        
    except ValueError as e:
        sys.exit(1)

if __name__ == "__main__": 
    main()
