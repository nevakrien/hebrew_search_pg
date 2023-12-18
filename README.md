# hebrew_search_pg
using pgvector to have knn search over a medium-large dataset

you will need to install both postgress and pgvector.


# notes
most systems have the postgres username as postgres if it is diffrent in your system replace it (including the install and uninstall files).
# setup

starting postgress 

'''bash
pg_ctl start
'''

making the db
'''bash 
createdb -h localhost -U postgres hebrew_document_search
'''

'''bash 
python setup.py
'''

## setting with deafualts

if you want to test the original dataset use:
'''bash 
python db_document.py
'''

for basic indexing use 
'''bash 
python snippets.py
'''

## calculating embeddings
using this command:
'''bash 
python embeddings.py
'''
would fill up all the missing embeddings
on my machine the calculation took around 3 hours for the full dataset
u can pass in a cup parameter into the embedding function. to get a small subset to test on (edit the main function) 

## testing 
to compare knn results from postgres to knn result gathered by numpy u can use

'''bash 
python testing.py
'''

# uninstall 
droping the db
'''bash 
dropdb -h localhost -U postgres hebrew_document_search
'''
