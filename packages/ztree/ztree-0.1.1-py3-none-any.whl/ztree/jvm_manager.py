import jpype
import os

def start_jvm():
    if not jpype.isJVMStarted():
        jar_path = r"C:/Users/ericr/Documents/ztree/ztree/lib/subway.jar"
        jpype.startJVM(jpype.getDefaultJVMPath(),
               "--enable-native-access=ALL-UNNAMED",
               classpath=[jar_path])

def stop_jvm():
    if jpype.isJVMStarted():
        jpype.shutdownJVM()