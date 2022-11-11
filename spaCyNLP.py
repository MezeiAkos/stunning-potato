import spacy
import pymongo
from spacy import displacy
# TODO make a pipeline, run this only when there are more than x unprocessed listings
password = input("Password: ")
myclient = pymongo.MongoClient(f"mongodb+srv://Admin:{password}"
                               f"@jobanalyzer.vydrnyx.mongodb.net/?retryWrites=true&w=majority")
mydb = myclient["jobAnalyzer"]

print(mydb.list_collection_names())
collection_name = input("Collection name: ")
mycol = mydb[collection_name]  # TODO error handle it

list_of_descriptions_and_id = []

for col in mycol.find():
    if col["is_processed"] is False:  # if a listing is already processed, don't process it again
        list_of_descriptions_and_id.append([col["description_raw"], col["_id"]])
# TODO check if a listing is processed with a given keyword, if not, process it again

spacy.prefer_gpu()  # this should run spacy on the gpu, but I don't think it works, or it works with 0% GPU utilization
nlp_en = spacy.load("en_core_web_sm")
nlp_ro = spacy.load("ro_core_news_sm")
doc_example = nlp_en("Excellent knowledge of Python and Django REST; ")  # just a testing example
list_of_tokens = []
list_of_tokens_string = []
i = 1  # variable for progress
length = len(list_of_descriptions_and_id)

keywords = input("Input keywords to search for separated by a space: ")
keywords = keywords.split()

for text in list_of_descriptions_and_id:
    doc = nlp_en(text[0])
    #  TODO get experience required for given language, not just the language
    for token in doc:
        if token.lower_ in keywords:
            if token.pos_ == "PROPN":  # PROPN = proper noun
                list_of_tokens.append(token)
    for token in list_of_tokens:  # TODO no need to use two fors, merge them into one
        list_of_tokens_string.append(token.text.lower())
    list_of_tokens_string = list(dict.fromkeys(list_of_tokens_string))  # getting rid of duplicates
    mycol.update_one({"_id": text[1]}, {"$set": {"keywords": list_of_tokens_string}})
    if len(list_of_tokens_string) > 0:  # only set processed status to true if there was at least one keyword found
        mycol.update_one({"_id": text[1]}, {"$set": {"is_processed": True}})

    percent = (i * 100) / length
    print(f"{i}/{length} done, {percent:.2f}% done")  # TODO maybe add a time estimate too
    i += 1
    list_of_tokens.clear()
    list_of_tokens_string.clear()

# TODO https://www.ejobs.ro/user/locuri-de-munca/data-scientist/1585369 it doesn't find keywords in this, refine the NLP
