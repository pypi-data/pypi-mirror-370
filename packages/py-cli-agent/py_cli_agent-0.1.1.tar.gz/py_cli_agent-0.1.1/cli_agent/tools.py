import os

class Tools:
    # File Operations
    @staticmethod
    def createFile(filePath: str, content: str):
        with open(filePath, "w") as file:
            file.write(content)

    @staticmethod
    def readFile(filePath: str):
        with open(filePath, "r") as file:
            return file.read()

    @staticmethod
    def writeFile(filePath: str, content: str):
        with open(filePath, "w") as file:
            file.write(content)

    @staticmethod
    def deleteFile(filePath: str):
        os.remove(filePath)

    # Folder Operations
    @staticmethod
    def createFolder(folderPath: str):
        os.makedirs(folderPath, exist_ok=True)

    @staticmethod
    def deleteFolder(folderPath: str):
        os.rmdir(folderPath)

    # General Utilities
    @staticmethod
    def executeCommand(command: str):
        os.system(command)

    @staticmethod
    def getCurrentDirectory():
        return os.getcwd()

    @staticmethod
    def changeDirectory(directory: str):
        os.chdir(directory)
