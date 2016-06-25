import os


class InputHandler():
    def __init__(self, editor):
        self.editor = editor
        print("Welcome to the level editor!")

    def main(self):
        i = input(">")
        self.handle_input(i)

    def handle_input(self, i):
        args = i.split(" ")
        if args[0] == "save":
            if os.path.isfile(self.editor.current_level):
                print("{} already exists. Overwrite? (y/n) ".format(self.editor.current_level))
                over = input(">")
                if over == "y":
                    self.editor.save_level()
                    print("Saved {}".format(self.editor.current_level))
                else:
                    print("Did not overwrite")
            else:
                self.editor.save_level()
                print("Saved {}".format(self.editor.current_level))
        
        elif args[0] == "load":
            if len(args) == 2:
                self.prompt_save("loading {}".format(args[1]))
                if self.editor.load_level(args[1]):
                    print("Loaded {}".format(args[1]))
                else:
                    print("{} level not found".format(args[1]))
            else:
                print("Error: expected 'load some_file_name'")
        
        elif args[0] == "new":
            if len(args) == 3 or len(args) == 4:
                self.prompt_save("creating a new level")
                if len(args) == 3:
                    default = None
                else:
                    default = int(args[3])
                x, y = int(args[1]), int(args[2])
                self.editor.level_rect = self.editor.make_level_rect(x, y)
                self.editor.level_data = self.editor.make_empty_level(x, y, default)
            else:
                print("Error: expected 'new x_dimension y_dimension [default_tile_type]")

        elif args[0] == "rename":
            if len(args) == 2:
                self.editor.current_level = args[1]
            else:
                print("Error: expected 'rename some_new_name'")
        
        elif args[0] == "name":
            print("The current level is {}".format(self.editor.current_level))

        elif args[0] == "quit" or args[0] == "exit":
            self.prompt_save("exiting")
            self.editor.quit = True
            print("Quiting...")

        else:
            print("'{}' is not a legal command".format(i))
            print("Legal commands are save, load, new, rename, name, quit, exit")

    def prompt_save(self, msg):
        print("Would you like to save before {}? (y/n)".format(msg))
        save = input(">")
        if save == "y":
            self.handle_input("save")
        else:
            print("Did not save {}".format(self.editor.current_level))