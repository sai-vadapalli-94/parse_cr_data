import json
import matplotlib.pyplot as plt
import seaborn as sns
import os
import math


def createProcessedFilesFolder() -> None:
    folderName = "processedCRFiles"
    
    # dump all the processed files into a directory
    if not os.path.exists(folderName):
        os.mkdir(folderName)
        print(f"\nFolder '{folderName}' created successfully.")
    else:
        print(f"\nFolder '{folderName}' already exists.")
    
    subDirectories = ["plots", "dataExtracts"]
    for subDir in subDirectories:
        subDirPath = os.path.join(folderName, subDir)
        if not os.path.exists(subDirPath):
            os.mkdir(subDirPath)
            print(f"\nSubdirectory '{subDir}' created successfully.")
        else:
            print(f"\nSubdirectory '{subDir}' already exists.")


def countQuerieState(data) -> dict[str, int]:
    queryStates = {"timeout": 0, "completed": 0, "closed": 0, "fatal": 0}
    for result in data["results"]:
        state = result["state"]
        if state in queryStates:
            queryStates[state] += 1

    return queryStates


# count unique queries
def countUniqueStatements(data: dict) -> None:
    uniqueStatements = set()
    for result in data["results"]:
        statement = result.get("statement", None)
        uniqueStatements.add(statement)

    with open("processedCRFiles/dataExtracts/uniqueStatements.json", "a") as outFile:
        for item in uniqueStatements:
            json.dump(item, outFile)
            outFile.write("\n")


def countErrors(data: dict):
    countErr: dict = {"errors": 0, "noErrors": 0}
    for result in data["results"]:
        errors = result["errorCount"]
        if errors != 0:
            countErr["errors"] += 1
        else:
            countErr["noErrors"] += 1

    return countErr


def convertToSeconds(timeStr: str) -> float:
    # Strip the 's' at the end
    timeStr = timeStr.strip("s")
    # Split the string into minutes and seconds
    if "m" in timeStr:
        minutes, seconds = timeStr.split("m")
        totalSeconds = int(minutes) * 60 + float(seconds)
    else:
        totalSeconds = float(timeStr)

    return math.floor(totalSeconds)


# print to STD out, in case if you don't need to write to a file
def printQeurySpecs(
    statement: str,
    state: str,
    scanConsistency: str,
    node: str,
    elapsedTime: str,
    resultCount: str,
    phaseTimes: str,
    requestSize: str,
    userAgent: str,
):
    print(f"Statement: {statement}")
    print(f"State:  {state}")
    print(f"Scan Consistency: {scanConsistency}")
    print(f"Node:  {node}")
    print(f"Elapsed Time: {elapsedTime}")
    print(f"Result Count: {resultCount}")
    print(f"phaseTimes: {phaseTimes}\n")
    print(f"Request Time: {requestSize}")
    print(f"User issue the query: {userAgent}")


def writeToFile(
    statement: str,
    state: str,
    scanConsistency: str,
    node: str,
    elapsedTime: str,
    resultCount: str,
    resultSize: str,
    phaseTimes: str,
    requestSize: str,
    userAgent: str,
    clientContextID: str,
    fileName: str,
) -> None:
    with open(fileName, "a") as outFile:
        dataToWrite = {
            "statement": statement,
            "state": state,
            "scanConsistency": scanConsistency,
            "node": node,
            "elapsedTime": elapsedTime,
            "resultCount": resultCount,
            "resultSize": resultSize,
            "phaseTimes": phaseTimes,
            "requestTime": requestSize,
            "userAgent": userAgent,
            "clientContexID": clientContextID
        }
        json.dump(dataToWrite, outFile)
        outFile.write("\n")  # Add a newline between entries


def unpackAndDumpData(data: dict) -> None:
    for result in data["results"]:
        statement = result.get("statement", None)
        state = result["state"]
        node = result["node"]
        scanConsistency = result["scanConsistency"]
        elapsedTime = result["elapsedTime"]
        resultCount = result["resultCount"]
        resultSize = result["resultSize"]
        phaseTimes = result["phaseTimes"]
        requestSize = result["requestTime"]
        userAgent = result["userAgent"]
        clientContextID= result["clientContextID"]
        # queries that took longer than 40 seconds
        if convertToSeconds(elapsedTime) > 40:
            # printQeurySpecs(statement, state, scanConsistency, node, elapsedTime, resultCount, phaseTimes, requestSize, userAgent)
            writeToFile(
                statement,
                state,
                scanConsistency,
                node,
                elapsedTime,
                resultCount,
                resultSize,
                phaseTimes,
                requestSize,
                userAgent,
                clientContextID,
                fileName="processedCRFiles/dataExtracts/dataExtractMoreThan40secs.json"
            )

        # write to a file for queries that timed out
        if state == "timeout":
            # printQeurySpecs(statement, state, scanConsistency, node, elapsedTime, resultCount, phaseTimes, requestSize, userAgent)
            writeToFile(
                statement,
                state,
                scanConsistency,
                node,
                elapsedTime,
                resultCount,
                resultSize,
                phaseTimes,
                requestSize,
                userAgent,
                clientContextID,
                fileName="processedCRFiles/dataExtracts/dataExtractOnlyTimeouts.json"
            )

        # write to a file for queries that were in fatal state
        if state == "fatal":
            # printQeurySpecs(statement, state, scanConsistency, node, elapsedTime, resultCount, phaseTimes, requestSize, userAgent)
            writeToFile(
                statement,
                state,
                scanConsistency,
                node,
                elapsedTime,
                resultCount,
                resultSize,
                phaseTimes,
                requestSize,
                userAgent,
                clientContextID,
                fileName="processedCRFiles/dataExtracts/dataExtractsOnlyFatals.json"
            )


# ------------------------------------------------------Plotting functions------------------------------------------------------------------------------


def plotBarGraphStatesVCounts(
    timeoutQueries: int, completedQueries: int, closedQueries: int, fatalQueries: int
) -> None:
    states = ["timeout", "completed", "closed", "fatal"]
    counts = [timeoutQueries, completedQueries, closedQueries, fatalQueries]
    plt.figure()
    plt.bar(states, counts)  # create a bar plot
    plt.title("Query States")
    plt.xlabel("states")
    plt.ylabel("counts")
    plt.savefig("./processedCRFiles/plots/barGraphQueryStatesvCount.png", dpi=600)


def plotNodeRequests(data: dict) -> None:
    # Initialize a dictionary to hold the count of requests per node
    nodeCounts = dict()
    # Iterate through the results to count requests per node
    for result in data["results"]:
        node = result["node"]
        if node in nodeCounts:
            nodeCounts[node] += 1
        else:
            nodeCounts[node] = 1

    # Prepare data for plotting
    nodes = list(nodeCounts.keys())
    counts = list(nodeCounts.values())
    print(f"\nThe nodes are {nodes} and the query requests sent to them are {counts}\n")
    plt.bar(nodes, counts)
    plt.xlabel("Node")
    plt.ylabel("Request Count")
    plt.title("Request Counts per Node")
    # plt.xticks(rotation=45)
    plt.savefig("./processedCRFiles/plots/plotNodeVsSentRequests.png", dpi=600)
    # Save the plot as file
    plt.cla()


def plotPieGraphOfErrors(countVals: dict) -> None:
    keys = list(countVals.keys())
    data = list(countVals.values())
    palette_color = sns.color_palette("Set2")
    # Plot data on chart
    plt.pie(data, labels=keys, colors=palette_color, autopct="%.0f%%", startangle=90)
    plt.title("Queries that had errors and no errors", fontsize=14, color="#000000")
    # Set position of title
    plt.savefig("./processedCRFiles/plots/plotPieGraphOfErrors.png", dpi=600)
