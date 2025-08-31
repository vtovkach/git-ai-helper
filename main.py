# import openai API 
from openai import OpenAI, AsyncOpenAI 
# import git API 
import git 

from colorama import Fore, Style
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

# Path to the current working directory  
repo = git.Repo(".")

InitialArea = []
StagingArea = []

class AreaType(Enum):
    InitialArea = 1
    StaginArea = 2     

@dataclass 
class File:
        file_path:    str
        file_name:    str
        file_diff:    str 
        commit_msg:   str 
        file_status:  str # modified, staged, untracked 
        isProcessed:  bool 
        
def main():

    # Eximine git repository for changes 
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
        elif user_input == "disp":
             displayInitArea()
        elif user_input == "proc":
             process_repo()
        else:
            continue
    
def exam_repo():
    """
    Examines the current Git repository for changes.

    This function uses `git status --porcelain` to detect all files
    that have been altered compared to HEAD (e.g., untracked, modified,
    staged, deleted, renamed, conflicted). For each file entry:

        - Extracts the Git status code (e.g., "M", "A", "D", "??").
        - Extracts the file path and file name.
        - Creates a `File` dataclass instance with metadata placeholders
          (diff = "", commit_msg = "", isProcessed = False).
        - Appends the instance to the global `InitialArea` list.
    """

    entries = repo.git.status("--porcelain").splitlines()

    for entry in entries:
        status_code = entry[:2].strip()
        path = entry[3:]

        temp_file = File(
             file_path = path,
             file_name = os.path.basename(path),
             file_diff = "",
             commit_msg = "",
             file_status = status_code,
             isProcessed = False
        )

        InitialArea.append(temp_file)

    return 0; 

def process_repo():
    pass 
    # generate all commit messages 

def displayInitArea():
    print(Fore.CYAN + "┌───┬─────┬──────────────────────────────────────────────┬────────────┐" + Style.RESET_ALL)
    print(Fore.CYAN + f"│{'No.':<3}│{'Code':<5}│{'File Path':<46}│{'State':<12}│" + Style.RESET_ALL)
    print(Fore.CYAN + "├───┼─────┼──────────────────────────────────────────────┼────────────┤" + Style.RESET_ALL)

    counter = 1
    for file in InitialArea:
        if(file.isProcessed):  
            print(f"│{counter:<3}│{file.file_status:<5}│{file.file_path:<46}│{Fore.GREEN}processed   {Style.RESET_ALL}│")
        else:
            print(f"│{counter:<3}│{file.file_status:<5}│{file.file_path:<46}│{Fore.RED}unprocessed {Style.RESET_ALL}│")

        counter += 1

    print(Fore.CYAN + "└───┴─────┴──────────────────────────────────────────────┴────────────┘" + Style.RESET_ALL)


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