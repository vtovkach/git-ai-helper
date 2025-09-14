# AI-Powered Git Assistant

## Project Status
This project is **still in the development stage**.

---

## Commands

### status  
Display staging area and commit messages.  
- `status -none` → Display staging area  
- `status -f<file #>` → Display commit message for the selected file  
- `status -a` → Display message for every file  

---

### change  
Regenerate or manually provide commit messages.  
- `change -cmg -f<file #>` → Use Gita to regenerate commit message  
- `change -cmo -f<file #>` → Enter a custom commit message manually  

---

### commit  
Commit files to the repository.  
- `commit -a` → Commit all files  
- `commit -<file #>` → Commit the selected file  

---

### uncommit  
Remove files from commit.  
- `uncommit -a` → Remove all files  
- `uncommit -<file #>` → Remove a specific commit 
