import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, render_template
from config import pwd
import json

#connection_string = "postgres:postgres@localhost:5432/Quotes"
#engine = create_engine('postgresql://postgres:password@localhost/Quotes')
rds_connection_string = f"postgres:{pwd}@localhost:5432/ETL_Project"
engine = create_engine(f'postgresql://{rds_connection_string}')

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)


app = Flask(__name__)

#######################################
def tags_for_the_quote(quote_id):
    tags = []
    print(f'getting tags for {quote_id}')
    tags_result = engine.execute(
        f'select tag  from tag where quote_id= {quote_id}')
    for tagrow in tags_result:
        tags.append(tagrow.tag)
    return tags
########################################


@app.route("/")
def welcome():
    """List all available api routes."""
    return render_template("index.html")

#################################################
# ALL QUOTES Route
#################################################
@app.route("/quotes")
def quotes():
     data = engine.execute('''SELECT quote.quote_text, quote.author_name, tag.tag
                            FROM quote, tag
                            WHERE quote.quote_id = tag.quote_id
                            group by quote.quote_text, quote.author_name, tag.tag ''').fetchall()
    #for result in data:
     #   quote = {'text': result.quote_text.replace('\u201c','').replace('\u201d',''), 'author name': result.author_name, 'tags': result.tag}
      #  results.append(quote)    
    #return jsonify(result)
    results = [list(row) for row in data]
    test = []
    for x in range(0, len(results)):
        result_dict = {'text': results[x][0].replace('\u201c','').replace('\u201d','').replace('\u2032',''), 'author':results[x][1], 'tags' : results[x][2]}
        test.append(result_dict)
    return jsonify(test)     
#     results = []
#     data = engine.execute('''SELECT quote.quote_text, quote.author_name, tag.tag
#                             FROM quote, tag
#                             WHERE quote.quote_id = tag.quote_id
#                             group by quote.quote_text, quote.author_name, tag.tag ''').fetchall()
# ​
#     for result in data:
#         quote = {'text': result.quote_text.replace('\u201c','').replace('\u201d',''), 'author name': result.author_name, 'tags': result.tag}
#         results.append(quote)    



#Route to all authors
@app.route("/authors/")
def author_name():
    results = []
    total = []
    author_count = engine.execute('''SELECT COUNT(name) FROM author''').fetchall()[0]
    Count = {'Author Count':author_count}
    total.append(Count)
    data = engine.execute('''SELECT author.name, author.born, author.description, quote.quote_text, count(quote.quote_id) as c
    FROM author, quote
    WHERE author.name = quote.author_name
    group by author.name, author.born, author.description, quote.quote_text ''').fetchall()
    for result in data:
        author = {'name': result.name ,'born' : str(result.born), 'description': result.description , 'quotes': result.quote_text.replace('\u201c','').replace('\u201d',''), 'Count by author': result.c}

        results.append(author)
    print(total)
    return jsonify(results)

#Route to individual author names (passed in)
@app.route("/authors/<author_name>")
def oneauthor(author_name):

    results = []
    total = []
    author_count = engine.execute('''SELECT COUNT(name) FROM author''').fetchall()[0]
    Count = {'Author Count':author_count}
    total.append(Count)
    
    data = engine.execute(f"SELECT author.name, author.born, author.description, quote.quote_text, count(quote.quote_id) as c\
                            FROM author\
                            left join quote on\
                                author.name = quote.author_name\
                            WHERE author.name = '{author_name}'\
                            group by author.name, author.born, author.description, quote.quote_text").fetchall()
    
    
    for result in data:
        ind_author = {'name': result.name ,'born' : str(result.born), 'description': result.description , 'quotes': result.quote_text.replace('\u201c','').replace('\u201d',''), 'Count by author': result.c}
        
        results.append(ind_author)
    
    return jsonify(results)  

#route to all tags
@app.route("/tags")
def tags():
    results_1 = []
    total = []
    tags_count = engine.execute('''SELECT COUNT(*) FROM tag''').fetchall()[0]
    Count_1 = {'Author Count':tags_count}
    total.append(Count_1)
    data_1 = engine.execute('''With count_tags as (
                                Select tag.tag, count(quote_id) as tag_count
                                from	tag
                                group by tag.tag)
                                
                                select t.tag, ct.tag_count, q.quote_text
                                from  tag t
                                left join
                                    count_tags ct on
                                    t.tag = ct.tag
                                left join
                                    quote q on
                                    t.quote_id = q.quote_id ''').fetchall()
    for result_1 in data_1:
        tags_1 = {'name': result_1.tag ,'number of quotes' : result_1.tag_count, 'quotes': result_1.quote_text.replace('\u201c','').replace('\u201d','')}

        results_1.append(tags_1)
    print(total)
    return jsonify(results_1)

@app.route("/tags/<tag_name>")
def onetag(tag_name):
    result = {}
    sub_result = []
    result['tag'] = tag_name
    quotes_result = engine.execute(f"select q.quote_id, quote_text from quote q inner join tag t on q.quote_id=t.quote_id where t.tag =  '{tag_name}'").fetchall()
    for row in quotes_result:
        quote_return = {}
        quote_return['text'] = row.quote_text
        quote_return['tags'] = tags_for_the_quote(row.quote_id)
        sub_result.append(quote_return)

    
    result['quotes'] = sub_result
    result['count'] = len(sub_result)
    return jsonify(result)



# Route to top 10 tags
@app.route("/top10tags")
def top10tags():
    result = []
    tags_result_set = engine.execute('''select tag , count(quote_id) as total from tag
                                        group by tag
                                        order by total desc
                                        limit 10''')

    for row in tags_result_set:
        tag = {}
        tag['tag'] = row.tag
        tag['total'] = row.total
        result.append(tag)
    return jsonify(result)






if __name__ == '__main__':
    app.run(debug=True)
