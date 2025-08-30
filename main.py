# import openai API 
from openai import OpenAI, AsyncOpenAI
# import git API 
from git import Repo

# import other neccessary libaries 
import os 
import subprocess
from dataclasses import dataclass
from enum import Enum

# retrive Openai API Key from the file  
with open("api_key", "r") as f:
        api_key = f.read().strip()

# Initialize OpenAi client with the key 
client = OpenAI(api_key=api_key)

# Here is the logic of the program 
#   - set up file entity 
#   - set up display area
#   - set up gita staging area 
#   

# Path to the current working directory  
repo = os.getcwd()

InitialArea = []
StagingArea = []

class AreaType(Enum):
    InitialArea = 1
    StaginArea = 2     

@dataclass 
class File:
        file_path:   str
        file_name:   str
        file_diff:   str 
        commit_msg:  str 
        type:        str # modified, staged, untracked 
        isProcessed: bool 
        
def main():

    # Eximine repository for all altered files
    exam_repo()

    print("=====================================================")
    print("    Welcome to GITA (Git Assistant Tool)")
    print("")
    print("    An AI-powered tool to help you craft, manage,")
    print("    and streamline Git commits with ease.")
    print("")
    print("    © 2025 Vadym — MIT License")
    print("=====================================================")

    while True:
        user_input = input("(gita) ")

        if user_input == "exit":
            break
        elif user_input == "exam":
            exam_repo()
        elif user_input == "disp -i":
            displayArea()
        elif user_input == "disp -s":
            displayArea()
        else:
            continue
    
def exam_repo():
    pass 
    # exam_repo routine     

    # Get a list of staged files
    # Get a list of Modified files 
    # Get a list of untracked files 

def process_repo():
    pass 
    # generate all commit messages 

def displayArea():
    pass
    # function will display either InitialArea or StaginArea 
    # argument will specify what Area to display 

def addFile():
    pass
    # The function will add specific file into the AreaType List 

def removeFile():
    pass 
    # The function will remove specific file from the AreaType List 

def commitStagingArea():
    pass 
    # this routine will commit all files in the staging area 


# Run GITA 
if __name__ == "__main__":
       main()


'''''
#### Usage Example ####

response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
                {"role": "system", "content": "You are my assistant."},
                {"role": "user", "content": "What is the Green's Theorem"}
        ]
)
print(response.choices[0].message.content)
'''''