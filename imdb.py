import matplotlib.pyplot as plt

import pandas as pd

from bs4 import BeautifulSoup

from requests import get

import seaborn as sns

sns.set(rc={'figure.figsize':(11.7,8.27)})

fromyear = int(input("Enter From Year: "))
tillyear = int(input("Till Year: "))

# Redeclaring the lists to store data in
names = [] 
years = []
imdb_ratings = []
metascores = []
votes = []
pages = [str(i) for i in range(1, 5)]
years_url = [str(i) for i in range(fromyear, tillyear)]
Movieshowtime = []
Moviegenre=[]


for year_url in years_url:


    for page in pages:


        response = get('http://www.imdb.com/search/title?release_date=' + year_url +
                       '&sort=num_votes,desc&page=' + page + '"Accept-Language": "en-US, en;q=0.5"')


        page_html = BeautifulSoup(response.text, 'html.parser')


        mv_containers = page_html.find_all('div', class_='lister-item mode-advanced')

        # For every movie of these 50
        for container in mv_containers:

            if container.find('div', class_='ratings-metascore') is not None:

                name = container.h3.a.text
                names.append(name)

                year = container.h3.find('span', class_='lister-item-year').text
                years.append(year)


                imdb = float(container.strong.text)
                imdb_ratings.append(imdb)

                m_score = container.find('span', class_='metascore').text
                metascores.append(int(m_score))


                vote = container.find('span', attrs={'name': 'nv'})['data-value']
                votes.append(int(vote))

                showtime = container.p.find('span', class_='runtime').text
                Movieshowtime.append((int(showtime.replace(" min", ''))))

                genre = container.p.find('span', class_='genre').text
                genre = str(genre)
                genre = genre.replace("\n", '')
                Moviegenre.append((genre))

movie_ratings = pd.DataFrame({'movie': names,
                              'year': years,
                              'imdb': imdb_ratings,
                              'metascore': metascores,
                              'votes': votes,
                              'runtime': Movieshowtime,
                              'genre':Moviegenre})
print(movie_ratings.info())
movie_ratings.head(10)
print(movie_ratings)
movie_ratings.to_csv('mov.csv', index=False)

imdb_csv = r'C:\Users\sw\1.csv'
df = pd.read_csv(imdb_csv)

print("Average Run time of the movies are :",df['runtime'].mean())

df.sort_values('imdb')
df.to_csv('123.csv', index=False)

df[['imdb','votes']].groupby('imdb').count().plot(kind='bar', title='IMDB ratings Visualization')
plt.xlabel('Votes')
plt.ylabel('')
plt.show()

categories = set([s for genre_list in df.genre.unique() for s in genre_list.split(",")])

# one-hot encode each movie's classification
for cat in categories:
    df[cat] = df.genre.transform(lambda s: int(cat in s))
# drop other columns
df = df[['genre','runtime'] + list(categories)]
# convert from wide to long format and remove null classificaitons
df = pd.melt(df,
             id_vars=['runtime'],
             value_vars = list(categories),
             var_name = 'Category',
             value_name = 'Count')
df = df.loc[df.Count>0]
top_categories = df.groupby('Category').aggregate(sum).sort_values('Count', ascending=False).index
howmany=8
# add an indicator whether a movie is short or long, split at 100 minutes runtime
df['duration'] = df.runtime.transform(lambda x: int(x > 100))
df = df.loc[df.Category.isin(top_categories[:howmany])]
p = sns.countplot(data=df, x = 'Category')
plt.show()
p = sns.countplot(data=df,
                  y = 'Category',
                  hue = 'duration')
plt.show()

