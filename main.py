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
 

@app.command("fav_book")
def fav_book(book_id: int, user_name: str):
	cur = conn.cursor()
	
	postgres_select_query = f"""select book_id , user_name from user_action where book_id = '{book_id}' and user_name = '{user_name}' """
	cur.execute(postgres_select_query)

	q1 = cur.fetchone()
	if q1 is not None:
		postgres_update_query = f"""update user_action set fav = 'true' where book_id = '{book_id}' and user_name = '{user_name}' """
		cur.execute(postgres_update_query)
		typer.echo(f"You added book {book_id} to your favorites!'")
		
	else:
		postgres_select_query = f"""select u.user_name, b.book_id from users u , books b  where b.book_id = '{book_id}' and u.user_name = '{user_name}' """
		cur.execute(postgres_select_query)
		q1 = cur.fetchone()
		if q1 is not None:
			postgres_insert_query = f""" INSERT INTO user_action (user_name,book_id,fav) VALUES ('{user_name}','{book_id}',true)"""
			cur.execute(postgres_insert_query)
			typer.echo(f"You added book {book_id} to your favorites!'")
		else:
			typer.echo(f"Sorry, user name or book id is incorrect!")
	
	cur.close()
	conn.commit()
 

@app.command("mark_read")
def mark_read(book_id: int, user_name: str):
	cur = conn.cursor()
	
	postgres_select_query = f"""select book_id , user_name from user_action where book_id = '{book_id}' and user_name = '{user_name}' """
	cur.execute(postgres_select_query)

	q1 = cur.fetchone()
	if q1 is not None:
		postgres_update_query = f"""update user_action set read = 'true' where book_id = '{book_id}' and user_name = '{user_name}' """
		cur.execute(postgres_update_query)
		typer.echo(f"You marked book {book_id} as read!")
		
	else:
		postgres_select_query = f"""select u.user_name, b.book_id from users u , books b  where b.book_id = '{book_id}' and u.user_name = '{user_name}' """
		cur.execute(postgres_select_query)
		q1 = cur.fetchone()
		if q1 is not None:
			postgres_insert_query = f""" INSERT INTO user_action (user_name,book_id,read) VALUES ('{user_name}','{book_id}',true)"""
			cur.execute(postgres_insert_query)
			typer.echo(f"You marked book {book_id} as reading!")
		else:
			typer.echo(f"Sorry, user name or book id is incorrect!")
	
	cur.close()
	conn.commit()
 
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


###################################################################################33333333333333333333333

@app.command("add_book")
def add_book():
	typer.echo(f"Please provide book detail!")
	cur = conn.cursor()
	title = input ("Title: ")
	author = input ("Author: ")
	pages = input ("No. of pages: ")
	genre = input ("Genre: ")
	quantity= int(input ("Quantity: "))

	postgres_select_query = f"""select quantity from books where title = '{title}' and author = '{author}' """

	cur.execute(postgres_select_query)

	q1 = cur.fetchone()
	if q1 is not None:
		q2 = q1[0]
		updated_quantity = q2+ quantity
		postgres_update_query = f"""update books set quantity = '{updated_quantity}'  where title = '{title}' and author = '{author}' """
		cur.execute(postgres_update_query)
		typer.echo(f"Successfully updated book's quantity!")
	
	else:
		postgres_insert_query = f""" INSERT INTO books (title,author,genre,pages,quantity) VALUES ('{title}','{author}','{genre}','{pages}','{quantity}')"""
		cur.execute(postgres_insert_query)
		typer.echo(f"Successfully added book!")
	
	cur.close()
	conn.commit()

##################################################################################################66666666666666666

@app.command("recently_added")
def recently_added(genre: Optional[str]= typer.Argument(None)):
	cur = conn.cursor()
	if genre is None:
		postgres_select_query = f"""
select ROW_NUMBER () OVER (order by added_date desc) as "#", book_id as "Book ID", title as "Name", author as "Author", pages as "# Pages",
							genre as "Genre", case when quantity> 0 then 'True'
													when quantity = 0 then 'False' end "Availability"
													from books order by added_date desc limit 5;"""
		cur.execute(postgres_select_query)
    
	
	else:
		postgres_select_query = f"""select ROW_NUMBER () OVER (order by added_date desc) as "#", book_id as "Book ID", title as "Name", author as "Author", pages as "# Pages",
							genre as "Genre", case when quantity> 0 then 'True'
													when quantity = 0 then 'False' end  "Availability"
													from books where genre = '{genre}' order by added_date desc limit 5 ;"""
		cur.execute(postgres_select_query)

	display_table(cur)
	cur.close()
	conn.commit()

#############################################################################################88888888888888888888888888
@app.command("most_favorite_books")
def most_favorite_books(genre: Optional[str]= typer.Argument(None)):
	cur = conn.cursor()
	if genre is None:
		postgres_select_query = f"""select row_number() over(order by count(fav) desc) as "#",ac.book_id as "Book ID", b.title as "Name", b.author as "Author"
								, b.genre  as "Genre", count(fav) as "Count"
								from user_action ac, books b where ac.book_id  = b.book_id and fav = 'true'  group by ac.book_id , b.title, b.author, b.genre order by count(fav) desc limit 10;"""
		cur.execute(postgres_select_query)

	else:
		postgres_select_query = f"""select row_number() over(order by count(fav) desc) as "#",ac.book_id as "Book ID", b.title as "Name"
								, b.author as "Author", b.genre  as "Genre", count(fav) as "Count"from user_action ac, books b 
								where ac.book_id  = b.book_id and fav = 'true' and genre =  '{genre}' 
								group by ac.book_id , b.title, b.author, b.genre order by count(fav) desc limit 10;"""
		cur.execute(postgres_select_query)

	display_table(cur)
	cur.close()
	conn.commit()
	
#################################################################################################################14 14 14 14 14 14
@app.command("mark_reading")
def mark_reading(book_id: int, user_name: str):
	cur = conn.cursor()
	
	postgres_select_query = f"""select book_id , user_name from user_action where book_id = '{book_id}' and user_name = '{user_name}' """
	cur.execute(postgres_select_query)

	q1 = cur.fetchone()
	if q1 is not None:
		postgres_update_query = f"""update user_action set reading = 'true' where book_id = '{book_id}' and user_name = '{user_name}' """
		cur.execute(postgres_update_query)
		typer.echo(f"You marked book {book_id} as reading!")
		
	else:
		postgres_select_query = f"""select u.user_name, b.book_id from users u , books b  where b.book_id = '{book_id}' and u.user_name = '{user_name}' """
		cur.execute(postgres_select_query)
		q1 = cur.fetchone()
		if q1 is not None:
			postgres_insert_query = f""" INSERT INTO user_action (user_name,book_id,reading) VALUES ('{user_name}','{book_id}',true)"""
			cur.execute(postgres_insert_query)
			typer.echo(f"You marked book {book_id} as reading!")
		else:
			typer.echo(f"Sorry, user name or book id is incorrect!")
	
	cur.close()
	conn.commit()
#########################################################################################################################

@app.command("statistics")
def statistics(user_name: str):
	cur = conn.cursor()
	
	postgres_select_query = f"""select count(read), count(distinct (b.author)), count(distinct(b.genre)), sum(b.pages)from user_action ac, books b where ac.book_id = b.book_id and read = 'true' and ac.user_name = '{user_name}'; """
	cur.execute(postgres_select_query)
	q=(cur.fetchall())

	table = Table(show_header=True, header_style="bold blue")
	table.add_column("Statistic", style="dim", width=30)
	table.add_column("Number", style="dim", min_width=10, justify=True)
	
	table.add_row('Books you read', str(q[0][0]))
	table.add_row('Authors you read', str(q[0][1]))
	table.add_row('Genres you read', str(q[0][2]))
	table.add_row('Total pages you read', str(q[0][3]))
	console.print(table)



if __name__ == "__main__":
	app()
	