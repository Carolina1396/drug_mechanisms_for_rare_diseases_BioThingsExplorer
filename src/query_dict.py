#Import libraries

from config import SERVER_URL
from config import TIMEOUT
import os
import requests #HTTP library for Python
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from urllib.parse import urljoin #combining URL components into a URL string
import json
import csv


# Get current working directory
__location__ = (os.getcwd())


#Save query response in a folder
def save_response (response, template, mondo_id, chembl_id):
    """
    This function will save the responses on independent json files but in the same folder.
    Folder will be named based on metapath template
    Files will be named based on gard_id + metapath template
    template: metapath template
    response: query response
    gard_id: disease id

    return: json file saved on  folder (../results)
    """

    # Directory to save query_responses
    query_resp_dir = os.path.join(__location__, "../results/")


    # To write the name of file as: "mondo_id + "categories" names":
    ## Access to nodes of metapath template
    template = template["message"]["query_graph"]["nodes"].values()

    ## And then access to "categories" values and save them together as one string (categ_name)
    categ_name = ""
    for node in template:
        for val in (node["categories"]):
            categ_name = categ_name + (str(val[val.find(":") + 1:])) + "_"  # Save value after ":"

    ## Set up directory for folder where respones will be saved
    directory = os.path.join(query_resp_dir, categ_name)

    # create the directory if doesnt exist already
    if not os.path.isdir(directory):
        os.mkdir(directory)

    # Set name and location of new file
    filename = str(mondo_id) + "_" + categ_name + str(chembl_id)  # file name
    file_path = os.path.join(directory, filename) #Path to save file

    # write file with response
    with open(file_path, "w") as outfile:
        f = json.dump(response, outfile)
    return (f)


#Request function
def make_request(mondo_id, chembl_id, template):
    """
    Send  request to SERVER_URL/v1/query
    :gard_id: Genetic and Rare Diseases id
    :template: Query path requested
    :return: response in json format
    """

    #Template for query request. Takes the gard_id as n0
    if mondo_id != None:
        if chembl_id != None:
            template["message"]["query_graph"]["nodes"]["n0"]["ids"] = [str(mondo_id)] #Mondo ID
            template["message"]["query_graph"]["nodes"]["n1"]["ids"] = ["CHEMBL.COMPOUND:"+ str(chembl_id)] #CHEMBl ID

            try:
                print (f"Request for {mondo_id},{chembl_id}")

                doc = requests.post(urljoin(SERVER_URL, "/v1/query"), json=template, timeout=TIMEOUT)

                if doc.status_code == 200:  # Request was successful
                    data = doc.json()  
                    save_response(data, template, mondo_id, chembl_id) # Save response json file

                    if len(data["message"]["knowledge_graph"]["nodes"].values()) > 0:
                        print("Call was successful")
                    if len(data["message"]["knowledge_graph"]["nodes"].values()) == 0:
                        print("Call was successful but doesnt have response")
                    return (data)
                else:
                    data = ("Error_Type:", "BTE timed out")
                    print (data)
                    save_response(data, template, mondo_id, chembl_id)
                    return (data)

                # Request exceptions
            except requests.exceptions.HTTPError as errh:
                data = ("Error_Type:", repr(errh))
                # Save response json file
                save_response(data, template, mondo_id, chembl_id)
                print ("Call to mondo_id failed. An Http Error occurred:{0}".format(repr(errh)))
                return (data)

            except requests.exceptions.ConnectionError as errc:
                data = ("Error_Type:", repr(errc))
                # Save response json file
                save_response(data, template, mondo_id, chembl_id)
                print("Call to mondo_id failed. An Error Connecting to the API occurred:{0}".format(repr(errc)))
                return (data)

            except requests.exceptions.Timeout as errt:
                data = ("Error_Type:", repr(errt))
                # Save response json file
                save_response(data, template, mondo_id, chembl_id)
                print("Call to mondo_id failed.A Timeout Error occurred:{0}".format(repr(errt)))
                return (data)

            except requests.exceptions.RequestException as err:
                data = ("Error_Type:", repr(err))
                # Save response json file
                save_response(data, template, mondo_id, chembl_id)
                print("Call to mondo_id failed. An Unknown Error occurred: {0}".format(repr(err)))
                return (data)


def eval_saved_res (mondo_id, chembl_id, template):
    """
    This function evaluates if response of gard_id is saved and if it was successful.
    It makes request if gard_id hasnt been evaluated or if if there was an error on request/response
    """

    #Access to files to evaluate
    ## Access to nodes of metapath template
    data = template["message"]["query_graph"]["nodes"].values()

    ## Get the name of folder (name_metapath):
    ## Access to "categories" values  of template
    categ_name = ""
    for node in data:
        for val in (node["categories"]):
            categ_name = categ_name + (str(val[val.find(":") + 1:])) + "_"  # Save value after ":"


    #Evaluate if path exist or creat it.
    ## Set up directory
    # Directory to save query_responses
    query_resp_dir = os.path.join(__location__, "../results/")
    directory = os.path.join(query_resp_dir, categ_name)  # Create the directory using "categories" name

    # create the directory if doesnt exist already
    if not os.path.isdir(directory):
        os.mkdir(directory)

    # name of the file with the gard_id
    resp_path = (os.path.join(__location__, "../results/" + categ_name))  # Directory of folder
    filename = (str(mondo_id) + "_" + categ_name + str(chembl_id))  # file name
    all_files = os.listdir((((resp_path) )))

    # Make request if file  doesnt exist
    if filename not in all_files:
        return(make_request(mondo_id, chembl_id, template))

    # If file exist, evaluate if it doesnt have an error. Make request if error
    if filename in all_files:
        # Evaluate response status of each file
        with open(resp_path + "/" + filename) as a_file:
            resp = json.load(a_file)

            # Request was successful, evaluate if response is NOT empty
            if "message" in resp:
                print ("Response of: " + str(mondo_id) + "-"+ str(chembl_id) + " " + "is already saved")
                return (resp)
           

            # Request was not successful
            if "BTE timed out" in resp:
                #print ("An Error Type of MONDO: " + str(mondo_id) + "-"+ str(chembl_id) + " " + "is already saved")
               #return (resp)
                return(make_request(mondo_id, chembl_id, template))
                
            if "ConnectionError" in resp:
                #print ("An Error Type of MONDO: " + str(gard_id) + " " + "is already saved")
                 return(make_request(mondo_id, chembl_id, template))

#Evaluate if response has unii of interest
def check_response(response):
    """
    This function check if the query response contains the unii id of interest
    :response: Response results of query request
    :unii: unique ingredient identifier
    """

    # Error on request
    if "Error_Type:" in response:
        return ("Request error")

    # Evalaute if UNII is on message
    if "message" in response:
        if len(response["message"]["knowledge_graph"]["nodes"].values()) != 0:
            print ("True")
            return ("True")
            
        if len(response["message"]["knowledge_graph"]["nodes"].values()) == 0:
            print ("False")
            return ("False")

        
#Make request and evaluate  response
def query(output_file, template_path):
    """
    :output_file: csv File to save results
    :template_path: Metapath templates

    This function open the oopd dictionary json file. And then makes request for each gard id and evaluate response for corresponding unii's
    This function takes the response and then calls the check_if _response_contain_unii function.
    Results are returned in csv file.

    """

    #open oop.json
    with open("data/mondo_chembl_id.json",) as a_file:
        data = json.load(a_file)

        # Open output_file as write mode
        with open(output_file, 'w', newline='') as outputfile:

            # Open request path as json object form
            with open(template_path) as f:
                template_file = json.load(f)

                # Write headers of the outputfile.csv
                fieldnames = ['mondo id', 'chembl id', 'has hit']
                writer = csv.DictWriter(outputfile, fieldnames=fieldnames)
                writer.writeheader()


                #Iterate over the gard:unii dictionary file
                for key in data:
                    mondo_id = key["MONDO"]
                    chemb_list = key["CHEMBL"]
                    for chembl_id in chemb_list:
                        api_res = eval_saved_res(mondo_id, chembl_id, template_file) #Evaluate if file is saved and make request 

                    #Check if response has unii and save results in csv
                        if api_res:
                            writer.writerow({'mondo id': mondo_id, 'chembl id': chembl_id, 'has hit': check_response(api_res)})
