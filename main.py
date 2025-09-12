from openai import OpenAI, AsyncOpenAI 
from colorama import Fore, Style
from dataclasses import dataclass
import os 
import git 

# retrive Openai API Key from the file  
with open("OpenAi/api_key", "r") as f:
    api_key = f.read().strip()

# Initialize OpenAi client with the key 
client = OpenAI(api_key=api_key)

# Path to the current working directory  
repo = git.Repo(".")

GitaStaginArea = []   

# Represent a number of currently committed files 
CommittedFiles = 0

HEAD_HASH = ""

@dataclass 
class File:
    file_path:    str
    file_name:    str
    file_diff:    str 
    commit_msg:   str 
    file_status:  str    # modified, staged, untracked 
    isReady:      bool 
    isCommited:   bool
    isPushed:     bool
        
def main() -> None:

    # disp 
    #   -none       -> display staging area 
    #   -f<file #>   -> display commit message for the selected file 
    #   -a          -> display message for every file 
    #   
    # redo 
    #   -cmg -f<file #>      -> use gita to regenerate commit message 
    #   -cmo -f<file #>      -> enter user's commit message manually 
    # 
    # commit 
    #   -a              -> commit all files 
    #   -<file #>       -> commit selected file
    # 
    # uncommit   
    #   -a              -> remove all files 
    #   -<file #>       -> specific commit 
    #
    # !!! Once something is removed redisplay all files

    print("\n=====================================================")
    print("    Welcome to GITA (Git Assistant Tool)")
    print("")
    print("    An AI-powered tool to help you craft, manage,")
    print("    and streamline Git commits with ease.")
    print("")
    print("    © 2025 Vadym — MIT License")
    print("=====================================================")

    # Eximine git repository for changes
    print("\n\nProcessing...\n") 
    processRepo()

    while True:
        # Get user input 
        user_input = input("(gita) ")

        parts = user_input.split()     # split by spaces 
        cmd = parts[0]
        args = [arg.lstrip("-") for arg in parts[1:]]

        if cmd == "disp":
            if len(args) == 0:
                displayInitArea()
            elif len(args) == 1:
                if args[0] == "a":
                    # display commit message for every file 
                    displayCommitMsg(True, -1)
                elif args[0][0] == "f":
                    # display commit message for the specific file
                    try:
                        file_num = int(args[0][1:])
                    except (ValueError, IndexError, TypeError):
                        print(" File number is invalid")
                        continue
                    displayCommitMsg(False, file_num)
                else:
                    print("Undefined options in \"{cmd}\" command. Try \"help\"") 
            else:
                print("Undefined options in \"{cmd}\" command. Try \"help\"") 
                
        elif cmd == "redo":
            if len(args) == 2:
                if args[0] == "cmg":
                    try:
                        option = args[1][0]
                    except IndexError:
                        print("Undefined options in \"{cmd}\" command. Try \"help\"")
                        continue
                    if option == "f":
                        try:
                            file_number = args[1][1:]
                            file_number = int(file_number)
                        except (IndexError, ValueError, TypeError):
                            print("Undefined options in \"{cmd}\" command. Try \"help\"")
                            continue
                        redoCommitMsg(True, file_number)
                    else:
                        print("Undefined options in \"{cmd}\" command. Try \"help\"")
                        continue
                elif args[0] == "cmo":
                    try:
                        option = args[1][0]
                    except IndexError:
                        print("Undefined options in \"{cmd}\" command. Try \"help\"")
                        continue
                    if option == "f":
                        try:
                            file_number = args[1][1:]
                            file_number = int(file_number)
                        except (IndexError, ValueError, TypeError):
                            print("Undefined options in \"{cmd}\" command. Try \"help\"")
                            continue
                        redoCommitMsg(False, file_number)
                    else:
                        print("Undefined options in \"{cmd}\" command. Try \"help\"")
                        continue
                else:
                    print("Undefined options in \"{cmd}\" command. Try \"help\"")
            else:
                print("Undefined options in \"{cmd}\" command. Try \"help\"") 

        elif cmd == "commit":
            if len(args) == 0:
                print("Undefined options in \"{cmd}\" command. Try \"help\"") 
                continue
            if len(GitaStaginArea) == 0:
                print("Staging area is empty. Nothing to commit.")
                continue
            elif len(args) == 1 and args[0] == "a":
                commitFiles(True, args)
            else:
                commitFiles(False, args)
        
        elif cmd == "uncommit":
            if len(args) == 0:
                print("Undefined options in \"{cmd}\" command. Try \"help\"")
                continue
            if CommittedFiles == 0:
                print("There is no committed files at the moment.")
                continue
            elif len(args) == 1 and args[0] == "a":
                uncommitFiles(True, args)
            else:
                uncommitFiles(False, args)

        elif cmd == "push":
            pass 
        
        elif cmd == "clear":
            os.system("clear")
        
        elif cmd == "exit":
            # Unstage all files from the current commit
            # Restores them to the state they were in before running 'gita'
            repo.git.reset()                    
            break
        else:
            print(f"Undefined command: \"{user_input}\". Try \"help\"")
            continue

    return 0
    

def processRepo() -> None:
    # Global variable 
    global HEAD_HASH

    # Retrive the hash of the HEAD commit
    HEAD_HASH = repo.head.commit.hexsha

    # Stage all files 
    repo.git.add(A=True)

    # Get file infos 
    entries = repo.git.status("--porcelain").splitlines()

    # Process each file one by one 
    for entry in entries:
        status_code = entry[:2].strip()
        path = entry[3:]

        temp_file = File(
            file_path = path,
            file_name = os.path.basename(path),
            file_diff = getDiff(path),
            commit_msg = "",
            file_status = status_code,
            isReady = True,
            isCommited = False,
            isPushed = False 
        )

        temp_file.commit_msg = getCommitMsg(temp_file, False)

        GitaStaginArea.append(temp_file)

    return None; 
    
def displayInitArea() -> None:
    # Print header
    print(
        Fore.BLUE +
        f"\n{'No.':<4} │ {'Code':<7} │ {'File Path':<30} │ {'Ready to Commit':<20} │ {'Committed':<12} │ {'Pushed':<8}"
        + Style.RESET_ALL
    )
    print("-" * 95)  # separator line

    counter = 1
    for file in GitaStaginArea:
        ready    = f"{Fore.GREEN}{'True':^20}{Style.RESET_ALL}" if file.isReady    else f"{Fore.RED}{'False':^20}{Style.RESET_ALL}"
        commited = f"{Fore.GREEN}{'True':^12}{Style.RESET_ALL}" if file.isCommited else f"{Fore.RED}{'False':^12}{Style.RESET_ALL}"
        pushed   = f"{Fore.GREEN}{'True':^8}{Style.RESET_ALL}"  if file.isPushed   else f"{Fore.RED}{'False':^8}{Style.RESET_ALL}"

        print(
            f"{counter:<4} │ "
            f"{file.file_status:<7} │ "
            f"{file.file_path:<30} │ "
            f"{ready} │ "
            f"{commited} │ "
            f"{pushed}"
            "\n"
        )
        counter += 1

    return None

def getDiff(filepath: str) -> str:
    # get file changes with 5 context lines  
    diff = repo.git.diff("--cached", "-U2", filepath)

    return diff 

def getCommitMsg(file: File, isCreative: bool) -> str:
    temperature = 0 if not isCreative else 1.5

    commit_msg = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {
                "role": "system",
                "content": (
                    "Analyze the Git repo diff provided by the user, then generate a commit message with Subject Line and specific body paragraph \n"
                    "Requirements:\n"
                    "- Subject line: ≤40 characters, concise\n"
                    "- Body: ≤100 characters total \n"
                    "- Message must be clear and very specific \n"
                    "- Format body as a dash list with separate ideas, use new lines so it looks nice"
                ),
            },
            {"role": "user", "content": file.file_diff},
        ],
        temperature=temperature,
    )

    return commit_msg.choices[0].message.content.strip()


def displayCommitMsg(display_all: bool, file_number: int) -> None:
    # Display every file 
    if display_all == True:
        counter = 1
        for file in GitaStaginArea:
            print() # empty line before 
            header = (
                f"{Fore.CYAN}"
                f"{'=' * 20} COMMIT MESSAGE FOR FILE {counter} "
                f"({file.file_path}) "
                f"{'=' * 20}{Style.RESET_ALL}"
            )
            print(header)
            # Commit message in bright green
            print(Fore.GREEN + file.commit_msg + Style.RESET_ALL + "\n")

            counter += 1

    else:
        # Rule out 0 as the file number and all negative numbers 
        if file_number < 1:
            print(f"File {file_number} does not exist!")
            return
        try:
            target_file = GitaStaginArea[int(file_number) - 1]
        except (IndexError, ValueError, TypeError):
            print(f"File {file_number} does not exist!")
            return
        
        print()  # empty line before
        header = (
            f"{Fore.CYAN}"
            f"{'=' * 20} COMMIT MESSAGE FOR FILE {file_number} "
            f"({target_file.file_path}) "
            f"{'=' * 20}{Style.RESET_ALL}"
        )
        print(header)

        # Commit message in bright green
        print(Fore.GREEN + target_file.commit_msg + Style.RESET_ALL + "\n")

    return

def redoCommitMsg(reuse_ai: bool, file_number: int) -> None:
    # Rule out 0 as the file number and all negative numbers
    if file_number < 1:
        print(f"File {file_number} does not exist!")
        return 
    
    # Validate provided file_number 
    try:
        target_file = GitaStaginArea[int(file_number) - 1]
    except (IndexError, ValueError, TypeError) :
        print(f"File {file_number} does not exist!")
        return
    
    # Determine whether to regenerate message with openai gpt or provide own message 
    if(reuse_ai):
        while True:
            target_file.commit_msg = getCommitMsg(target_file, True)
            displayCommitMsg(False, file_number)
            user_input = input("Would you like to save this commit message?(y/n)")
            if user_input.lower() == "y":
                print("Commit message has been successfully updated!\n")
                break; 
            print("Wait please. Generating a new commit message.")
    else:
        target_file.commit_msg = input("Enter your commit message: ")
        print("Commit message has been successfully updated!\n")

    return


def commitFiles(commit_all: bool, args: list[str]) -> None:
    global CommittedFiles
    file_numbers = []

    if commit_all == False:
        for arg in args: 
            if arg[0] == "f":
                try:
                    current_file_num = int(arg[1:])
                    # Rule out 0 as the file number and all negative numbers 
                    if current_file_num < 1:
                        print(f"File {current_file_num} does not exist!")
                        continue
                    file_numbers.append(int(arg[1:]))
                except (IndexError, TypeError, ValueError):
                    print(f"Error accessing provided file number.")
                    break
            else:
                print("Undefined options in \"commit\" command. Try \"help\"") 
            
    if commit_all == True:
        for file in GitaStaginArea:
            if file.isCommited:
                print(f"File {file.file_path} is already committed.")
                continue
            else:
                try:
                    # Comment for now 
                    repo.git.commit(file.file_path, m=file.commit_msg)
                    file.isCommited = True
                    print(f"{file.file_path} has been successfully committed. ✅ done!")
                    CommittedFiles += 1
                except Exception as e:
                    print(f"{file.file_path} has not been committed due to error. ❌ failed! ({e})")
    
    else:
        for file_num in file_numbers:
            try:
                target_file = GitaStaginArea[file_num - 1]
            except (IndexError):
                print(f"File {file_num} does not exist!")
                continue
            if target_file.isCommited:
                print(f"File {target_file.file_path} is already committed.")
                continue
            else:
                try:
                    repo.git.commit(target_file.file_path, m=target_file.commit_msg)
                    target_file.isCommited = True
                    print(f"{target_file.file_path} has been successfully committed. ✅ Done!") 
                    CommittedFiles += 1
                except IndexError:
                    print(f"File {file_num} does not exist! Commit failed! ❌")
    return

def uncommitFiles(uncommit_all: bool, args: list[str]) -> None:
    global CommittedFiles
    global GitaStaginArea

    if uncommit_all == True:
        repo.git.reset("--soft", HEAD_HASH)
        for file in GitaStaginArea:
            if file.isCommited:
                file.isCommited = False
                print(f"{file.file_path} has been uncommitted. 🟠 Done!")
                CommittedFiles -= 1
    else:
        file_numbers = []
        
        # retrive all file nums from args 
        for arg in args:
            if arg[0] == 'f':
                try:
                    current_file_num = int(arg[1:])
                    # Rule out negative numbers including 0 
                    if current_file_num < 1 or current_file_num > len(GitaStaginArea):
                        print(f"File {current_file_num} does not exist!")
                        continue
                    if GitaStaginArea[current_file_num].isCommited == False:
                        print(f"File {GitaStaginArea[current_file_num].file_path} is not committed!")
                        continue
                    file_numbers.append(current_file_num)
                except (IndexError, TypeError, ValueError):
                    print(f"Error accessing provided file number.")
                    break
            else:
                print("Undefined options in \"commit\" command. Try \"help\"")

        # If file_numbers list is not empty then there is at least one specific file to be uncommitted
        if file_numbers:
            # uncommit all of the changes 
            repo.git.reset("--soft", HEAD_HASH)
            for i in range(len(GitaStaginArea)):
                if (i+1) in file_numbers:
                    GitaStaginArea[i].isCommited = False
                    CommittedFiles -= 1
                    print(f"{GitaStaginArea[i].file_path} has been uncommitted. 🟠 Done!")

            # commit all files back except those to be uncommitted
            for file in GitaStaginArea:
                if file.isCommited:
                    repo.git.commit(file.file_path, m=file.commit_msg)
    return 

def pushCommits() -> None:
    # Routine to push all committed changes from local repo to host repo

    # git command error GitCommandError
    pass 

# Run GITA 
if __name__ == "__main__":
    main()


# Add the following functunality:
#   - undo commits
#       - add message about uncommit 
#   - push commits 
#   
#   - make status command 

# Other things to do 
#   - Error handling for openai requests 
#   - Improve ai prompt for better git commit message     
#   - Handle git divergences                                
#   - Speed up chatgpt requests 
#   - !!! Refactor functions !!!        !!! IMPORTANT 
#   - add option to push with token
#
#   Bugs
#       - no bugs at this moment to fix 
#     
#