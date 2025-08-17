import sys
import subprocess
import tempfile
import os

# Python programs (d group)
python_programs = {
    "d1": """L=[60,30,78,23,10]
n=len(L)
for i in range(n-1):
    min=i
    for j in range(i+1,n):
        if L[j]<L[min]:
            min=j
    L[i],L[min]=L[min],L[i]
print(L)

""",

    "d2": """def find_min_max(arr, low, high):
    if low == high:
        return arr[low], arr[low]
    
    if high == low + 1:
        return (min(arr[low], arr[high]), max(arr[low], arr[high]))
    
    mid = (low + high) // 2
    min1, max1 = find_min_max(arr, low, mid)
    min2, max2 = find_min_max(arr, mid + 1, high)
    return min(min1, min2), max(max1, max2)

arr = list(map(int, input("Enter elements of the array separated by spaces: ").split()))
minimum, maximum = find_min_max(arr, 0, len(arr) - 1)

print("Minimum element:", minimum)
print("Maximum element:", maximum)


""",

    "d3": """def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left_half = merge_sort(arr[:mid])
    right_half = merge_sort(arr[mid:])
    return merge(left_half, right_half)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

n = int(input("Enter the number of elements: "))
arr = []

for _ in range(n):
    num = int(input("Enter number: "))
    arr.append(num)

sorted_arr = merge_sort(arr)
print("Sorted list:", sorted_arr)


""",

    "d4": """from collections import deque
graph = {}
n = int(input("Number of nodes: "))
for _ in range(n):
    node = input(f"Node {_+1}: ")
    graph[node] = []
print("Enter edges (u v), type 'done' to stop:")
while True:
    edge = input()
    if edge == "done":
        break
    u, v = edge.split()
    graph[u].append(v)
start = input("Start BFS from: ")
visited = set()
queue = deque([start])
print("BFS:", end=' ')
while queue:
    node = queue.popleft()
    if node not in visited:
        print(node, end=' ')
        visited.add(node)
        queue.extend(graph[node])

""",

    "d5": """def dfs(graph, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)
    print(start, end=' ')
    for neighbor in graph.get(start, []):
        if neighbor not in visited:
            dfs(graph, neighbor, visited)

n = int(input("Enter number of edges: "))
graph = {}

print("Enter edges (e.g., A B):")
for _ in range(n):
    u, v = input().split()
    graph.setdefault(u, []).append(v)
    graph.setdefault(v, [])  # Ensure all nodes are in the graph

start_node = input("Enter start node for DFS: ")
print("DFS Traversal:")
dfs(graph, start_node)

"""
}

# R programs (r group) – real code
r_programs = {
    "r1": """
x = c(4, 5, 6)
y = c(1, 2, 3, 4)
if (length(x) == length(y)) {
  print("both vector length same")
} else {
  print("both vector are not same")
}
""",
    "r2": """
for (i in 1:10) {
  print(paste("i =", i))
  if (i == 5) stop("iteration stopped (on condition) at 5")
}
""",
    "r3": """
fact <- function(n) {
  if (n <= 1) return(1)
  else return(n * factorial(n - 1))
}
n <- as.numeric(readline("Enter n value: "))
print(paste("Factorial of number is:", fact(n)))
""",
    "r4": """
a <- c(8, 10, 4, 6, 23, 5, 9, 8, 5, 4, 8, 7, 8)
print(paste("mean of vector =", mean(a)))
print(paste("median of vector =", median(a)))
print(paste("mode of vector =", names(sort(-table(a)))[1]))
""",
    "r5": """
output_file_path <- "D:/out.txt"
data <- "hello, my name is A"
writeLines(data, output_file_path)
print(paste("Reading a file =", readLines("D:/out.txt")))
""",
    "r6": """
df = data.frame(
  name = c("amiya", "roy", "aish"),
  programming_language = c("C", "Python", "Java"),
  age = c(22, 21, 23)
)
cat("data in dataframe is:\\n")
print(df)
newdf = rbind(
  df,
  data.frame(name = c("Pavan"), programming_language = c("R"), age = c(24))
)
cat("after adding new row(s):\\n")
print(newdf)
""",
    "r7": """
groupA<-c(18,21,24,27,30)
groupB<-c(17,20,23,26,29)
res_ttest<-t.test(groupA,groupB)
print(res_ttest)
"""
}

def open_in_idle(code: str):
    """Open Python code in IDLE."""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code)
        temp_path = f.name
    subprocess.Popen([sys.executable, "-m", "idlelib", temp_path])

def main():
    if len(sys.argv) < 2 or sys.argv[1] == "-h":
        print("# Commands:\n  ig d -h\n  ig r -h")
        return

    cmd = sys.argv[1]

    if cmd == "d" and len(sys.argv) > 2 and sys.argv[2] == "-h":
        print("# Available Python programs:")
        print("  - d1: 1] Selection Sort")
        print("  - d2: 2] Find min/max using Divide & Conquer")
        print("  - d3: 3] Merge Sort")
        print("  - d4: 4] BFS Algorithm")
        print("  - d5: 5] DFS Algorithm")
        return

    if cmd == "r" and len(sys.argv) > 2 and sys.argv[2] == "-h":
        print("# Available R programs:")
        print("  - r1: 1] else stmt & it operator on vectors")
        print("  - r2: 2] for loop & stop with error message")
        print("  - r3: 3] Factorial using recursion")
        print("  - r4: 4] Mean, Median & Mode")
        print("  - r5: 5] Read & Write file")
        print("  - r6: 6] DataFrame manipulation")
        print("  - r7: 7] ANOVA test")
        return

    if cmd in python_programs:
        open_in_idle(python_programs[cmd])
    elif cmd in r_programs:
        print(r_programs[cmd])
    else:
        print("Unknown command. Use ig -h for help.")

if __name__ == "__main__":
    main()
