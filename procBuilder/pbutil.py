# Michael Thomas 912226 - Wrote most functions, variables



import copy
import ryvencore_qt as rc
from ryvencore_qt.src.ryvencore.dtypes import dtypes

# List of valid file types
NUMBER = "number"
STRING = "string"
FOLDER_PATH = "folderPath"

FILE_NAME = "fileName"

FILE_LIST = "fileList"
FILE_LIST_VTK = "fileListVtk"
FILE_LIST_VTK_VALID = "fileListVtkValid"
FILE_LIST_VTK_INVALID = "fileListVtkInvalid"
FILE_LIST_GIPL= "fileListGipl"
FILE_LIST_TFMAT = "fileListTFMAT"

TYPES_FILE_LIST = {FILE_LIST, FILE_LIST_VTK, FILE_LIST_VTK_VALID, FILE_LIST_VTK_INVALID, FILE_LIST_GIPL, FILE_LIST_TFMAT}
TYPES_FILE_LIST_VTK = {FILE_LIST_VTK, FILE_LIST_VTK_VALID, FILE_LIST_VTK_INVALID}

# NOTE: this class has issues, as when used it creates a label on the nodes. It is no longer needed, but has been left as it provides information about DTypes
# class TypedData(dtypes.DType):
#     """A generic dictionary that has type and data fields"""

#     def __init__(self, typeName: str = "", dataValue=None, doc: str = "", _load_state=None):
#         self.typeName = typeName
#         self.dataValue = copy.deepcopy(dataValue)
#         default = getNewTypedData(typeName=self.typeName, dataValue=self.dataValue)
#         super().__init__(default=default, doc=doc, _load_state=_load_state)
#         self.add_data('typeName')
#         self.add_data('dataValue')

def isValidTypedData(data):
    '''Check if a piece of data is non-empty'''
    try:
        return (data["type"] != "") and (data["data"] != None)
    except:
        return False

def getNewTypedData(typeName: str = "", dataValue=None):
    '''Create a new typed data dictionary'''
    return {"type": typeName, "data": dataValue}

def isSameType(outputType, inputType):
    '''Custom method to check if two types are equivalent'''
    if outputType == inputType: # Are actually the same
        return True
    # Otherwise, check if we think they are the same
    elif isFileListType(outputType) and inputType == FILE_LIST: 
        # Can decrease FileList specificity, but not increase it
        return True
    elif isFileListVtkType(outputType) and inputType == FILE_LIST_VTK:
        # Can decrease FileList specificity, but not increase it
        return True
    # Else, are not the same
    return False

# Custom type checker for file list
def isFileListType(typeName):
    '''Check if type is compatable with FileList'''
    return typeName in TYPES_FILE_LIST

def isFileListVtkType(typeName):
    '''Check if type is compatable with FileListVtk'''
    return typeName in TYPES_FILE_LIST_VTK
