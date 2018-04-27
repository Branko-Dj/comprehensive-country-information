# countries name and codes resource - https://mapanet.eu/EN/resources/Countries.asp

import sys
import os
import pandas
import logging
import re
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

class Resource:

    def __init__(self, name, urlsToScrape, fieldsToExtract, isCSV):
        self.name = name
        self.urlsToScrape = urlsToScrape
        self.fieldsToExtract = fieldsToExtract
        self.isCSV = isCSV


class Country:

    # this is called instance variable, all instances of Country share it,
    # this dictionary structure has a format {ISO2_code: country(of type Country)}
    listOfCountries = []

    def __init__(self, ISO2_code, primaryName):
        self.ISO2_code = ISO2_code
        self.primaryName = primaryName
        self.dictionaryOfCountryFields = {"Postal code format": "", "All names": [primaryName],
        "Dialing prefix": "", "Calling code": "", "Currency name": "", "Currency code": "",
        "Currency symbol (first version)": "", "Currency symbol (second version)": "",
        "Date formats": "", "Time formats": "", "Time zones (UTC offset)": "", "System of measurements": "",
        "Locales": "", "Member of EU": "", "Member of NAFTA": "", "Member of NATO": ""}

    def __str__(self):
        return "[Country name: " + self.primaryName + ", countryISOCode: " + self.ISO2_code +\
        ", Postal code format: " + self.dictionaryOfCountryFields["Postal code format"] + "]"

    def modifyField(self, field, value):
        if field not in self.dictionaryOfCountryFields:
            print("The field ", field, " does not exist in class Country")
        else:
            self.dictionaryOfCountryFields[field] = value

    def addCountryToPandasDataFrame(self, dataFrame):
        pass


def extractCountriesNameAndCode(dataCsvPath):
    # Ako ne stavim keep_default_na=False, nece mi ucitati oznaku za Namibiju, jer cita 'NA' kao Not a Number(NaN)
    countriesNameCodeDataframe = pandas.read_csv(dataCsvPath, sep = '\t',
        usecols = ['CountryISO_A2', 'NameEnglish'], keep_default_na=False)
    dict_ = countriesNameCodeDataframe.set_index('CountryISO_A2').to_dict('dict')
    dict_ = list(dict_.values())[0]
    for countryISOCode, countryName in dict_.items():
        Country.listOfCountries.append(Country(ISO2_code=countryISOCode, primaryName=countryName))

def extractPostalCodeFormats(dataCsvPath):
    postalCodesDataFrame = pandas.read_csv(dataCsvPath, usecols=['CountryA2', 'Format'], keep_default_na=False)
    dict_ = postalCodesDataFrame.set_index('CountryA2').to_dict('dict')
    postalCodesDictionary = list(dict_.values())[0]
    for country in Country.listOfCountries:
        try:
            country.modifyField("Postal code format", postalCodesDictionary[country.ISO2_code])
        except:
            myLogger("for country " + country.ISO2_code + " no postal code format was found in resource " + dataCsvPath)
            country.modifyField("Postal code format", "")


def scrapeDialingInformationFromUrl(dialingInfoUrl):
    # soup = extractSoupFromUrl(dialingInfoUrl)
    html = open("../archives/Country calling codes and international dialling prefixes.html","r").read()
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find("table").findAll("tr")
    dialingInfo = {}
    for row in rows:
        cells = row.findAll("td")
        if len(cells) == 4:
            cells = list(map(lambda x: x.text, cells))
            countryName = re.sub('[\W]\(.+\)', '', cells[1])
            listOfCountryPrimaryNames = list(map(lambda x: x.primaryName, Country.listOfCountries))

            if countryName not in listOfCountryPrimaryNames:
                print(countryName)
            # dialingInfo[cells[1]] = {"Dialing prefix": cells[2], "Calling code": cells[0]}
    # return dialingInfo

def extractSoupFromUrl(url):
    # We spoof User-Agent in order not to get 403 Forbidden response
    userAgent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36"
    html = urlopen(Request(url, headers = {'User-Agent': userAgent})).read()
    soup = BeautifulSoup(html, 'html.parser')
    return soup

if __name__ == '__main__':
    logging.basicConfig(filename="sample.log", filemode="w", level=logging.INFO)
    abspath = os.path.abspath(__file__)
    os.chdir(os.path.dirname(abspath))
    webSourcesDictionary = {
        "Country names": "../archives/mapanet-eu-countries.csv",
        "Postal code format": "../archives/mapanet-eu-postal-codes-format.csv",
        ("Dialing prefix", "Calling code"): "https://www.countries-ofthe-world.com/list-of-country-calling-codes.html"
    }
    extractCountriesNameAndCode(webSourcesDictionary["Country names"])
    extractPostalCodeFormats(webSourcesDictionary["Postal code format"])
    scrapeDialingInformationFromUrl(webSourcesDictionary[("Dialing prefix", "Calling code")])

