
import subprocess
import os 
import openai
from git import Repo 
from dataclasses import dataclass 

@dataclass 
class Git_Commit:
    file_path:      str 
    diff:           str 
    commit_type:    str 
    commit_msg:     str

# Get 
REPO = Repo(".")

# List to store Git_Commit objects 
COMMITS = [] 

def gita_inspect():  

    # Check if COMMITS Empty 
    # If not, ask user to delete all previous commits from gita 
    # TODO 

    # Get unstaged files info 
    status_lines = REPO.git.status("--porcelain").splitlines()

    for line in status_lines:
        
        # Get status code 
        status = line[: 2].strip()

        # Resolve untracked files 
        if status == "??":
            status = "Untracked"

        # Get path 
        path = line[3:].strip()

        # Initialize object of type Git_Commit 
        commit = Git_Commit(
            file_path = path, 
            diff = "",
            commit_type = status,
            commit_msg = ""
        )

        # Append commit to the list 
        COMMITS.append(commit)

        return 
    
def gita_show():

    print(len(COMMITS))
    for index, commit in enumerate(COMMITS):
        print(f"{index} {commit.commit_type} {commit.file_path}")

    return 
    
def main():

    while(True):

        usr_input = input("gita :> ")

        if usr_input == "inspect":
            gita_inspect()

        elif usr_input == "show":
            gita_show()
        
        elif usr_input == "commit":
            print("commiting")
        elif usr_input == "push":
            print("pushing")
        elif usr_input == "exit":
            break
        else:
            print("no such command")


# Run GITA 
if __name__ == "__main__":
    main()