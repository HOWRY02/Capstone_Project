
import subprocess

# Execute the command with error handling and output redirection
try:
    result = subprocess.run(["sh", "./src/BRS/runScanner.sh"], stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
except subprocess.CalledProcessError as error:
    print(f"Error running command: {error}")
