# doing necessary imports

from flask import Flask, render_template, request, jsonify
#from flask_cors import CORS, cross_origin  # for secured https like amazon
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
#import pymongo  # commented for deploying on Heroku

app=Flask(__name__) #initialising the flask  app with the name 'app'

@app.route('/',methods=['GET'])  # route to display the home page
#@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) #route with allowed methods as POST and GET

def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ", "")  # obtaining the search string entered in the form
            # dbConn = pymongo.MongoClient("mongodb://localhost:27017/")  # opening a connection to Mongo
            # db = dbConn['crawlerDB']  # connecting to the database called crawlerDB
            # reviews = db[searchString].find({})  # searching the collection with the name same as the keyword
            # if reviews.count() > 0:  # if there is a collection with searched keyword and it has records in it
            #     return render_template('results.html', reviews=reviews)  # show the results to user
            # else:
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString # preparing the url to search the product on flipkart
            uClient = uReq(flipkart_url) # requesting the webpage from the internet
            flipkartPage = uClient.read() #reading the webpage
            uClient.close() # closing the connection to the webserver
            flipkart_html = bs(flipkartPage,"html.parser") # parsing the webpage as HTML
            bigboxes = flipkart_html.findAll('div', {"class": "_1AtVbE col-12-12"}) # finding the HTML section containing the customer comments
            del bigboxes[0:3]  # the first 3 members of the list do not contain relevant information, hence deleting them.
            box = bigboxes[0]  # taking the first iteration (for demo)
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']  # extracting the actual product link
            prodRes = requests.get(productLink)  # getting the product page from server
            prodRes.encoding = 'utf-8'
            prod_html = bs(prodRes.text, "html.parser")  # parsing the product page as HTML
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})  # finding the HTML section containing the customer comments

            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)

                # table = db[searchString]  # creating a collection with the same name as search string. Tables and Collections are analogous.
            reviews = []  # initializing an empty list for reviews
                #  iterating over the comment section to get the details of customer and their comments
            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all('p', {'class': "_2sc7ZR _2V5EHH"})[0].text

                except:
                    name = 'No Name'

                try:
                    rating = commentbox.div.div.div.div.text

                except:
                    rating = 'No Rating'

                try:
                    commentHead = commentbox.div.div.div.p.text

                except:
                    commentHead = 'No Comment Heading'

                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    custComment = comtag[0].div.text
                except:
                    custComment = 'No Customer Comment'

                    mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                            "Comment": custComment}  # saving that detail to a dictionary
                    # x = table.insert_one(mydict)  # insertig the dictionary containing the rview comments to the collection
                    reviews.append(mydict)  # appending the comments to the review list
                return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])  # showing the review to the user
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    else:
        return render_template('index.html')

if __name__ == "__main__":
    #app.run(port=8000, debug=True)  # running the app on the local machine on port 8000
    app.run(debug=True)



















