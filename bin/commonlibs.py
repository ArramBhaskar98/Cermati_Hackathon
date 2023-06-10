import requests
from bs4 import BeautifulSoup
import re
import json
from collections import defaultdict
import threading

# Creating Default Dictionary to store final results based on Department key
final_json_result = defaultdict(list)


def get_urls():
    """ Requesting Cermati careers site to get the number of openings till date """

    # Cermati careers url
    url = "https://www.cermati.com/karir"

    response = requests.get(url)
    if response.status_code == 200:
        print("Response Status Code is: ", response.status_code)
        html_content = response.content

        # Parsing HTML Data using BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # Find an element by tag name
        script_tag = soup.find("script", type="application/json")
        script_content = script_tag.string

        # Applying regular expression to extract all careers opening details under smartRecruiterResult
        pattern = r'"smartRecruiterResult":{.*}'
        match = re.search(pattern, script_content)
        if match:
            print("Match Found for smartRecruiterResult in Response Body")
            script_output = "{" + match.group()

            # Converting the response string object to JSON
            d = json.loads(script_output)

            urls = []

            # All the Job Opening details present under below JSON Tags.
            all_content = d['smartRecruiterResult']['all']['content']

            # Parsing all the Job Opening URLs and storing in List Data Structure
            for dictionary in all_content:
                urls.append(dictionary["ref"])

            return urls
        else:
            print("Match Not Found for Specified Pattern: smartRecruiterResult. Please specify correct Pattern to get Cermati Career Details...!")
            return None
    else:
        print("Error in Fetching response. Please check whether URL is correct..")
        return None


def scraping_urls_data(url):

    """ This method is useful to process the required data for each response such as -
    extracting Job-Id and Title, Location, HTML Parsing for Job Description and Qualification, Job Type and Posted By  """

    parsed_result = {}
    response = requests.get(url)
    if response.status_code == 200:
        d = response.json()

        type_of_employment_id = d["typeOfEmployment"]["id"]
        type_of_employment_label = d["typeOfEmployment"]["label"]
        creator_name = d["creator"]["name"]

        if "department" in d:
            dep_label = d["department"]["label"]
        else:
            dep_label = "NA"

        parsed_result["title"] = d["id"] + " - " + d["name"]
        parsed_result["location"] = d["location"]["city"] + ", " + d["customField"][-1]["valueLabel"]

        desc_soup = BeautifulSoup(d["jobAd"]["sections"]["jobDescription"]["text"], "html.parser")
        qualify_soup = BeautifulSoup(d["jobAd"]["sections"]["qualifications"]["text"], "html.parser")

        parsed_result["description"] = [tag.text for tag in desc_soup.find_all()]
        parsed_result["qualification"] = [tag.text for tag in qualify_soup.find_all()]

        parsed_result["job_type"] = type_of_employment_id if type_of_employment_id != "" else "NA" + ", " + type_of_employment_label if type_of_employment_label != "" else "NA"
        parsed_result["postedBy"] = creator_name if creator_name != "" else "NA"

        # Final processed results for each response are storing based on grouping the Department names.
        try:
            final_json_result[dep_label].append(parsed_result)
        except KeyError:
            print("Key not found in the dictionary: ", d, url)
    else:
        print("Invalid URL Passed..!")


def parallel_thread_calls(careers_urls):

    """ This method is useful to execute the parallel threads for each job opening in Cermati careers page """
    threads = []
    for url in careers_urls:
        thread = threading.Thread(target=scraping_urls_data, args=(url,))
        threads.append(thread)
        thread.start()

    # Waiting for all threads to complete
    for thread in threads:
        # print("Thread in For loop: ", thread)
        thread.join()

    # Converting defaultdict to regular dictionary
    reg_dict = dict(final_json_result)

    # Return Final JSON once all parallel thread executions are completed
    return reg_dict

