import socket

import os
import json
import zipfile
import loggerutility as logger

def get_machine_ip():
    """
    Retrieve the current machine IP address

    :return: IP address
    """
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))

    return s.getsockname()[0]


def decompress_file(file_path, destination_dir):
    """
    Decompress zip/tar file at file_path to destination_dir

    :param file_path: Zip file path
    :param destination_dir: The directory to extract file
    """
    if not os.path.isfile(file_path):
        raise Exception('No file exists at location [{}]'.format(file_path))

    with zipfile.ZipFile(file_path, 'r') as zip_file:
        zip_file.extractall(destination_dir)


def search_recursive(directory, file_names):
    """
    Search file in given directory which is matched file_names, and return the absolute path of file

    :param directory: Directory to search file
    :param file_names: File names to match

    :return: A tuple,
              first value is bool, success or failure
              second value is absolute path of file, if found else None
    """
    if not os.path.exists(directory):
        return False, None

    index_files = [file.lower() for file in file_names]

    for directory_path, directory_names, files in os.walk(directory):
        for file in files:
            if file.lower() in index_files:
                return True, os.path.join(directory_path, file)

    return False, None

def getErrorXml(descr, trace, message=""):
    errorXml = '''<Root>
                    <Errors>
                        <error type="E" id="">
                            <message><![CDATA['''+message+''']]></message>
                            <description><![CDATA['''+descr+''']]></description>
                            <trace><![CDATA['''+trace+''']]></trace>
                            <type>E</type>
                        </error>
                    </Errors>
                </Root>'''

    return errorXml

def getErrorJson(Message,description):
    errorjson = '''{
                    "Root":{
                        "Errors":[
                        {
                            "error":{
                            "message":"'''+Message+'''",
                            "description":"'''+description+'''",
                            "type":"E"
                            }
                        }
                        ]
                    }
                }'''
    return errorjson

def getTraineModelPath(modelType, modelName, modelScope, enterprise=""):
        modelPath=""
        logger.log("inside getTraineModelPath","0")
        logger.log(f"modelScope 95::{modelScope}", "0")
        modelScope =  "global" if modelScope=="G" or modelScope=="global" or modelScope=="g" else "enterprise"
        logger.log(f"modelScope 97::{modelScope}", "0")
        if modelScope=="global":
            logger.log("inside getTraineModelPath if","0")
            modelPath = "/proteus-sense/trained_model/" + modelType.lower() + "/" + modelScope.lower() +  "/"+ modelName.lower()
        else:
            logger.log("inside getTraineModelPath else ","0")
            modelPath = "/proteus-sense/trained_model/" +  modelType.lower()  + "/" + modelScope.lower() + "/" + enterprise.lower() +  "/"+ modelName.lower()
        if not os.path.exists(modelPath):
            os.makedirs(modelPath)
            logger.log(f"inside getTraineModelPath modelPath::{modelPath}","0")
        return modelPath

def createModelScope(modelScope, modelType, modelName, enterprise=""):
        path = "/proteus-sense/trained_model"
        fileName = "modelScope.json"
        filePath = path + "/" + fileName
        if os.path.exists(filePath):
            logger.log(f"File already exists.","0")
        else:
            if not os.path.exists(path):
                os.makedirs(path)   
            with open (filePath,"w") as file:
                fileData={}
                fileData=str(fileData).replace("'", '"')
                logger.log(f"after{str(fileData)}","0")
                file.write(fileData)
                file.close()
                if os.path.exists(filePath):
                    logger.log(f"File created","0")

        with open (filePath,"r") as file:
            FilejsonData = file.read()
            file.close()
            logger.log(f"FilejsonData::{FilejsonData},{type(FilejsonData)}","0")

            modelScopefileJson=json.loads(FilejsonData)
            logger.log(f"parsedJsonData::{modelScopefileJson},{type(modelScopefileJson)}","0")
        
        if modelScope == "global":
            if modelType in modelScopefileJson:
                if modelScope in modelScopefileJson[modelType]:
                    if modelName not in modelScopefileJson[modelType][modelScope]:
                        modelScopefileJson[modelType][modelScope].append(modelName)
                    else:
                        logger.log(f"ModelName exists","0")
                    logger.log(f"if::{modelScopefileJson}","0")

                else:
                    modelScopefileJson[modelType][modelScope] = [modelName]
            else:
                modelScopefileJson[modelType] = {modelScope :[modelName]}
        
        elif modelScope == "enterprise":
            if modelType in modelScopefileJson:
                if modelScope in modelScopefileJson[modelType]:
                    if enterprise not in modelScopefileJson[modelType][modelScope]:
                        modelScopefileJson[modelType][modelScope][enterprise]=[modelName]
                    else:    
                        if not modelName in modelScopefileJson[modelType][modelScope][enterprise]:
                            modelScopefileJson[modelType][modelScope][enterprise].append(modelName)
                        else:
                            logger.log(f"ModelName exists","0")
                else:
                    modelScopefileJson[modelType][modelScope] = {enterprise:[modelName]}
            else:
                modelScopefileJson[modelType] = {modelScope: {enterprise:[modelName]}}
        else:
            logger.log(f"Invalid modelScope received:: {modelScope}","0")
        
        logger.log(f"data: {modelScopefileJson}","0")

        with open (filePath,"w") as file:
            logger.log(f"modelScopefileJson in write mode;::: {modelScopefileJson}","0")    
            modelScopefileJson=str(modelScopefileJson).replace("'", '"')
            logger.log(f"after line 172 :: {str(modelScopefileJson)}","0")
            file.write(modelScopefileJson)
            file.close()
            logger.log(f"File updated","0")
        
        return "File Updated successfully "
    
def write_JsonFile(fileName, intent_input, read_data_json, invokeIntentModel, finalResult=""):
        '''
        This function is used to create a json file and maintain the history count of each input query and its resultant output. 
        Params  :
            fileName            : str  --> userId_uuid.json
            intent_input        : str  --> Stock of item Peanut
            invokeIntentModel   : str  --> OpenAI / LocalAI
            read_data_json      : dict --> [{"role": "user", "content": "Stock of item Peanut"}, {"role": "assistant", "content": ""}
            finalResult         : dict -->  output of the intent query
        '''
        directoryPath = invokeIntentModel + "_Instruction"
        fileName      = directoryPath + "/" + fileName
        
        if len(read_data_json ) != 0:
            with open(fileName, "w") as file :
                if invokeIntentModel == "OpenAI" :
                    read_data_json.append({"role" : "user",       "content"  : [
                                                                                {   
                                                                                    "text":intent_input,
                                                                                    "type":"text"
                                                                                }
                                                                                ] 
                                                        })
                    read_data_json.append({"role" : "assistant",  "content"  : [
                                                                                {   
                                                                                    "text":finalResult,
                                                                                    "type":"text"
                                                                                }
                                                                            ]   
                                                        })
                else:
                    read_data_json.append({"role" : "user",       "content"  :  intent_input })
                    read_data_json.append({"role" : "assistant",  "content"  :  finalResult  })
                json.dump(read_data_json, file)
                file.close()
                logger.log(f"File {fileName} overwritten.")
        else:
            if not os.path.exists(directoryPath):
                os.mkdir(directoryPath)
            with open(fileName, "w") as file:
                if invokeIntentModel == "OpenAI":
                    read_data_json.append({"role" : "user",       "content"  : [
                                                                                {   
                                                                                    "text":intent_input,
                                                                                    "type":"text"
                                                                                }
                                                                                ] 
                                                        })
                    read_data_json.append({"role" : "assistant",  "content"  : [
                                                                                {   
                                                                                    "text":finalResult,
                                                                                    "type":"text"
                                                                                }
                                                                            ]   
                                                        })
                else:
                    read_data_json.append({"role" : "user",       "content"  :  intent_input })
                    read_data_json.append({"role" : "assistant",  "content"  :  finalResult  })
                json.dump(read_data_json, file)
                file.close()
            logger.log(f"File {fileName} created.")

def validate_token(connection, token_id):
    if connection:
        cursor = connection.cursor()
        queryy = f"""
            SELECT TOKEN_STATUS FROM API_AUTH_TOKEN 
            WHERE TOKEN_ID = '{token_id}'
        """
        cursor.execute(queryy)
        is_token_exists = cursor.fetchone()

        logger.log(f"\n is_token_exists value:::\t{is_token_exists}")
        cursor.close()

        if is_token_exists != None:
            TOKEN_STATUS = is_token_exists[0]

            logger.log(f"\n TOKEN_STATUS value:::\t{TOKEN_STATUS}")

            if TOKEN_STATUS == 'A':
                return "active"
            else:
                return "inactive"
        else:
            return "notexist"
    else:
        logger.log("No active connection to close.")
        return "Notexist" 
    
    




