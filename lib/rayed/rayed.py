import os

class SimpleNano:
    def __init__(self, filename=None):
        self.filename = filename
        self.content = []

    def open_file(self):
        if self.filename and os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                self.content = file.readlines()
        else:
            print(f"{self.filename} does not exist. Creating a new file.")
            self.content = []

    def save_file(self):
        if not self.filename:
            self.filename = input("Enter the filename to save as: ")
        with open(self.filename, 'w') as file:
            file.writelines(self.content)

    def display_content(self):
        for idx, line in enumerate(self.content):
            print(f"{idx + 1}: {line}", end='')

    def run(self):
        if self.filename:
            self.open_file()
        else:
            self.filename = input("Enter the filename to open or create: ")
            self.open_file()
        
        while True:
            self.display_content()
            command = input("\n(i)nsert, (d)elete, (s)ave, (q)uit: ").strip().lower()
            if command == 'i':
                line = input("Enter text to insert: ")
                self.content.append(line + '\n')
            elif command == 'd':
                line_no = int(input("Enter line number to delete: ")) - 1
                if 0 <= line_no < len(self.content):
                    self.content.pop(line_no)
                else:
                    print("Invalid line number.")
            elif command == 's':
                self.save_file()
                print("File saved.")
            elif command == 'q':
                break
            else:
                print("Unknown command.")

if __name__ == "__main__":
    filename = input("Enter filename to edit: ").strip()
    editor = SimpleNano(filename)
    editor.run()