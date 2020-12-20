import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import *
import sqlite3
from tkinter import messagebox
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

#import modules Start Region
from RedditAPI import GetData, GetUserData
from BotClassifier import BotClassifier
from TextRank import Summarizer
from SentimentAnalysis import SentimentAnalyzer
from TextRank import Keywords
#import modules End Region

# Region 1 Start(Window Settings)
window = Tk()
window.title("Text Analyzer")

w = window.winfo_reqwidth()
h = window.winfo_reqheight()
ws = window.winfo_screenwidth()
hs = window.winfo_screenheight()
x = (ws/4) - (w/4)
y = (hs/4) - (h/4)
window.geometry('+%d+%d' % (x, y))

window.config(background='black')

style = ttk.Style(window)
style.configure('lefttab.TNotebook', tabposition='wn',)

tab_control = ttk.Notebook(window, style='lefttab.TNotebook')

tab1 = ttk.Frame(tab_control, height=100)
tab2 = ttk.Frame(tab_control, height=100)
tab3 = ttk.Frame(tab_control, height=100)
tab5 = ttk.Frame(tab_control, height=100)

# ADD TABS TO NOTEBOOK
tab_control.add(tab1, text=f'{"Reddit API":^30s}')
tab_control.add(tab2, text=f'{"TextRank Algorithm":^20s}')
tab_control.add(tab3, text=f'{"Sentiment Analysis":^20s}')

label1 = Label(tab1, text='Reddit API', padx=5, pady=5)
label1.grid(column=0, row=0)

label2 = Label(tab2, text='TextRank Algorithm', padx=5, pady=5)
label2.grid(column=1, row=0)

label3 = Label(tab3, text='Sentiment Analysis', padx=5, pady=5)
label3.grid(column=1, row=0)

label4 = Label(tab5, text='About', padx=5, pady=5)
label4.grid(column=0, row=0)

tab_control.pack(expand=1, fill='both')
# Region 1 End(Window Settings)

# Functions
def get_reddit():
	query_s = str(query_str.get('1.0',tk.END))
	query_s = query_s.strip()
	subreddits = str(entry.get('1.0',tk.END)).split(',')
	data = GetData.GetData
	try:
		for sub in subreddits:
			word = sub.rstrip()
			data.getdata(int(limit_text.get('1.0',tk.END)), word, search_query=query_s)
	except:
		messagebox.showinfo("Exception", f"Exception occurred with {word.upper()}, possible reasons: \n 1. There is no such topic \n 2. Incorrectly entered topic \n 3. Other \n\n Try again!")
		print()
	get_records()

def deEmojify(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')

def get_records():
	records = tree.get_children()
	for element in records:
		tree.delete(element)
	query = 'SELECT DISTINCT topicTitle, topicText, topicCategory FROM topics ORDER BY topicText ASC'
	con = sqlite3.connect('reddit.db')
	c = con.cursor()
	db_rows = c.execute(query)
	gv_count = 0

	for row in db_rows:
		tree.insert('', 0, text = deEmojify(row[0]), values = (deEmojify(row[1]), row[2]))
		gv_count = gv_count + 1

	label1 = Label(tab1, text=f'Result: { gv_count } row(s)', padx=5, pady=5)
	label1.place(x=180, y=270)

def summarize():
	text = str(displayed_file.get('1.0',tk.END))
	if text == '\n':
		messagebox.showinfo("Error", "Input field cannot be empty")
	else:
		tab2_display_text.insert(INSERT, Summarizer.summarize(text, language='english', ratio=0.4, words=500))
	word_cloud()

def word_cloud():
	text = str(displayed_file.get('1.0',tk.END))
	words = Keywords.keywords(text)
	word_cloud = WordCloud(width=1000, height=1000, background_color='white', stopwords=STOPWORDS).generate(words)
	plt.figure(figsize=(10, 8), facecolor='white', edgecolor='blue')
	plt.imshow(word_cloud)
	plt.axis('off')
	plt.show(block=False)

def get_topics():
		query = 'SELECT DISTINCT topicText FROM topics'
		con = sqlite3.connect('reddit.db')
		c = con.cursor()
		db_rows = c.execute(query)
		# try:
		for row in db_rows:
			row = ''.join(row)
			displayed_file.insert(INSERT, deEmojify(row))
		print("Topics")
		# except:
			# messagebox.showinfo("Error", row)

def get_sentiment():
	fig1, ax1 = plt.subplots(2)
	sentiment = SentimentAnalyzer.Sentiment
	category = url_entry.get()
	classifier = BotClassifier.BotClassifier()
	print("Bot check", bot_check.get())
	troll_count = 0
	bot_count = 0
	normal_count = 0
	try:
		query = f'SELECT DISTINCT commentText, topicAuthor FROM comments WHERE topicCategory = \'{category}\''
		con = sqlite3.connect('reddit.db')
		c = con.cursor()
		db_rows = c.execute(query)
		text = []
		for row in db_rows:
			if bot_check.get():
				user = GetUserData.UserData(row[1])
				features = user.get_features()
				predicted = classifier.predict(features)
				print(predicted, row[1])
				if predicted[0] == 'normal':
					text.append(row[0])
					normal_count += 1
				elif predicted[0] == 'troll':
					troll_count += 1
				elif predicted[0] == 'bot':
					bot_count += 1
			else:
				text.append(row[0])
		res = sentiment.get_sentiment(text)
		print("res", res)

		url_display.insert(INSERT, "poz: " + str("{0:.0f}%".format(100 * res[0] / sum(res))) + '\n')
		url_display.insert(INSERT, "neu: " + str("{0:.0f}%".format(100 * res[1] / sum(res))) + '\n')
		url_display.insert(INSERT, "neg: " + str("{0:.0f}%".format(100 * res[2] / sum(res))) + '\n')
		ax1[0].pie(res, labels=['poz', 'neu', 'neg'], autopct='%1.1f%%',
				 		  shadow=True, startangle=90)
		ax1[0].axis('equal')

	except:
		messagebox.showinfo("Error", f"{str(category).upper()} topic does not exist")

	if bot_check.get():
		labels = ['trolls', 'bots', 'normal users']
		ax1[1].pie([troll_count, bot_count, normal_count],labels=labels, autopct='%1.1f%%',
				shadow=True, startangle=90)
		ax1[1].axis('equal')
	plt.show()

# Clear entry widget
def clear_text():
    clear_display_result()
    entry.delete('1.0', END)

def clear_display_result():
	limit_text.delete('1.0',END)

# Clear Text  with position 1.0
def clear_text_file():
	displayed_file.delete('1.0',END)

# Clear Result of Functions
def clear_text_result():
	tab2_display_text.delete('1.0',END)

def clear_url_display():
	url_display.delete('1.0',END)

# Reddit tab
l1=Label(tab1,text="Enter comma separated subbredits")
l1.grid(row=1,column=0)

l1=Label(tab1,text="Limit")
l1.place(x=5, y=175)

l1=Label(tab1,text="Search")
l1.place(x=5, y=145)

entry=Text(tab1,height=5, width=50)
entry.grid(row=2,column=0,columnspan=2,padx=5,pady=5)

limit_text = Text(tab1, height=1, width=10)
limit_text.place(x=50, y=175)

query_str = Text(tab1, height=1, width=44)
query_str.place(x=50, y=145)

tree = ttk.Treeview(tab1, height=15, columns=["", ""])
tree.place(x=5, y=310)
tree.heading('#0', text='topicTitle', anchor=W)
tree.heading('#1', text='topicText', anchor=W)
tree.heading('#2', text='topicCategory', anchor=W)

# BUTTONS
button1=Button(tab1,text="Clear",command=clear_text, width=12,bg='#03A9F4',fg='#fff')
button1.place(x=150, y=220)

button3=Button(tab1,text="Get Data", command=get_reddit,width=12,bg='#03A9F4',fg='#fff')
button3.place(x=5, y=220)

#TextRank tab
l1=Label(tab2,text="Enter text to summarize")
l1.grid(row=1,column=1)

displayed_file = ScrolledText(tab2,height=7)# Initial was Text(tab2)
displayed_file.grid(row=2,column=0, columnspan=3,padx=5,pady=3)

# BUTTONS FOR SECOND TAB/FILE READING TAB

b2=Button(tab2,text="Summarize ", width=12,command=summarize,bg='#03A9F4',fg='#fff')
b2.grid(row=3,column=0,padx=10,pady=10)

b4=Button(tab2,text="Get Topics ", width=12,command=get_topics,bg='#03A9F4',fg='#fff')
b4.grid(row=5,column=0,padx=10,pady=10)

b1=Button(tab2,text="Clear ", width=12,command=clear_text_file,bg='#03A9F4',fg='#fff')
b1.grid(row=3,column=1,padx=10,pady=10)

b3=Button(tab2,text="Clear Result", width=12,command=clear_text_result, bg='#03A9F4',fg='#fff')
b3.grid(row=5,column=1,padx=10,pady=10)

# Display Screen
# tab2_display_text = Text(tab2)
tab2_display_text = ScrolledText(tab2,height=10)
tab2_display_text.grid(row=7,column=0, columnspan=3,padx=5,pady=5)

# Allows you to edit
tab2_display_text.config(state=NORMAL)

# Sentiment tab
l1=Label(tab3,text="Analysis of this topic")
l1.grid(row=1,column=0)

raw_entry=StringVar()
url_entry=Entry(tab3,textvariable=raw_entry,width=50)
url_entry.place(x=130, y=30)


bot_check = BooleanVar()
bot_check.set(0)
bot_checkbox = Checkbutton(tab3, text="Check bots", variable=bot_check, onvalue=1, offvalue=0)
bot_checkbox.place(x=130, y=50)

# BUTTONS
button1=Button(tab3,text="Analyze",command=get_sentiment, width=12,bg='#03A9F4',fg='#fff')
button1.grid(row=4,column=0,padx=10,pady=10)

button3=Button(tab3,text="Clear Result", command=clear_url_display,width=12,bg='#03A9F4',fg='#fff')
button3.grid(row=5,column=0,padx=10,pady=10)

l1=Label(tab3,text="Result")
l1.place(x=100, y=150)

# Display Screen For Result
url_display = ScrolledText(tab3,height=10, width=50)
url_display.place(x=100, y=180)

# About tab
about_label = Label(tab5,text="Thesis Mileev Daniil \n 4th year student \n\n Modules: \n Reddit API \n TextRank Algorithm \n Sentiment Analysis",pady=10,padx=250)
about_label.grid(column=0,row=1)

window.mainloop()

