
import subprocess

# Execute the command with error handling and output redirection
try:
    result = subprocess.run(["sh", "./runScanner.sh"], stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL )
except subprocess.CalledProcessError as error:
    print(f"Error running command: {error}")


'''with open("images/test.png", 'rb') as f:
    img_data = f.read
    
url = ""
headers = {"": ""} 

r = requests.post(url, headers=headers)

files = {"image": ("test.png", img_data)}

r = requests.post(url, headers=headers, files=files)

if r.status_code == 201:
    print("Image uploaded successfully!")'''
