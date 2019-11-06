from HW import getBookList, getBooksData
# import HW1
url = 'https://www.books.com.tw/web/books_nbtopm_19/?loc=P_0001_019'
bookList = getBookList(url)
print(bookList)
booksData = getBooksData()
print(booksData)