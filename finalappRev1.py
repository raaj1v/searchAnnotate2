import streamlit as st
import pandas as pd
import re
import nltk
nltk.download('wordnet')
from nltk import WordNetLemmatizer
from difflib import get_close_matches
import streamlit as st
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

#=====================================================================================================================================

def match_company(input_text):
    input_words = re.findall(r'[a-zA-Z,]+', input_text)
    # initialize variables
    companyDict = {}
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
    companyDict['company_matches'] = keyword_matches
    # return keycodeids and corresponding phrases
    return companyDict

#=====================================================================================================================================
def search_keywords(input_text2):
    words = input_text2.split()
    cleaned_words = []
    for i in range(len(words)):
        if words[i].lower() in prepositions:
            break
        cleaned_words.append(words[i])
    output_text = ' '.join(cleaned_words)
    # print("output_text", output_text)
    # remove unwanted characters
    output_text = output_text.replace(",", " BRK").replace(".", " BRK")
    output_text = re.findall(r'[a-zA-Z]+', output_text)
    # remove stop words
    filtered_words = [word for word in output_text 
                  if word.lower() not in stop_words 
                  and word.lower() not in location['Districts'].str.lower().tolist()
                  and word.lower() not in procurement['ProcurementTerms'].str.lower().tolist()
                  and word.lower() not in company_df['CompanyName'].str.lower().tolist()
                  and word.lower() not in company_df['Abbrevation'].str.lower().tolist()]
    # print("filtered_words", filtered_words)

    for i in range(len(filtered_words)):
        for j in range(len(shortCodes)):
            if filtered_words[i].lower() == shortCodes['ShortName'][j].lower():
                filtered_words[i] = shortCodes['Fullform'][j]
                filtered_words
                
    # initialize variables
    ExtractedMatches = {}
    keyword_matches = []
    product_matches = []
    synonym_matches = []
    remaining_words = filtered_words
    wordNotFound=[]
    # search for longest possible matching word strings in keyword column
    while len(remaining_words) > 0:
        for i in range(len(remaining_words), 0, -1):
            phrase = ' '.join(remaining_words[:i])
            matches = product_df[product_df['ProductName'].str.lower() == phrase.lower()]
            if len(matches) > 0:
                product_matches.append((matches.iloc[0]['ProductCode'], phrase))
                ExtractedMatches['product_matches'] = product_matches
                remaining_words = remaining_words[i:]
                break
        else:
            # no match found in keyword column, try synonym column
            for i in range(len(remaining_words), 0, -1):
                phrase = ' '.join(remaining_words[:i])
                matches = product_df[product_df['keyword'].str.lower()==phrase.lower()]
                if len(matches) > 0:
                    keyword_matches.append((matches.iloc[0]['keycodeid'], phrase))
                    ExtractedMatches['keyword_matches'] = keyword_matches
                    remaining_words = remaining_words[i:]
                    break
            else:
                # no match found in synonym column, try productname column
                for i in range(len(remaining_words), 0, -1):
                    phrase = ' '.join(remaining_words[:i])
                    matches = product_df[product_df['synonymkeyword'].str.lower()==phrase.lower()]
                    if len(matches) > 0:
                        synonym_matches.append((matches.iloc[0]['synonymId'], phrase))
                        ExtractedMatches['synonym_matches'] = synonym_matches
                        remaining_words = remaining_words[i:]
                        break
                else:
                    # no match found in any column
                    wordNotFound.append(remaining_words.pop(0))
    # return keycodeids and corresponding phrases
    return ExtractedMatches, wordNotFound


 #=====================================================================================================================================
def final(input_text):

    Comp= match_company(input_text)
    textSegments = textSegmentation(input_text)

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
        c = get_close_matches(i, product_df['keyword'], n=2, cutoff=0.)
        temp=[]
        for j in c:
            if j[0].lower()==i[0].lower():
                temp.append(j)
        print('temp value:',temp)
        getCloseMatch.append(temp)
        for index in getCloseMatch:
            getCloseMatch = [index for index in getCloseMatch if index is not None]
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

    return code_A, code_B, code_D , Comp, textSegments
#=====================================================================================================================================
material=['SDBC','Asphalt','Bitumen','Bituminous','Block','Brick','CC','Cement','Concrete','Concrete Cement','Gravel','Macadam','Paver','PCC','Plain Concrete Cement',
          'Prestressed concrete','RCC','Reinforced Cement Concrete','Reinforced concrete','Tile','Water Bound Macadam','WBM','bt','LED','Metal']

Product=['Tack','Coat','marking','Strips','Alley','Approach','Asphalting Work','Bituminous Work','Boardwalk','Carriageway','Crossroad','Divider','Driveway','Expressway','Footpath',
         'Footway','Freeway','Grade Separated Junction','Grade Separated Structure','Grade Separator','Highway','Intersection','Lane','Main Road',
         'Marg','Motorway','Passage','Passageway','Path','Pathwalk','Pathway','Pavement','Promenade','Rasta','Ring Road','Road','Roadway','Roadwork',
         'Roundabout','Sadak','Sidewalk','Slip Road','Street','Surface Work','Surfacing Work','Track','Traffic Island','Trunk Road','Walkway']

PT=['Work','Design','Purchase','Providing','Supply','Installation','Testing','Commissioning','Engineering','Procurement','Construction',
'EPC','Reconstruction','Development','Redevelopment','Rehabilitation','Renovation','Restoration','Implementation','Refurbishment','Establishment','Maintenance','Repair','Upgradation','Upgrading',
'Execution','Erection','Widening','Strengthening','Resurfacing','Improvement','Renewal','Carpeting','Concreting','Formation','Laying','Paving',
'Rectification','Expansion','Extension','Operation','Recarpeting','Rejuvenation','Surfacing','Joint filling','Setting up','Resetting','Boring',
'Fixing','Alteration','Outsourcing','Realignment','Hiring','Hire','Leasing','Lease','Rental','Rent','Renting','Appointment','Sale','Sell','Replacement','Import','Export',
'Annual Maintenance Contract','AMC','Arrangement','Fabrication','Manufacturing','Inspection','Packing','Delivery','Excavation','Extraction','Rate Contract','Modification','Shifting',
'Rewinding','Revamping','Allotment','Preparation','Provision','Painting','Landscaping','Beautification','Transportation','Loading','Unloading','Stacking',
'Laning','Overhauling','Auction','Augmentation','Addition','Engaging','Fencing','Servicing','Drawing','Reconditioning','Licensing','Collection','Disposal',
'Empanelment','Selection','Deployment','Refilling','Assembling','Facility','Remaining','Carpainting','maintance']

genericWords=['Old','Damage','Complete','Absence','lack', 'unavailability','Academic','Borrow','Boundary','overseas','Incorporate',
             'include','defend','Margin','area', 'locality','undertake','thick','other','annual','Schem','Connecting','Miscellaneous',
             'old','25mm','damage']
#=====================================================================================================================================

toLowerMaterial=[x.lower() for x in material]
toLowerProduct=[x.lower() for x in Product]
toLowerPTCase=[x.lower() for x in PT]
toLowergeneric=[x.lower() for x in genericWords]

#=====================================================================================================================================
proposition=['Abroad','About','Above','According to','Across','After','Against','Ago','Ahead of','Along','Amidst','Among','Apart','Around','As','As far as','As well as','Aside',
'At','Away','Barring','Because of','Before','Behind','Below','Beneath','Beside','Besides','Between','Beyond','But','By','By means of','Crica','Concerning',
'Despite','Down', 'Due to','During','In','In accordance with','In addition to','In case of','In front of','In lieu of','In place of','In spite of',
'In to','Inside','Instead of','Into','Except','Except for','Excluding','For','Following','From','Hence','Like','Minus','Near',
'Next','Next to','Past','Per','Prior to','Round','Off','On','On account of','On behalf of','On to','On top of','Onto','Opposite',
'Out','Out from','Out of','Outside','Over','Owing to','Than','Through','Throughout','Till','Times','To','Toward','Towards',
'Under','Underneath','Unlike','Until','Unto','Up','Upon','Via','With','Within','Reparing']

toLowerCasePropo=[x.lower() for x in proposition]

recheck=['Abroad','About','Above','According to','Across','After','Against','Ago','Ahead of','Amidst','Among','Apart','Around','As','As far as',
'At','Away','Barring','Because of','Before','Behind','Below','Beneath','Beside','Besides','Between','Beyond','But', 'By', 'Crica','Concerning',
'Despite','Down', 'Due to','During','In','In accordance with','In addition to','In case of','In front of','In lieu of','In place of','In spite of',
'In to','Inside','Instead of','Into','Except','Except for','Excluding','Following','From','Hence','Like','Minus','Near',
'Next','Next to','Past','Per','Prior to','Round','Off','On','On account of','On behalf of','On to','On top of','Onto','Opposite',
'Out','Out from','Out of','Outside','Over','Owing to','Than','Through','Throughout','Till','Times','To','Toward','Towards',
'Under','Underneath','Unlike','Until','Unto','Up','Upon','Via','Within','Reparing']

toLowerCasePropoUpdate=[x.lower() for x in recheck]

import nltk
import re
from nltk.stem import WordNetLemmatizer
lemm = WordNetLemmatizer()
def split_Text_Index(sentence):
    sentence.split('.')
    res=sentence.lower()
    res = sentence.split()

    # print('after split:',res)
    temp=[]
    index=[]
    cleanSentence=[]
    for pos,sen in enumerate(res):
        sen=sen.lower()
        # print('convert into the lower():',sen)
        if pos == 0:
            temp.append(pos)
        if sen in toLowerCasePropo:
            temp.append(pos)
        else:
            cleanSentence.append(sen)
    return temp



##=====================================================================================================================================
def chunksData(text,index):
    # print('F sentence:',text,'index:',index)
    extractedData=[]
    for i,j in zip([text],[index]):
        # print('Type:',type(i))
        # print('F i:',i,'F index:',j)
        getData=[]
        splitData=i.split()
        splitData = [lemm.lemmatize(word) for word in splitData]
        # print("lemmatizedWords:",splitData)
        # print('Sep:',splitData)
        for ind,word in enumerate(j):
            try:
                # print('index:',j[ind],'word is :',j[ind+1])
                # print('Extracted:',splitData[j[ind]:j[ind+1]])
                # print("Final Strings:",' '.join(splitData[j[ind]:j[ind+1]]))
                data=' '.join(splitData[j[ind]:j[ind+1]])
                getData.append(data)
#                     return extractedData
            except:
                # print('inside the except part')
                # print(' '.join(splitData[j[ind]:]))
                data=' '.join(splitData[j[ind]:])
                getData.append(data)
                # print('-------------------------')
#                     return extractedData
        extractedData.append(getData)
    return extractedData

#=====================================================================================================================================

def perfectChunks(listData):
    finalChunks = []
    location=[]
    listData=listData.split()
    print('listData:',listData)
    firstCheck = listData[0].lower()
    pattern = '(^:)'
    secondCheck = re.match(pattern, listData[0])
    if firstCheck not in toLowerCasePropoUpdate or secondCheck:
        ff = ' '.join(listData)
        print( 'ff:',ff)
        finalChunks.append(ff)
    else:
        bb = ' '.join(listData)
        print( 'bb:',bb)
        location.append(bb)
#     for data in listData:
#         print('data:',data)
#         pattern = '(^:)'
#         firstCheck = data[0].lower()
#         print('First Data:',firstCheck)
#         secondCheck = re.match(pattern, data)
#         if firstCheck in toLowerCasePropoUpdate or secondCheck:
#             ff = ' '.join(listData)
#             print( 'ff:',ff)
#         finalChunks.append(ff)
    
    return finalChunks, location
#=====================================================================================================================================
def newFunModify(s):
    print('Sentence :',s)
    s=s.lower()
    checking=s.split(' ')
    print('Checking Data:',checking)
    junk=[]
    Product=[]
    finalProduct=[]
    temp=[]
    if checking[-1] in toLowerPTCase:
        print('inside the last word is PT')
        tempData=checking[:-1]
        print('TempData:',tempData)
        combined=' '.join(tempData)
        print('After Removing the PT:',combined)
        mergedData=''
        if any(check in combined.lower() for check in toLowergeneric) :
            print('Combined Data:',combined)
            combined=combined.split(' ')
            for word in combined:
                print('Word:',word)
                word=word.lower()
                if word in toLowergeneric:
                    print('inside the generic Word:',word)
                    junk.append(word)
                elif word in toLowerPTCase:
                    print('inside the PT Word:',word)
                    junk.append(word)
                else:
                    print('last word:',checking[-1])
                    Product.append(word)
                    mergedData=word +' '+checking[-1]
                combined=' '.join(mergedData)
            finalProduct.append(mergedData)
        else:
            finalProduct.append(combined) 
    
    elif s.startswith("of "):
        print('Inside Starts with of :')
        s=s.replace('of','')
        if any(check in s.lower() for check in toLowergeneric):
            print('something is generic inside the sentence:')
            newSentence=s.split(' ')
            for word in newSentence:
                print('Word:',word)
                word=word.lower()
                if word in toLowergeneric:
                    print('inside the generic Word:',word)
                    junk.append(word)
                elif word in toLowerPTCase:
                    print('inside the PT Word:',word)
                    junk.append(word)
                else:
                    Product.append(word)
                combined=' '.join(Product)
            finalProduct.append(combined)    
        else:
            finalProduct.append(s)
    elif 'of' in s:
        sentence=s.split(' of ')
        print('After break:',sentence)
        for splitData in sentence:
            print('set_env:',splitData)
            splitData=splitData.lower()
            if any(check in splitData.lower() for check in toLowergeneric) :
                print('generic or Procurment Term inside the sentence:')
                newSentence=splitData.split(' ')
                print('New Sentence:',newSentence)
                for word in newSentence:
                    print('Word:',word)
                    word=word.lower()
                    if word in toLowergeneric:
                        print('inside the generic Word:',word)
                        junk.append(word)
                    elif word in toLowerPTCase:
                        print('inside the PT Word:',word)
                        junk.append(word)
                    else:
                        print('inside the product:',word)
                        Product.append(word)
                    combined=' '.join(Product)
                finalProduct.append(combined)    
            else:
                combined=''
                newSentence=splitData.split(' ')
                print('sen:',newSentence)
                print('First Word:',newSentence[0])
                if any(check in newSentence[0] for check in toLowerPTCase) :
                    print('PT in Sen')
                    for i in newSentence:
                        print('inside the PT Word:',i)
                        junk.append(i)
                else:
                    combined=' '.join(newSentence)
            finalProduct.append(combined)
    
    elif '&' in s:
        sentence=s.split('&')
        print('After  end break:',sentence)
        for splitData in sentence:
            print('set_env:',splitData)
            if any(check in splitData.lower() for check in toLowergeneric):
                print('generic inside the sentence:')
                newSentence=splitData.split(' ')
                print('New Sentence:',newSentence)
                for word in newSentence:
                    print('Word:',word)
                    word=word.lower()
                    if word in toLowergeneric:
                        print('inside the generic Word:',word)
                        junk.append(word)
                    elif word in toLowerPTCase:
                        print('inside the PT Word:',word)
                        junk.append(word)
                    else:
                        print('inside the product:',word)
                        Product.append(word)
                    combined=' '.join(Product)
                finalProduct.append(combined)    
            else:
                finalProduct.append(splitData)
    else:
        print('Inside totally else part:')
        if any(check in s.lower() for check in toLowergeneric):
            print('something is generic inside the sentence:')
            newSentence=s.split(' ')
            for word in newSentence:
                print('Word:',word)
                word=word.lower()
                if word in toLowergeneric:
                    print('inside the generic Word:',word)
                    junk.append(word)
                elif word in toLowerPTCase:
                    print('inside the PT Word:',word)
                    junk.append(word)
                else:                    
                    Product.append(word)
                combined=' '.join(Product)
            finalProduct.append(combined)    
        else:
            finalProduct.append(s)
    return finalProduct        
    # print('junk:',junk,'Product:',Product,'final Product:',finalProduct)
#=====================================================================================================================================
def splitFunction(userInput):
    appendedResult = []
    result = re.split(r'\.(?![^\(\)]*\))', userInput)
    # print('result:', result)
    for i in result:
        # print('i:', i)
        result = split_Text_Index(i)
        # print('result:', result)
        chunk = chunksData(i, result)
        for j in chunk:
            # print('Value of J:',j)
            for k in j:
                # print('Value of K:',k)
                spiltData = perfectChunks(str(k))
                # print('spiltData:->',spiltData)
                for m in spiltData[0]:
                    # print('finding the Product inside the Chunks:',m)
                    ram=newFunModify(m)
                    # print('Suggestion:',ram)
                    appendedResult.append(ram)
    return appendedResult, spiltData[1]
#=====================================================================================================================================

def mainFunction(userInput):
    Resultset = []
    F= splitFunction(userInput)
    for i in F[0]:
        Q = ' '.join(i)
        test  = final(Q)
        Resultset.append(test)
    return Resultset
#=====================================================================================================================================


# def mainFunction(userInput):
#     result=split_Text_Index(userInput)
#     # print('Divided data index:',result)
#     chunk=chunksData(userInput,result)
#     appendedResult=[]
#     # print('Final Data:',chunk)
#     for i in chunk:
#         spiltData=perfectChunks(str(i))
#         # print('spiltData:',spiltData)
#         for d in spiltData:
#             # print('Final Data:',d)
#             FullFinal=final(d)
#             appendedResult.append(FullFinal)
#     return appendedResult
#             # print('FullFinal:',FullFinal)
        




#=====================================================================================================================================

# st.title("TIGER AI")

# # Get user input
# input_text = st.text_input("Enter the search phrase:")

    
# if st.button("Get Results"):
#     # Call all three functions and display the results
#     segmentation_result = textSegmentation(input_text)
#     company_result = match_company(input_text)
# #     product_result = search_keywords(input_text)
# #     output_text = drop_prepositions(input_text)
#     product_result = final(input_text)

#     st.write("Units: ", segmentation_result['units'])
#     st.write("Locations: ", segmentation_result['locations'])
#     st.write("Procurement Terms: ", segmentation_result['procurement Terms'])
#     st.write("Company Name Matches: ", company_result)
#     st.write("Product Name Matches: ", product_result)
