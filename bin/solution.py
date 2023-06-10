from datetime import datetime
import time
from commonlibs import *

# Start Time for Each run
start_time = time.time()

if __name__ == "__main__":

    print("============ EXECUTION STARTED ============")

    # Getting All Cermati Career URLs from the careers_url list
    careers_urls = get_urls()
    dict_output = parallel_thread_calls(careers_urls)

    # Creating a JSON File to display final output
    output_filename = "output_" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    # Dump the dictionary to JSON File
    with open("../output/"+output_filename+".json", "w") as json_file:
        json.dump(dict_output, json_file)
    print("JSON dumped to Output Folder..!")

    # Calculating the Elapse Time
    end_time = time.time()
    elapse_time = end_time - start_time
    print("Total Elapsed Time is : ", elapse_time, "secs")

    print("============ EXECUTION COMPLETED ============")
