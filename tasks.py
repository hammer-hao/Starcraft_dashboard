from SC2 import APIrequests, dataprocessing

fetcheddata = APIrequests.getplayersandmatchdata()

dataprocessing.processmatches(fetcheddata)

