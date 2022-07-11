import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from tabulate import tabulate
from urllib.parse import unquote
from urllib.parse import urljoin
from tqdm import tqdm

MAX_CHAR_AUTH = 25 # Maximum characters displayed for the author. Change according to N_AUTHORS.
MAX_CHAR_TITLE = 50 # Maximum characters displayed for the book title
MAX_CHAR_PUB = 20 # Maximum characters displayed for the publisher.

base = 'https://gen.lib.rus.ec/search.php?&'
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}


def searchBooks(search_term, column, page):
    '''
    This function makes the request to libgen with the needed
    parameters like the search term, column(author, title,
    extension etc) and page of the search query. 

    Parameters:
    search_term(str): The search term for the libgen query
    column(str): The column in which to search for, like author or extension etc.
    page(int): The page of the query

    Returns: 
    books(bs4.element.Tag): The table of the query containing the books
    numberofbooks(int): The number of files in the search(only returned if the page is 1)
    '''
    parameters = urlencode({'req':search_term, 'column':column, 'page':page})
    url = base + parameters
    r = requests.get(url, headers=headers)
    s = BeautifulSoup(r.text, 'lxml')
    #numberofbooks = None
    if page == 1:
        numberofbooks = s.find('font', {'color': 'grey', 'size': '1'}).text.split(' ')[0]
        print(f'{numberofbooks} books found')
    print(f'Now displaying page {page}')
    table = s.find('table', {'class':'c'})
    books = table.find_all('tr')
    books = books[1:]
    if page == 1:
        return(books, numberofbooks)
    else:
        return(books)


def parseBooks(books):
    '''
    This function parses the book table obtained from the searchBooks
    method. It obtains book metadata like the identification number, 
    title, author, language, file type of the book, MD5 hash and the
    download mirrors of the book.

    Parameters:
    books(bs4.element.Tag): The table containing books 

    Returns: 
    table(list): The search results to be printed in the terminal
    download_mirror(list): A list containing dictionaries of the MD5 hash and the download mirrors of each book
    '''
    table = []
    download_Mirrors = []
    for i in books:
        attributes = i.find_all('td')
        identifier = attributes[0].text
        author = attributes[1].text.split(',')[0]
        author = author[:MAX_CHAR_AUTH]
        title = attributes[2].text
        smol_title = title[:MAX_CHAR_TITLE]
        publisher = attributes[3].text[:MAX_CHAR_PUB]
        year = attributes[4].text
        lang = attributes[6].text
        extension = attributes[8].text
        # Handle the mirrors
        mirror_list = {}  
        for j in range(9, 13):
            mirror = j - 8  # So that the mirror list selection choices can start from 1
            mirror_list[mirror] = attributes[j].a.attrs['href']
        # Handle the MD5 hash
        md5 = ''
        for j in attributes[2].find_all('a'):
            if j.get('href').startswith('book/index.php?md5='):
                md5 = j.get('href').partition('book/index.php?md5=')[2]
        book = (identifier, author, smol_title, publisher, year, lang, extension)   # Results that will be printed in the terminal
        book_download = {
            'ID':identifier, 
            'Title': title, 
            'File type': extension,
            'Mirrors': mirror_list, 
            'MD5': md5
        }   # Book metadata and mirror list for downloading the book
        table.append(book)
        download_Mirrors.append(book_download)
    return(table, download_Mirrors)


def pickBook(page, table, numberofbooks, mirrors):
    '''
    Pretty print the search results in the terminal, 
    and browse the search results. The user makes their
    choice by typing the ID of the book they want.

    Parameters: 
    page(int): The page of the search result
    table(list): The list of the books to be pretty printed in the terminal
    numberofbooks(int): The total number of books in the search result
    mirrors(list): A list containing dictionaries of the MD5 hash and the download mirrors of each book
    '''
    headers = ['ID', 'Author', 'Title', 'Publisher', 'Year', 'Language', 'Extension']
    print(tabulate(table[(page - 1) * 25:page * 25], headers))
    if numberofbooks == len(table):
        print(f'\n\nYou have reached the end of the list')
    while True:
        if numberofbooks == len(table):
            action = input('\nType the ID of the book you want to download or press q to quit: ')
        else:
            action = input('\nType the ID of the book you want to download, enter to see more results, or press q to quit: ')
        
        if action.isnumeric():
            for i in mirrors:
                if action in i['ID']:
                    for key, value in i.items():
                        print(f'{key}: {value}')
                    while True:
                        choice = input('Is this the book you are looking for?(yes/no) ').lower()
                        if choice == 'yes':
                            getBook(i);return False
                        elif choice == 'no':
                            break
                        else:
                            print('Please type yes or no.')
        elif action == 'q' or action == 'Q':  # Quit
            print('Exiting...')
            return(False)
        
        elif not action:
            if numberofbooks == len(table):
                print('Not a valid option')
                continue
            else:
                return(True)


def getBook(mirrors):
    '''
    This functions presents a choice of the availalble
    mirrors to the user. The user can make a numeric 
    choice to select a mirror, and the needed functions
    for the selected mirrors will be called. 

    Parameters: 
    mirrors(dict):  
    '''
    print(f'=====\nThis book can be downloaded from these mirrors:')
    m = mirrors['Mirrors']
    for key, value in m.items():
        print(f'{key}: {value}')
    mirror = int(input('What mirror do you want to choose? '))
    if mirror == 1:
        mirror1(m[mirror])
    elif mirror == 2:
        mirror2(m[mirror], mirrors['File type'])

def mirror1(mirror):
    '''
    A function to interface with the first mirror, 
    http://library.lol/. The title to save the book is 
    obtained by decoding the download url of the book.

    Parameters:
    mirror(str): This is the url of the page which contains the download url of the book. 
    '''
    r = requests.get(mirror)
    s = BeautifulSoup(r.text, 'html.parser')
    download_url = s.find('td', {'id':'info'}).find('h2').find('a').get('href')
    title = unquote(download_url)
    idx = title.rfind('/')
    title = title[idx+1:]
    download(download_url, title)

def mirror2(mirror, filetype):
    '''
    A function to interface with the second mirror, 
    https://libgen.rocks/ aka https://cdn1.booksdl.org/. 
    The title to save the book is obtained by scraping the 
    author and title, and then joining the 2 together along
    with the filetype.

    Parameters:
    mirror(str): This is the url of the page which contains the download url of the book.
    filetype(str): Unlike the first mirror, which has the filetype in the mirror in the url, the filetype is a parameter so the title can contain a filetype to save the book.
    '''
    domain = mirror[:mirror.rfind('/')]
    r = requests.get(mirror)
    s = BeautifulSoup(r.text, 'html.parser')
    download_url = s.find('td', {'align':'center'}).find('a').get('href')
    download_url = urljoin(domain, download_url)
    d = str(s.find_all('td')[7])
    title = d[11:d.find("<br/>")]+f'.{filetype}'
    author = d[d.find('Author(s): '):];author = author[11:author.find('<br/>')]
    title = author + ' - ' + title
    download(download_url, title)


def download(url, title):
    '''
    A function that when given a download url and
    book title, downloads the book. 

    Parameters:
    url(str): The URL which points to the book that can be downloaded
    title(str): The title of the book, which will also be the filename
    '''
    r = requests.get(url, stream=True)
    total_size= int(r.headers.get('content-length', 0))
    block = 1024 #1 Kibibyte
    print(f'=====\nDownloading {title}')
    progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
    with open(title, 'wb') as file:
        for data in r.iter_content(block):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    if total_size != 0 and progress_bar.n != total_size:
        print("ERROR, something went wrong")

if __name__ == '__main__':
    books = []
    mirrors = []
    search_term = input('What do you want to search for? ')
    page = 1
    sel_column = 'def'
    '''for arg in search_arguments:
        if arg[0]:
            sel_column = arg[1]'''
    get_next_page = True
    while get_next_page:
        if page == 1:
            raw_books, numberofbooks = searchBooks(search_term, sel_column, page)
        else:
            raw_books = searchBooks(search_term, sel_column, page)

        if raw_books:
            new_books, new_mirrors = parseBooks(raw_books)
            books += new_books
            mirrors += new_mirrors
            get_next_page = pickBook(page, books, numberofbooks, mirrors)
            page += 1
        else:  # 0 matches total
            get_next_page = False