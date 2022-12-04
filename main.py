import typer
from rich.console import Console
from rich.table import Table
from typing import Optional
from create_table import create_tables
import psycopg2
import json

console = Console()

app = typer.Typer()

conn = psycopg2.connect(
	host="localhost",
	database="library",
	user="postgres",
	password="postgres")
	

@app.command("start")
def start():
	typer.secho(f'''Welcome to Library CLI!\n\n
		You can execute command '--help' to see the possible commands''', fg=typer.colors.GREEN)
	# TODO: connect to database
	create_tables()
	with open('books.json', 'r') as f:
		books = json.load(f)
	for i in books:
		cur = conn.cursor()
		title = i['title']
		author = i ["authors"][0]
		pages = i['pageCount']
		genre = i["categories"][0]
		quantity= 1
		postgres_select_query = f"""select quantity from books where title = '{title}' and author = '{author}' """
		cur.execute(postgres_select_query)
		q1 = cur.fetchone()
		if q1 is None:
			postgres_insert_query = f""" INSERT INTO books (title,author,genre,pages,quantity) VALUES ('{title}','{author}','{genre}','{pages}','{quantity}')"""
			cur.execute(postgres_insert_query)
			cur.close()
			conn.commit()

# This is how you can get arguments, here username is a mandatory argument for this command.
@app.command("sign_up")
def sign_up(username: str):
	typer.echo(f"Nice that you are signing up!")
	# TODO: Add user with name {username} to database table
	cur = conn.cursor()
	postgres_insert_query = f""" INSERT INTO users (user_name) VALUES ('{username}')"""
	cur.execute(postgres_insert_query)
	cur.close()
	conn.commit()

 
@app.command("search_by_author")
def search_by_author(author):
	cur = conn.cursor()
	postgres_select_query = f"""select ROW_NUMBER () OVER (ORDER BY book_id) as "#",
 							book_id as "Book ID", title as "Name", author as "Author", pages as "# Pages",
							genre as "Genre",  quantity > 0 as "Availability" from books where  author LIKE '{author}%' """
	cur.execute(postgres_select_query)
	display_table(cur)
	cur.close()
	conn.commit()
 
@app.command("most_read_genres")
def smost_read_genres():
	cur = conn.cursor()
	postgres_select_query = f""" SELECT  ROW_NUMBER () OVER (ORDER BY COUNT(b.genre) DESC) as "#", b.genre AS "GENRE", COUNT(b.genre) AS "COUNT" FROM user_action u JOIN books b 
                            ON b.book_id = u.book_id GROUP BY  b.genre 
                            ORDER BY COUNT(b.genre) DESC LIMIT 5 """
	cur.execute(postgres_select_query)
	display_table(cur)
	cur.close()
	conn.commit()
 
 
@app.command("fav_book")
def fav_book(book_id,username):
	cur = conn.cursor()
	postgres_insert_query = f""" INSERT INTO user_action (user_name,book_id,fav) VALUES ('{username}','{book_id}',true)"""
	cur.execute(postgres_insert_query)
	cur.close()
	conn.commit()
	typer.echo(f"{username} added book {book_id} to your favorites! '.")
 

@app.command("mark_read")
def mark_read(book_id,username):
	cur = conn.cursor()
	postgres_insert_query = f""" INSERT INTO user_action (user_name,book_id,read) VALUES ('{username}','{book_id}',true)"""
	cur.execute(postgres_insert_query)
	cur.close()
	conn.commit()
	typer.echo(f"{username} marked book {book_id} as 'read'.")
 
@app.command("my_books")
def my_books(username):
	typer.echo(f"BOOKS YOU READ")
	cur = conn.cursor()
	postgres_select_query = f""" select DISTINCT ON (b.book_id) ROW_NUMBER () OVER (ORDER BY b.book_id) as "#",
			b.book_id as "Book ID", b.title as "Name", b.author as "Author", b.pages as "# Pages",
			b.genre as "Genre",  b.quantity > 0 as "Availability" from books b join 
			user_action u on b.book_id=u.book_id where u.user_name='{username}' and u.read=true ORDER BY b.book_id"""
	cur.execute(postgres_select_query)
	display_table(cur)
	cur.close()
	conn.commit()
	typer.echo(f"BOOKS YOU ARE READING")
	cur = conn.cursor()
	postgres_select_query = f""" select DISTINCT ON (b.book_id) ROW_NUMBER () OVER (ORDER BY b.book_id) as "#",
			b.book_id as "Book ID", b.title as "Name", b.author as "Author", b.pages as "# Pages",
			b.genre as "Genre",  b.quantity > 0 as "Availability" from books b join 
			user_action u on b.book_id=u.book_id where u.user_name='{username}' and u.reading=true ORDER BY b.book_id"""
	cur.execute(postgres_select_query)
	display_table(cur)
	cur.close()
	conn.commit()
	typer.echo(f"BOOKS YOU WILL READ")
	cur = conn.cursor()
	postgres_select_query = f""" select DISTINCT ON (b.book_id) ROW_NUMBER () OVER (ORDER BY b.book_id) as "#",
			b.book_id as "Book ID", b.title as "Name", b.author as "Author", b.pages as "# Pages",
			b.genre as "Genre",  b.quantity > 0 as "Availability" from books b join 
			user_action u on b.book_id=u.book_id where u.user_name='{username}' and u.will_read=true ORDER BY b.book_id"""
	cur.execute(postgres_select_query)
	display_table(cur)
	cur.close()
	conn.commit()
	typer.echo(f"YOUR FAVORITE BOOKS")
	cur = conn.cursor()
	postgres_select_query = f""" select DISTINCT ON (b.book_id) ROW_NUMBER () OVER (ORDER BY b.book_id) as "#",
			b.book_id as "Book ID", b.title as "Name", b.author as "Author", b.pages as "# Pages",
			b.genre as "Genre",  b.quantity > 0 as "Availability" from books b join 
			user_action u on b.book_id=u.book_id where u.user_name='{username}' and u.fav=true ORDER BY b.book_id"""
	cur.execute(postgres_select_query)
	display_table(cur)
	cur.close()
	conn.commit()
	
	
 
# Example function for tables, you can add more columns/row.
@app.command("display_table")

def display_table(cursor):	
	table = Table(show_header=True, header_style="bold blue")
	column_names=[desc[0] for desc in cursor.description]
	for c in column_names:
		table.add_column(c, style="dim", min_width=10, justify=True)
	for d in cursor.fetchall():
		ll=[]
		for i in d:
			ll.append(f"{i}")  
		table.add_row(*ll)	
	console.print(table)

if __name__ == "__main__":
	app()
	