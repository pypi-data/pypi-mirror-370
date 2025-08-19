# coding: utf-8

from krypto_gui_smalk.resource_manager import ResourceManager
from krypto_gui_smalk.tk_inf import App

def main():
    rm = ResourceManager()
    app = App(rm=rm)
    app.mainloop()


if __name__ == "__main__":
    main()
