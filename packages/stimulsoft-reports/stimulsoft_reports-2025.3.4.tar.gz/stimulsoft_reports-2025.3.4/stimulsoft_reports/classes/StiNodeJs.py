from __future__ import annotations

import base64
import json
import os
import platform
import shutil
import subprocess
import typing
import urllib.request
from array import array

from stimulsoft_data_adapters.classes.StiFunctions import StiFunctions
from stimulsoft_data_adapters.classes.StiPath import StiPath

from ..enums import StiHtmlMode
from .StiHandler import StiHandler

if typing.TYPE_CHECKING:
    from .StiComponent import StiComponent


class StiNodeJs:

### Fields

    __id: str = None
    __component: StiComponent = None
    __error: str = None
    __errorStack: list = None
    __handler: StiHandler = None


### Options

    version = '22.12.0'
    system = ''
    processor = ''
    architecture = ''
    binDirectory = ''
    workingDirectory = ''


### Properties

    @property
    def error(self) -> str:
        """Main text of the last error."""

        return self.__error
    
    @property
    def errorStack(self) -> array:
        """Full text of the last error as an array of strings."""

        return self.__errorStack
    
    @property
    def id(self) -> str:
        return self.__id


### Parameters

    def __getSystem(self) -> str:
        systemName = platform.system()
        if systemName == 'Windows': return 'win'
        if systemName == 'Darwin': return 'darwin'
        return 'linux'
    
    def __getProcessor(self) -> str:
        return platform.machine()
    
    def __getArchitecture(self) -> str:
        processor = self.__getProcessor()
        bits = '64' if '64' in processor else '32'
        return f'arm{bits}' if processor.startswith('arm') else f'x{bits}'
    
    def __getProduct(self) -> str:
        return 'dashboards' if StiFunctions.isDashboardsProduct() else 'reports'


### Handler

    @property
    def handler(self) -> StiHandler:
        if self.__component == None and self.__handler == None:
            self.__handler = StiHandler()

        return self.__component.handler if self.__component else self.__handler
    
    def __getVersion(self) -> str:
        return self.handler.version
    
    def __getHandlerScript(self) -> str:
        script = self.handler.getHtml(StiHtmlMode.SCRIPTS)
        return script.replace('Stimulsoft.handler.send', 'Stimulsoft.handler.https')


### Helpers
    
    def __clearError(self):
        self.__error = None
        self.__errorStack = None

    def __getNodeError(self, returnError: str, returnCode: int) -> str:
        lines = (returnError or '').split('\n')
        npmError = False
        errors = ['npm ERR', 'Error', 'SyntaxError', 'ReferenceError', 'TypeError', 'RequestError']
        for line in lines:
            if len(line or '') > 0:
                for error in errors:
                    if line.startswith(error):
                        if line.startswith('npm') and not npmError:
                            npmError = True
                            continue
                        return line.rstrip()
                    
                    # Handling a parser error from StiHandler
                    if line.startswith('[') and line.find('StiHandler') > 0 and line.find('StiHandler') < 10:
                        return line.rstrip()
        
        if returnCode != 0:
            for line in lines:
                if not StiFunctions.isNullOrEmpty(line):
                    return line
                
            return f'ExecErrorCode: {returnCode}'
        
        return None
    
    def __getNodeErrorStack(self, returnError: str) -> list:
        return None if StiFunctions.isNullOrEmpty(returnError) else returnError.replace('\r\n', '\n').split('\n')

    def __getSystemPath(self, app) -> str:
        command = f'where /F {app}' if self.system == 'win' else f'which {app}'
        execResult = subprocess.run(command, capture_output=True, shell=True)
        result = execResult.stdout.decode().rstrip()
        lines = result.split('\n')
        return lines[0].strip('"')
    
    def __getInstallPath(self) -> str:
        basePath = os.getcwd()
        return StiPath.normalize(f'{basePath}/nodejs-v{self.version}')
    
    def __setEnvPath(self, app):
        appPath = os.path.dirname(os.path.realpath(app))
        path = os.getenv('PATH')
        if path.find(appPath) < 0:
            separator = ';' if self.system == 'win' else ':'
            newPath = f'{path}{separator}{appPath}'
            os.putenv('PATH', newPath)
        

### Paths

    def __getArchiveExt(self) -> str:
        return 'zip' if self.system == 'win' else 'tar.gz'
    
    def __getArchiveName(self) -> str:
        architecture = self.processor if self.processor == 'armv6l' or self.processor == 'armv7l' else self.architecture
        extension = self.__getArchiveExt()

        return f'node-v{self.version}-{self.system}-{architecture}.{extension}'
    
    def __getArchiveUrl(self) -> str:
        archiveName = self.__getArchiveName()
        return f'https://nodejs.org/download/release/v{self.version}/{archiveName}'

    def __getArchivePath(self) -> str:
        installPath = self.__getInstallPath()
        archiveName = self.__getArchiveName()
        return StiPath.normalize(f'{installPath}/{archiveName}')

    def __getApplicationPath(self, app) -> str:
        appPath = self.__getSystemPath(app)
        if not StiFunctions.isNullOrEmpty(appPath):
            return appPath

        path = self.__getInstallPath() if StiFunctions.isNullOrEmpty(self.binDirectory) else self.binDirectory
        path = StiPath.normalize(path)

        appPath = StiPath.normalize(f'{path}/{app}')
        if os.path.isfile(appPath):
            self.__setEnvPath(appPath)
            return appPath
        
        appPath = StiPath.normalize(f'{path}/bin/{app}')
        if os.path.isfile(appPath):
            self.__setEnvPath(appPath)
            return appPath

        self.__error = f'The executable file "{app}" was not found in the "{path}" directory.'
        return False
    
    def getNodePath(self) -> str:
        """
        Returns the full path to the Node executable, or false if the file was not found.
        
        return:
            The path to the executable file, or False if the path was not found.
        """
        
        app = 'node.exe' if self.system == 'win' else 'node'
        return self.__getApplicationPath(app)

    def getNpmPath(self) -> str:
        """
        Returns the full path to the Npm executable, or false if the file was not found.

        return:
            The path to the executable file, or False if the path was not found.
        """
    
        app = 'npm.cmd' if self.system == 'win' else 'npm'
        return self.__getApplicationPath(app)
    

### Methods

    def __download(self) -> bool:
        installPath = self.__getInstallPath()
        archiveUrl = self.__getArchiveUrl()
        archivePath = self.__getArchivePath()

        try:
            if not os.path.isdir(installPath):
                os.mkdir(installPath, 775)

            urllib.request.urlretrieve(archiveUrl, archivePath)
        except Exception as e:
            self.__error = str(e)
            return False
        
        return True

    def __move(self, fromPath, toPath):
        files = os.listdir(fromPath)
        for sourceFile in files:
            shutil.move(os.path.join(fromPath, sourceFile), toPath)
        
        os.rmdir(fromPath)

    def __extract(self) -> bool:
        installPath = self.__getInstallPath()
        archivePath = self.__getArchivePath()
        
        try:
            shutil.unpack_archive(archivePath, installPath)
        except Exception as e:
            self.__error = str(e)
            return False

        extension = self.__getArchiveExt()
        archiveBasePath = archivePath[0:-len(extension)-1]
        self.__move(archiveBasePath, installPath)
        os.remove(archivePath)
        
        return True


### Public

    def installNodeJS(self) -> bool:
        """
        Installs the version of Node.js specified in the parameters into the working directory from the official website.
        
        return:
            Boolean execution result.
        """

        self.__clearError()
        nodePath = self.getNodePath()

        if nodePath == False:
            self.__clearError()
            
            if self.__download() == False:
                return False

            if self.__extract() == False:
                return False

        return True


    def updatePackages(self) -> bool:
        """
        Updates product packages to the current version.
        
        return:
            Boolean execution result.
        """

        self.__clearError()

        npmPath = self.getNpmPath()
        if npmPath == False:
            return False
        
        product = self.__getProduct()
        version = self.__getVersion()
        command = f'"{npmPath}" install stimulsoft-{product}-js@{version}'

        result = subprocess.run(command, cwd=self.workingDirectory, capture_output=True, text=True, shell=True)
        
        errorText = result.stderr if not StiFunctions.isNullOrEmpty(result.stderr) else result.stdout
        self.__error = self.__getNodeError(errorText, result.returncode)
        self.__errorStack = self.__getNodeErrorStack(errorText)
        
        return StiFunctions.isNullOrEmpty(self.error)

    def run(self, script) -> bytes|str|bool:
        """
        Executes server-side script using Node.js
        
        script:
            JavaScript prepared for execution in Node.js

        return:
            Depending on the script, it returns a byte stream or string data or a bool result.
        """

        self.__clearError()

        nodePath = self.getNodePath()
        if nodePath == False:
            return False

        product = self.__getProduct()
        require = f"var Stimulsoft = require('stimulsoft-{product}-js');\n"
        handler = self.__getHandlerScript()
        command = f'"{nodePath}"'
        input = str(require+handler+script).encode()
        
        result = subprocess.run(command, cwd=self.workingDirectory, input=input, capture_output=True, shell=True)

        stdout = '' if result.stdout == None else result.stdout.decode()
        stderr = '' if result.stderr == None else result.stderr.decode()

        errorText = stderr if not StiFunctions.isNullOrEmpty(stderr) else stdout
        self.__error = self.__getNodeError(errorText, result.returncode)
        self.__errorStack = self.__getNodeErrorStack(errorText)

        if not StiFunctions.isNullOrEmpty(self.error):
            return False

        if not StiFunctions.isNullOrEmpty(stdout):
            try:
                jsonStart = stdout.find(self.__id) + len(self.__id)
                jsonLength = stdout.find(self.__id, jsonStart) - jsonStart
                if jsonLength > 0:
                    jsonData = stdout[jsonStart:jsonStart + jsonLength]
                    jsonObject = json.loads(jsonData)

                if jsonLength < 0 or jsonObject == None:
                    self.__error = 'The report generator script did not return a response.'
                    return False

                if jsonObject['type'] == 'string':
                    return jsonObject['data']
                
                if jsonObject['type'] == 'bytes':
                    return base64.b64decode(jsonObject['data'])
            except Exception as e:
                self.__error = 'ParseError: ' + str(e)
                return False
        
        return True


### Constructor

    def __init__(self, component: StiComponent = None):
        self.__id = StiFunctions.newGuid()
        self.__component = component
        self.system = self.__getSystem()
        self.processor = self.__getProcessor()
        self.architecture = self.__getArchitecture()
        self.workingDirectory = os.getcwd()