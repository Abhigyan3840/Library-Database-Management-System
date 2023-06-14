# Importing all necessary modules
import sqlite3
from tkinter import *
import tkinter.ttk as ttk
import tkinter.messagebox as mb
import tkinter.simpledialog as sd

# Connecting to Database
connector = sqlite3.connect('library.db')
cursor = connector.cursor()

connector.execute(
    'CREATE TABLE IF NOT EXISTS Library (BK_NAME TEXT, BK_ID TEXT PRIMARY KEY NOT NULL, AUTHOR_NAME TEXT, BK_STATUS TEXT, CARD_ID TEXT)'
)

# Functions
def issuer_card():
    Cid = sd.askstring('Issuer Card ID', 'What is the Issuer\'s Card ID?\t\t\t')
    if not Cid:
        mb.showerror('Issuer ID cannot be empty!', 'Can\'t keep Issuer ID empty, it must have a value')
    else:
        return Cid


def display_records():
    global connector, cursor
    global tree
    tree.delete(*tree.get_children())
    curr = cursor.execute('SELECT * FROM Library')
    data = curr.fetchall()
    for records in data:
        tree.insert('', END, values=records)


def clear_fields():
    global bk_status, bk_id, bk_name, author_name, card_id
    bk_status.set('Available')
    for i in ['bk_id', 'bk_name', 'author_name', 'card_id']:
        exec(f"{i}.set('')")
    try:
        tree.selection_remove(tree.selection()[0])
    except:
        pass


def clear_and_display():
    clear_fields()
    display_records()


def add_record():
    global connector
    global bk_name, bk_id, author_name, bk_status
    if bk_status.get() == 'Issued':
        card_id.set(issuer_card())
    else:
        card_id.set('N/A')
    surety = mb.askyesno('Are you sure?',
                        'Are you sure this is the data you want to enter?\nPlease note that Book ID cannot be changed in the future')
    if surety:
        try:
            cursor.execute(
                'INSERT INTO Library (BK_NAME, BK_ID, AUTHOR_NAME, BK_STATUS, CARD_ID) VALUES (?, ?, ?, ?, ?)',
                (bk_name.get(), bk_id.get(), author_name.get(), bk_status.get(), card_id.get()))
            connector.commit()
            clear_and_display()
            mb.showinfo('Record added', 'The new record was successfully added to your database')
        except sqlite3.IntegrityError:
            mb.showerror('Book ID already in use!',
                         'The Book ID you are trying to enter is already in the database, please alter that book\'s record or check any discrepancies on your side')


def view_record():
    global bk_name, bk_id, bk_status, author_name, card_id
    global tree
    if not tree.focus():
        mb.showerror('Select a row!', 'To view a record, you must select it in the table. Please do so before continuing.')
        return
    current_item_selected = tree.focus()
    values_in_selected_item = tree.item(current_item_selected)
    selection = values_in_selected_item['values']
    bk_name.set(selection[0])
    bk_id.set(selection[1])
    bk_status.set(selection[3])
    author_name.set(selection[2])
    try:
        card_id.set(selection[4])
    except:
        card_id.set('')


def wipe_database():
    surety = mb.askyesno('Are you sure?', 'Are you sure you want to wipe the entire database?\nThis action cannot be undone.')
    if surety:
        try:
            cursor.execute('DELETE FROM Library')
            connector.commit()
            clear_and_display()
            mb.showinfo('Database wiped', 'The database was successfully wiped. It is now empty.')
        except:
            mb.showerror('An error occurred', 'An error occurred while wiping the database. Please try again later.')


def update_record():
    global connector
    global bk_name, bk_id, author_name, bk_status, card_id
    if not tree.focus():
        mb.showerror('Select a row!', 'To update a record, you must select it in the table. Please do so before continuing.')
        return
    if bk_status.get() == 'Issued':
        card_id.set(issuer_card())
    elif bk_status.get() == 'Available':
        card_id.set('N/A')
    else:
        card_id.set('')
    surety = mb.askyesno('Are you sure?',
                        'Are you sure you want to update this record with the new data?\nPlease note that Book ID cannot be changed in the future')
    if surety:
        try:
            book_id = bk_id.get()
            cursor.execute('UPDATE Library SET BK_NAME = ?, AUTHOR_NAME = ?, BK_STATUS = ?, CARD_ID = ? WHERE BK_ID = ?',
                           (bk_name.get(), author_name.get(), bk_status.get(), card_id.get(), book_id))
            connector.commit()
            clear_and_display()
            mb.showinfo('Record updated', 'The selected record was successfully updated')
        except sqlite3.IntegrityError:
            mb.showerror('Book ID already in use!',
                         'The Book ID you are trying to update to is already in the database, please alter that book\'s record or check any discrepancies on your side')


def delete_record():
    global connector
    global tree
    if not tree.focus():
        mb.showerror('Select a row!', 'To delete a record, you must select it in the table. Please do so before continuing.')
        return
    surety = mb.askyesno('Are you sure?', 'Are you sure you want to delete this record? This action cannot be undone.')
    if surety:
        try:
            selected_item = tree.selection()[0]
            values_in_selected_item = tree.item(selected_item)
            selection = values_in_selected_item['values']
            book_id = selection[1]
            cursor.execute('DELETE FROM Library WHERE BK_ID = ?', (book_id,))
            connector.commit()
            clear_and_display()
            mb.showinfo('Record deleted', 'The selected record was successfully deleted')
        except:
            mb.showerror('An error occurred', 'An error occurred while deleting the record. Please try again later.')


# Main Program
root = Tk()
root.title('Library Database Management System')
root.configure(bg='#6600CC')  # Set the background color

# Creating the Treeview and Scrollbar
tree_frame = Frame(root)
tree_frame.pack(pady=20)
tree_scroll = Scrollbar(tree_frame)
tree_scroll.pack(side=RIGHT, fill=Y)
tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, style='Custom.Treeview')
tree.pack()
tree_scroll.config(command=tree.yview)

tree['columns'] = ('BK_NAME', 'BK_ID', 'AUTHOR_NAME', 'BK_STATUS', 'CARD_ID')
tree.column('#0', width=0, stretch=NO)
tree.column('BK_NAME', anchor=W, width=200)
tree.column('BK_ID', anchor=W, width=100)
tree.column('AUTHOR_NAME', anchor=W, width=200)
tree.column('BK_STATUS', anchor=CENTER, width=100)
tree.column('CARD_ID', anchor=W, width=100)

tree.heading('#0', text='', anchor=W)
tree.heading('BK_NAME', text='Book Name', anchor=W)
tree.heading('BK_ID', text='Book ID', anchor=W)
tree.heading('AUTHOR_NAME', text='Author Name', anchor=W)
tree.heading('BK_STATUS', text='Book Status', anchor=CENTER)
tree.heading('CARD_ID', text='Card ID', anchor=W)

# Adding the Book Details
book_details_frame = LabelFrame(root, text='Book Details', bg='#6600CC', fg='white')
book_details_frame.pack(fill='x', expand='yes', padx=20)

bk_name_label = Label(book_details_frame, text='Book Name: ', bg='#6600CC', fg='white')
bk_name_label.grid(row=0, column=0, padx=10, pady=10)
bk_name = StringVar()
bk_name_entry = Entry(book_details_frame, textvariable=bk_name)
bk_name_entry.grid(row=0, column=1, padx=10, pady=10)

bk_id_label = Label(book_details_frame, text='Book ID: ', bg='#6600CC', fg='white')
bk_id_label.grid(row=1, column=0, padx=10, pady=10)
bk_id = StringVar()
bk_id_entry = Entry(book_details_frame, textvariable=bk_id)
bk_id_entry.grid(row=1, column=1, padx=10, pady=10)

author_name_label = Label(book_details_frame, text='Author Name: ', bg='#6600CC', fg='white')
author_name_label.grid(row=2, column=0, padx=10, pady=10)
author_name = StringVar()
author_name_entry = Entry(book_details_frame, textvariable=author_name)
author_name_entry.grid(row=2, column=1, padx=10, pady=10)

bk_status_label = Label(book_details_frame, text='Book Status: ', bg='#6600CC', fg='white')
bk_status_label.grid(row=3, column=0, padx=10, pady=10)
bk_status = StringVar()
bk_status_combo = ttk.Combobox(book_details_frame, textvariable=bk_status, state='readonly')
bk_status_combo['values'] = ('Available', 'Issued', 'Lost')
bk_status_combo.grid(row=3, column=1, padx=10, pady=10)

card_id_label = Label(book_details_frame, text='Card ID: ', bg='#6600CC', fg='white')
card_id_label.grid(row=4, column=0, padx=10, pady=10)
card_id = StringVar()
card_id_entry = Entry(book_details_frame, textvariable=card_id, state='readonly')
card_id_entry.grid(row=4, column=1, padx=10, pady=10)

# Buttons
button_frame = Frame(root, bg='#6600CC')
button_frame.pack(pady=20)

add_button = Button(button_frame, text='Add Record', command=add_record, bg='#993399', fg='white')
add_button.grid(row=0, column=0, padx=10)

update_button = Button(button_frame, text='Update Record', command=update_record, bg='#993399', fg='white')
update_button.grid(row=0, column=1, padx=10)

delete_button = Button(button_frame, text='Delete Record', command=delete_record, bg='#993399', fg='white')
delete_button.grid(row=0, column=2, padx=10)

clear_button = Button(button_frame, text='Clear Fields', command=clear_fields, bg='#993399', fg='white')
clear_button.grid(row=0, column=3, padx=10)

view_button = Button(button_frame, text='View Record', command=view_record, bg='#993399', fg='white')
view_button.grid(row=0, column=4, padx=10)

wipe_button = Button(button_frame, text='Wipe Database', command=wipe_database, bg='#993399', fg='white')
wipe_button.grid(row=0, column=5, padx=10)

# Configure treeview style
style = ttk.Style()
style.configure('Custom.Treeview', background='#993399', foreground='white', fieldbackground='#993399')

# Displaying Records
display_records()

root.mainloop()

# Closing the database connection
connector.close()