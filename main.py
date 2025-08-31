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

    print("=====================================================")
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
            # Unstage all uncommited files 
            repo.git.reset()
            break

        elif user_input == "disp":
            displayInitArea()

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
    


'''''
def displayInitArea() -> None:
    # Column widths
    no_width      = 3
    code_width    = 6
    path_width    = max(20, max(len(file.file_path) for file in GitaStaginArea))
    ready_width   = 7
    commit_width  = 9
    push_width    = 7

    # Top border
    print(Fore.CYAN + "┌───┬──────┬" + "─" * path_width +
          "┬" + "─" * ready_width +
          "┬" + "─" * commit_width +
          "┬" + "─" * push_width + "┐" + Style.RESET_ALL)

    # Header row
    print(Fore.CYAN +
          f"│{'No.':<{no_width}}│{'Status':<{code_width}}│{'File Path':<{path_width}}│"
          f"{'Ready':<{ready_width}}│{'Committed':<{commit_width}}│{'Pushed':<{push_width}}│"
          + Style.RESET_ALL)

    # Separator
    print(Fore.CYAN + "├───┼──────┼" + "─" * path_width +
          "┼" + "─" * ready_width +
          "┼" + "─" * commit_width +
          "┼" + "─" * push_width + "┤" + Style.RESET_ALL)

    # Data rows
    counter = 1
    for file in GitaStaginArea:
        ready    = f"{Fore.GREEN}True {Style.RESET_ALL}" if file.isReady    else f"{Fore.RED}False{Style.RESET_ALL}"
        commited = f"{Fore.GREEN}True {Style.RESET_ALL}" if file.isCommited else f"{Fore.RED}False{Style.RESET_ALL}"
        pushed   = f"{Fore.GREEN}True {Style.RESET_ALL}" if file.isPushed   else f"{Fore.RED}False{Style.RESET_ALL}"

        print(f"│{counter:<{no_width}}│{file.file_status:<{code_width}}│{file.file_path:<{path_width}}│"
              f"{ready:<{ready_width}}│{commited:<{commit_width}}│{pushed:<{push_width}}│")
        counter += 1

    # Bottom border
    print(Fore.CYAN + "└───┴──────┴" + "─" * path_width +
          "┴" + "─" * ready_width +
          "┴" + "─" * commit_width +
          "┴" + "─" * push_width + "┘" + Style.RESET_ALL)
    
    return None 
'''''

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


# Run GITA 
if __name__ == "__main__":
    main()


# Add the following functunality:
#   - display commit message 
#   - 
#   - redo commit message 
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

