import streamlit as st
import pandas as pd
import re
from difflib import get_close_matches
import streamlit as st
import nltk
nltk.download('wordnet')
from nltk import WordNetLemmatizer
# from spellchecker import SpellChecker

# Load the data
uom = pd.read_csv("uom.csv")
location = pd.read_csv("indianLocationList.csv", encoding="ISO-8859-1")
# prepositions = pd.read_csv("prepositions_updated.csv")['prepositions'].tolist()
prepositions = pd.read_csv("prepositionsFinal.csv")['Preposition'].tolist()
shortCodes = pd.read_csv("shortCodesProduct.csv")
procurement = pd.read_csv("PT.csv")
product_df = pd.read_csv("Updated_keywordProductSynonym2.csv", encoding = "Windows-1252")
product_df['synonymkeyword'] = product_df['synonymkeyword'].fillna('')
company_df = pd.read_csv("Copy of company_list_with_abbr.csv")
# stop_words = pd.read_csv("stop_words.csv")
stop_words = pd.read_csv("stopWordsFinal.csv")["Stop word"].tolist()

#=====================================================================================================================================

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
    for i in range(len(input_text)):
        for j in range(i+1, len(input_text)+1):
            phrase = " ".join(input_text[i:j])
            if any(location['Districts'].str.lower() == phrase.lower()):
                locations.add(phrase)
    result_dict['locations'] = locations

    procurementTerm = set()
    for word in input_text:
        if any(procurement['ProcurementTerms'].str.contains(fr"\b{word}\b", regex=True, case=False)):
            procurementTerm.add(word)
    result_dict['procurement Terms'] = procurementTerm   
    # return the dictionary of results
    return result_dict

#=====================================================================================================================================

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

#=====================================================================================================================================

def search_keywords(input_text2):
    words = input_text2.split()
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
    filtered_words = [word.lower() for word in output_text 
                  if word.lower() not in stop_words 
                  and word.lower() not in location['Districts'].str.lower().tolist()
                  and word.lower() not in procurement[0].str.lower().tolist()
                  and word.lower() not in company_df['CompanyName'].str.lower().tolist()
                  and word.lower() not in company_df['Abbrevation'].str.lower().tolist()]
    for i in range(len(filtered_words)):
        for j in range(len(shortCodes)):
            if filtered_words[i].lower() == shortCodes['ShortName'][j].lower():
                filtered_words[i] = shortCodes['Fullform'][j]
                filtered_words

    # print("filtered_words", filtered_words)
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


 #=====================================================================================================================================
# def final(input_text):

#     lemm = WordNetLemmatizer()
#     wordL = []
#     A = search_keywords(input_text)
#     not_found_words = A[1]
#     for word in not_found_words:
#         wordlemmatized = lemm.lemmatize(word)
#         wordL.append(wordlemmatized)
#     wordL = ' '.join(wordL)
#     B = search_keywords(wordL)
#     wordforCloseMatching = B[1]
#     getCloseMatch = []
#     c = get_close_matches(i, product_df['keyword'], n=2)
#     first_letter = i[0].lower()
#     matches = [match for match in c if match.lower().startswith(first_letter)]
#     getCloseMatch.append(matches)
#     for items in getCloseMatch:
#         getCloseMatch = [items for items in getCloseMatch if items is not None]
#     result = []
#     for l in getCloseMatch:
#         result += l
#     brahmastra = ' '.join(result)
#     D = search_keywords(brahmastra)
    
#     # Extract the codes from the search results
#     code_A = [(p[0], p[1]) for p in A[0]]
#     code_B = [(p[0], p[1]) for p in B[0]]
#     code_D = [(p[0], p[1]) for p in D[0]]
    
#     return (code_A, code_B, code_D)    
#=====================================================================================================================================

# def final(input_text):

#     lemm = WordNetLemmatizer()
#     # spell = SpellChecker()
#     wordL = []
#     close_matches =[]
#     A = search_keywords(input_text)
#     # print("A:==>",A)

#     not_found_words = A[1]
#     for word in not_found_words:
#         wordlemmatized = lemm.lemmatize(word)
#         wordL.append(wordlemmatized)
#     wordL = ' '.join(wordL)
#     B = search_keywords(wordL)
#     # print("B:==>",B)

#     wordforCloseMatching = B[1]
#     # print("B(1)", B[1])
#     getCloseMatch = []
#     for i in wordforCloseMatching:
#         # print(i)
#         c = get_close_matches(i, product_df['keyword'], n=2, cutoff=0.85)
#         getCloseMatch.append(c)
#         for items in getCloseMatch:
#             getCloseMatch = [items for items in getCloseMatch if items is not None]
#     # print("getCloseMatch",getCloseMatch)    
#     # getCloseMatch = ' '.join(getCloseMatch)
#     result = []
#     for l in getCloseMatch:
#         result += l
#     # print(result)
#     brahmastra = ' '.join(result)
#     # print("brahmastra", brahmastra)
#     D = search_keywords(brahmastra)
#     return A,B,D 

#=====================================================================================================================================
def final(input_text):

    lemm = WordNetLemmatizer()
    # spell = SpellChecker()
    wordL = []
    close_matches =[]
    A = search_keywords(input_text)
    # print("A:==>",A)

    not_found_words = A[1]
    for word in not_found_words:
        wordlemmatized = lemm.lemmatize(word)
        wordL.append(wordlemmatized)
    wordL = ' '.join(wordL)
    B = search_keywords(wordL)
    # print("B:==>",B)

    wordforCloseMatching = B[1]
    # print("B(1)", B[1])
    getCloseMatch = []
    for i in wordforCloseMatching:
        # print(i)
        c = get_close_matches(i, product_df['keyword'], n=2, cutoff= 0.8)
        print("c", c)
        # temp=[]
        # for i in c:
        #     if i[0].lower()==c[i][0]:
        #         temp.append(c[i])
        first_letter = i[0].lower()
        print("first_letter", first_letter)
        matches = [match for match in c if match.lower().startswith(first_letter)]
        print("matches", matches)
        # print('temp value:',temp)
        getCloseMatch.append(matches)
        for items in getCloseMatch:
            getCloseMatch = [items for items in getCloseMatch if items is not None]
    # print("getCloseMatch",getCloseMatch)    
    # getCloseMatch = ' '.join(getCloseMatch)
    result = []
    for l in getCloseMatch:
        result += l
    # print(result)
    brahmastra = ' '.join(result)
    # print("brahmastra", brahmastra)
    D = search_keywords(brahmastra)

    code_A = A[0]
    code_B = B[0]
    code_D = D[0]

    return code_A + code_B + code_D


st.title("search Segmentation")

# Get user input
input_text = st.text_input("Enter the search phrase:")

    
if st.button("Get Results"):
    # Call all three functions and display the results
    segmentation_result = textSegmentation(input_text)
    company_result = match_company(input_text)
#     product_result = search_keywords(input_text)
#     output_text = drop_prepositions(input_text)
    product_result = final(input_text)

    st.write("Units: ", segmentation_result['units'])
    st.write("Locations: ", segmentation_result['locations'])
    st.write("Procurement Terms: ", segmentation_result['procurement Terms'])
    st.write("Company Name Matches: ", company_result)
    st.write("Product Name Matches: ", product_result)
