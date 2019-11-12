import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import roc_auc_score


# reading csv file data
movie_data_orig = pd.read_csv("movies_metadata.csv")

# all column names
print(movie_data_orig.columns)

# removing irrelevant columns
df_cleaned = movie_data_orig.drop(["adult", "belongs_to_collection", "homepage", "id", "imdb_id", "original_language",
                                   "original_title", "overview", "poster_path", "production_countries", "release_date",
                                   "spoken_languages", "status", "tagline", "video" ], axis=1)
len(df_cleaned)       # 45466

# print(df_cleaned.head(5))
# taking into account only those movies where budget and/or revenue is greater than $100,000 (some of values in budget & revenue
# columns are 0, 1, 2, 3 etc which do not make any sense

df_cleaned.dtypes             # datatype of all columns in the dataframe; (budget is of "object" datatype instead of "int")
df_cleaned.describe()           # giving summary statistics of columns with dtype = float64

# budget column contains alpha-numeric characters, so need to fix it
df_cleaned['budget'] = df_cleaned['budget'].str.extract('(\d+)', expand=False)   # removing all non-numeric values from budget column

df_cleaned["budget"] = df_cleaned["budget"].astype(float).fillna(0.0)    # changing budget column from object to float
# df_cleaned.dtypes       # confirming that budget's dtype has changed to float64
# df_cleaned.describe()
df_cleaned = df_cleaned.loc[df_cleaned['budget'] > 100000]   # subsetting df to only movies with budget greater than $100,000

df_cleaned = df_cleaned.loc[df_cleaned['revenue'] > 1000]      # subsetting df to only movies with revenue greater than $1000


# creating our target/label column showing status i.e success/flop movie.
df_cleaned["status"] = df_cleaned["revenue"]/df_cleaned["budget"]
# df_cleaned.describe()
# df_cleaned.dtypes


# Our criteria for success is any value greater than 1 else flop
df_cleaned["New_status"] = np.nan      # creating a new empty column
df_cleaned["New_status"] = df_cleaned["New_status"].mask( df_cleaned["status"] > 1, 1)
df_cleaned["New_status"] = df_cleaned["New_status"].mask( df_cleaned["status"] <= 1, 0)


# # 1. converting (genre) json column to normal string column

df_cleaned['genres'] = df_cleaned['genres'].replace(np.nan,'{}',regex = True)
df_cleaned['genres'] = pd.DataFrame(df_cleaned['genres'].apply(eval))
# dividing all genres in a cell into separate cols/series, concating it to main df & then dropping the original "genres" column from df
df_cleaned = pd.concat([df_cleaned.drop(['genres'], axis=1), df_cleaned['genres'].apply(pd.Series)], axis=1)
# Removing all columns except the major genre type for each movie
df_cleaned.drop(df_cleaned.iloc[:, 11:18], inplace = True, axis = 1)
# creating separate series for "id" & "name" and concating it to main df
df_cleaned = pd.concat([df_cleaned.drop([0], axis=1), df_cleaned[0].apply(pd.Series)], axis=1)
df_cleaned.rename(columns = {'name' : 'Genre'}, inplace = True)   # renaming col
df_cleaned.drop(df_cleaned.iloc[:, 10:12], inplace = True, axis = 1)     # dropping extraneous cols
print(df_cleaned.columns)


# 2. converting (production_companies) json column to normal string column

df_cleaned['production_companies'] = df_cleaned['production_companies'].replace(np.nan,'{}',regex = True)
df_cleaned['production_companies'] = pd.DataFrame(df_cleaned['production_companies'].apply(eval))
df_cleaned = pd.concat([df_cleaned.drop(['production_companies'], axis=1), df_cleaned['production_companies'].apply(pd.Series)], axis=1)
df_cleaned.drop(df_cleaned.iloc[:, 11:36], inplace = True, axis = 1)
df_cleaned = pd.concat([df_cleaned.drop([0], axis=1), df_cleaned[0].apply(pd.Series)], axis=1)
df_cleaned.rename(columns = {'name' : 'Production Company'}, inplace = True)
df_cleaned.drop(df_cleaned.iloc[:, 10:12], inplace = True, axis = 1)
print(df_cleaned.columns)


# there are many entries where the number of people who voted for a movie are 1, 2 , 3 etc
df_cleaned = df_cleaned.loc[df_cleaned['vote_count'] > 100]      # subsetting df to only movies where atleast 100 people voted for a movie
len(df_cleaned)      # 3763

# Removing Duplicates
df_cleaned.drop_duplicates(inplace = True)
print(len(df_cleaned)) # 3763
print(df_cleaned.columns)

# Modeling
#Decision Tree Gini
# split the dataset into input and target variables
X = df_cleaned.loc[:,['runtime','vote_average','Genre', 'Production Company']]
y = df_cleaned.loc[:,['New_status']]

# encloding the class with sklearn's LabelEncoder
le = LabelEncoder()

# fit and transform the class
y = le.fit_transform(y)
X = pd.get_dummies(X)

# split the dataset into train and test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=100)

# perform training with giniIndex.
# creating the classifier object
clf_gini = DecisionTreeClassifier(criterion="gini", random_state=100, max_depth=3, min_samples_leaf=5)

# performing training
clf_gini.fit(X_train, y_train)

# predicton on test using gini
y_pred_gini = clf_gini.predict(X_test)

print("Classification Report: ")
print(classification_report(y_test,y_pred_gini))
print("Accuracy : ", accuracy_score(y_test, y_pred_gini) * 100)

#Decision Tree Entropy
# perform training with Entropy.
# creating the classifier object
clf_entropy = DecisionTreeClassifier(criterion="entropy", random_state=100, max_depth=3, min_samples_leaf=5)

# performing training
clf_entropy.fit(X_train, y_train)

# predicton on test using gini
y_pred_entropy = clf_entropy.predict(X_test)

print("Classification Report: ")
print(classification_report(y_test,y_pred_entropy))
print("Accuracy : ", accuracy_score(y_test, y_pred_entropy) * 100)

#Applying SVM Classification
# perform training
# creating the classifier object
clf = SVC(kernel="linear")

# performing training
clf.fit(X_train, y_train)

# predicton on test
y_pred_svm = clf.predict(X_test)

# calculate metrics
print("\n")

print("Classification Report: ")
print(classification_report(y_test,y_pred_svm))
print("\n")

print("Accuracy : ", accuracy_score(y_test, y_pred_svm) * 100)
print("\n")

#KNN
# standardize the data
stdsc = StandardScaler()

stdsc.fit(X_train)

X_train_std = stdsc.transform(X_train)
X_test_std = stdsc.transform(X_test)

# perform training
# creating the classifier object
clf_knn = KNeighborsClassifier(n_neighbors=3)

# performing training
clf_knn.fit(X_train_std, y_train)

#%%-----------------------------------------------------------------------
# make predictions

# predicton on test
y_pred_knn = clf.predict(X_test_std)

#%%-----------------------------------------------------------------------
# calculate metrics

print("\n")
print("Classification Report: ")
print(classification_report(y_test,y_pred_knn))
print("\n")


print("Accuracy : ", accuracy_score(y_test, y_pred_knn) * 100)
print("\n")

#Naive Bayese
# creating the classifier object
clf_nb = GaussianNB()

# performing training
clf_nb.fit(X_train, y_train)

#%%-----------------------------------------------------------------------
# make predictions

# predicton on test
y_pred_nb = clf_nb.predict(X_test)

y_pred_nb_score = clf_nb.predict_proba(X_test)

#%%-----------------------------------------------------------------------
# calculate metrics

print("\n")

print("Classification Report: ")
print(classification_report(y_test,y_pred_nb))
print("\n")


print("Accuracy : ", accuracy_score(y_test, y_pred_nb) * 100)
print("\n")

print("ROC_AUC : ", roc_auc_score(y_test,y_pred_nb_score[:,1]) * 100)
print("\n")
