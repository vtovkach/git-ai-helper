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

@dataclass 
class File:
    file_path:    str
    file_name:    str
    file_diff:    str 
    commit_msg:   str 
    file_status:  str   # modified, staged, untracked 
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
    #   -<file #> 
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

        if user_input == "exit":
            repo.git.reset()
            break

        parts = user_input.split()      # split by spaces 
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
                    except ValueError:
                        print(" File number is invalid")
                        continue
                    displayCommitMsg(False, file_num)
                else:
                    print("Undefined options in \"{cmd}\" command. Try \"help\"") 
            else:
                print("Undefined options in \"{cmd}\" command. Try \"help\"") 
                
        elif cmd == "redo":
            pass 
        elif cmd == "commit":
            pass
        elif cmd == "uncommit":
            pass 
        elif cmd == "clear":
            os.system("clear")
        else:
            print(f"Undefined command: \"{user_input}\". Try \"help\"")
            continue

    return 0
    

def processRepo() -> None:

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
    temperature = 0 if not isCreative else 1

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
        try:
            target_file = GitaStaginArea[file_number - 1]
        except IndexError:
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

# Run GITA 
if __name__ == "__main__":
    main()


# Add the following functunality:
#   - display commit message 
#   - 
#   - add posibility to redo commit message 
#       - allow user to use their own messages 
#       - or request new message from ai  
#       - 
#   - commit changes 
#       - commit all at once 
#       - commit certain file
#       - 
#   - remove commit from 'ready to commit' 
#   

# Other things to do 
#   - Error handling 
#   - Improve ai prompt for better git commit message       !!! DONE !!!
#   - Handle git divergences                                
#   - Speed up chatgpt requests 

