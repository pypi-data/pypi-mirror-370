"""
file handling functions
this is a really old module but it works
LGPLv3
email: maru@lithium-dev.xyz (pgp attached)
signal: maru.222
BTC: 16innLYQtz123HTwNLY3vScPmEVP7tob8u
ETH: 0x48994D78B7090367Aa20FD5470baDceec42cAF62 
XMR: 49dNpgP5QSpPDF1YUVuU3ST2tUWng32m8crGQ4NuM6U44CG1ennTvESWbwK6epkfJ6LuAKYjSDKqKNtbtJnU71gi6GrF4Wh
"""


def read(filename):
    with open(filename, "r", encoding="utf-8") as file:
        contents = file.read()
    return contents
def write(fnw, data):
    try:
        fw = open(fnw, "w", encoding="utf-8")
        fw.write(data)
        fw.close()
    except Exception as e:
        print(f"Error: {e}")
def amend(fnw, data):
    #WILL NOT ADD NEWLINE
    try:
        with open(fnw, "r", encoding="utf-8") as read:
            existing_data = read.read()  
        with open(fnw, "w", encoding="utf-8") as write:
            write.write(existing_data + data)
    except Exception as e:
        print(f"Error: {e}")
    print(f"Data appended to {fnw}")
def touch(fnw):
    write(fnw, "")
def nread():
    try:
        fnr = input("Filename to read(utf-8): ")
        fr = read(fnr)
        print(fr)
        input()
    except Exception as e:
        print(f"Error: {e}")
def nwrite():
    fw = input("Filename to write to(utf-8): ")
    print("Enter/Paste your content. Ctrl-D or Ctrl-Z ( windows ) to save it.")
    fr2 = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        fr2.append(line)
    write(fw, fr2)
    print(fr2)
def notepad():
    try:
        s1 = input("would you like to r/w?: ")
        if s1 == "r":
            nread()
        elif s1 == "w":
            nwrite()
        else:
            print("Invalid input. Please enter 'r' or 'w'.")   
    except Exception as e:
        print(f"Error: {e}")
        