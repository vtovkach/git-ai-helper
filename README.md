# AI-Powered Git Assistant
A lightweight AI-integrated Git helper tool for developers. It can automatically generate commit messages using the OpenAI API and lets you commit only the changes you need with clear messages.

---

## Available Commands

### status  
Display staging area.
- `status -none` → Display staging area

---
### disp 
Display commit messages.
- `disp -f<file #>` → Display commit message for the selected file  
- `disp -a` → Display message for every file  

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

---

## Installation

1. Go to the **Releases** section where the tool is hosted.  
2. **Download** the archive file for gita.  
3. Once downloaded, **unzip** the archive.  
4. Make the installer executable:  
   ```bash
   chmod +x install.sh
5. Run the installer:  
   ```bash
   ./install.sh
   ```
6. After installation, you may safely remove the downloaded archive and the unzipped folder.  

---

## Usage

Once installed, you can launch the tool by typing:

```bash
gita
```
