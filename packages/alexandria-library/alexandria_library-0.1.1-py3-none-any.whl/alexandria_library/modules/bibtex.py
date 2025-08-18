
# pip install scholarly

from scholarly import scholarly

def get_bibtex_from_scholar(title):
    search = scholarly.search_pubs(title)
    try:
        first_result = next(search)
        bibtex = scholarly.bibtex(first_result)
        return bibtex
    except StopIteration:
        return None

if __name__ == "__main__":
    bibtex = get_bibtex_from_scholar("Introduction to Logic - Routledge 2016")
    print(bibtex)
