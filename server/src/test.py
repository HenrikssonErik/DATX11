import subprocess
import time

name = input("What's your name? ")
tic = time.perf_counter()
output = subprocess.check_output(["go", "run", "cidCheck.go", name])
print(output)
result = output.decode().strip()  # convert bytes to string and remove whitespace
print(r)
toc = time.perf_counter()
print(f"Downloaded the tutorial in {toc - tic:0.4f} seconds")
if result == "User Exists":
    print( True)
else:
    print (False) 