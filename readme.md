I made this simple CLI tool because i wanted a offline, Secured and simple method to merge pdf files. this is a very basic app i know but it solves my usecase. it works on windows, linux & macos. i made PDFmerge a global name so it makes it easy to use. Online tool for this is not safe for sensitive documents and good ones are paid or full of ads & watermarks.

Requirements - 
pypdf>=4.0.0

Usage - 
# basic merge
pdfmergepro a.pdf b.pdf c.pdf

# custom output name
pdfmergepro *.pdf --out final_report.pdf

# with password
pdfmergepro *.pdf --password mypassword123

# compress + custom name
pdfmergepro *.pdf --out compressed.pdf --compress

# dry run - see what would happen without writing anything
pdfmergepro *.pdf --dry

# undo last merge (deletes the output file)
pdfmergepro --undo

# all features at once
pdfmergepro a.pdf b.pdf c.pdf --out report.pdf --password abc --compress


## Global Setup

### macOS / Linux
```bash
mkdir -p ~/.local/bin
cp pdfmergepro.py ~/.local/bin/pdfmergepro
chmod +x ~/.local/bin/pdfmergepro
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
```
Linux with bash: replace `~/.zshrc` with `~/.bashrc`

### Windows
```cmd
mkdir C:\tools
copy pdfmergepro.py C:\tools\
```
Create `C:\tools\pdfmergepro.bat`:
```bat
@echo off
python "%~dp0pdfmergepro.py" %*
```
Then run: `setx PATH "%PATH%;C:\tools"` and reopen terminal.

