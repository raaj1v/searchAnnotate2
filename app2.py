# import streamlit as st
import pandas as pd
import re
from nltk import WordNetLemmatizer
from difflib import get_close_matches
from spellchecker import SpellChecker

# Load the data
uom = pd.read_csv("uom.csv")
location = pd.read_csv("indianLocationList.csv", encoding="ISO-8859-1")
# prepositions = pd.read_csv("prepositions_updated.csv")['prepositions'].tolist()
prepositions = pd.read_csv("Place_preposition_Product.csv")['Preposition'].tolist()
shortCodes = pd.read_csv("shortCodesProduct.csv")
procurement = pd.read_csv("procurementTerms.csv")
product_df = pd.read_csv("Updated_keywordProductSynonym2.csv", encoding = "Windows-1252")
product_df['synonymkeyword'] = product_df['synonymkeyword'].fillna('')
company_df = pd.read_csv("Copy of company_list_with_abbr.csv")
stop_words = pd.read_csv("stop_words.csv")



input_text = "roads diesel diesel generator set bridge bridges road "


def textSegmentation(input_text):
    input_text = re.findall(r'[a-zA-Z]+', input_text)
    result_dict={}
    units = set()
    for word in input_text:
        if any(uom['units'].str.contains(fr"\b{word}\b", case=False, regex=True)):
            units.add(word)
    result_dict['units'] = units
    
    # extract locations from the cleaned text
    locations = set()
    for word in input_text:
        if any(location['Districts'].str.contains(fr"\b{word}\b", regex= True,case=False)):
            locations.add(word)
    result_dict['locations'] = locations

    procurementTerm = set()
    for word in input_text:
        if any(procurement['ProcurementTerms'].str.contains(fr"\b{word}\b", regex=True, case=False)):
            procurementTerm.add(word)
    result_dict['procurement Terms'] = procurementTerm   
    # return the dictionary of results
    return result_dict




def match_company(input_text):
    input_words = re.findall(r'[a-zA-Z,]+', input_text)
    # initialize variables
    keyword_matches = []
    remaining_words = input_words
    # search for longest possible matching word strings in keyword column
    while len(remaining_words) > 0:
        for i in range(len(remaining_words), 0, -1):
            phrase = ' '.join(remaining_words[:i])
            matches = company_df[company_df['Abbrevation'].str.lower() == phrase.lower()]
            if len(matches) > 0:
                keyword_matches.append((matches.iloc[0]['companyrecno'], phrase))
                remaining_words = remaining_words[i:]
                break
        else:
            for i in range(len(remaining_words), 0, -1):
                phrase = ' '.join(remaining_words[:i])
                matches = company_df[company_df['CompanyName'].str.lower() == phrase.lower()]
                if len(matches) > 0:
                    keyword_matches.append((matches.iloc[0]['companyrecno'], phrase))
                    remaining_words = remaining_words[i:]
                    break
            else:
                # no match found in any column
                remaining_words.pop(0)
    # return keycodeids and corresponding phrases
    return keyword_matches

def search_keywords(input_text):
    words = input_text.split()
    cleaned_words = []
    for i in range(len(words)):
        if words[i].lower() in prepositions:
            break
        cleaned_words.append(words[i])
    output_text = ' '.join(cleaned_words)
    # remove unwanted characters
    output_text = output_text.replace(",", " BRK").replace(".", " BRK")
    output_text = re.findall(r'[a-zA-Z]+', output_text)
    # remove stop words
    filtered_words = [word for word in output_text if word.lower() not in stop_words]
    # initialize variables
    keyword_matches = []
    remaining_words = filtered_words
    wordNotFound=[]
    # search for longest possible matching word strings in keyword column
    while len(remaining_words) > 0:
        for i in range(len(remaining_words), 0, -1):
            phrase = ' '.join(remaining_words[:i])
            matches = product_df[product_df['keyword'].str.lower() == phrase.lower()]
            if len(matches) > 0:
                keyword_matches.append((matches.iloc[0]['keycodeid'], phrase))
                remaining_words = remaining_words[i:]
                break
        else:
            # no match found in keyword column, try synonym column
            for i in range(len(remaining_words), 0, -1):
                phrase = ' '.join(remaining_words[:i])
                matches = product_df[product_df['synonymkeyword'].str.lower()==phrase.lower()]
                if len(matches) > 0:
                    keyword_matches.append((matches.iloc[0]['synonymId'], phrase))
                    remaining_words = remaining_words[i:]
                    break
            else:
                # no match found in synonym column, try productname column
                for i in range(len(remaining_words), 0, -1):
                    phrase = ' '.join(remaining_words[:i])
                    matches = product_df[product_df['ProductName'].str.lower()==phrase.lower()]
                    if len(matches) > 0:
                        keyword_matches.append((matches.iloc[0]['ProductCode'], phrase))
                        remaining_words = remaining_words[i:]
                        break
                else:
                    # no match found in any column
                    wordNotFound.append(remaining_words.pop(0))
    # return keycodeids and corresponding phrases
    return keyword_matches, wordNotFound

result=search_keywords(input_text)





# d=result[1]





# Streamlit UI






# st.title("TIGER AI")

# # Get user input
# input_text = st.text_input("Enter the search phrase:")

    
# if st.button("Get Results"):
#     # Call all three functions and display the results
#     segmentation_result = textSegmentation(input_text)
#     company_result = match_company(input_text)
# #     product_result = search_keywords(input_text)
# #     output_text = drop_prepositions(input_text)
#     product_result = search_keywords(input_text)

#     st.write("Units: ", segmentation_result['units'])
#     st.write("Locations: ", segmentation_result['locations'])
#     st.write("Procurement Terms: ", segmentation_result['procurement Terms'])
#     st.write("Company Name Matches: ", company_result)
#     st.write("Product Name Matches: ", product_result)

