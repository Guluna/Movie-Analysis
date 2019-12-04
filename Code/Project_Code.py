import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import shapiro


from sklearn.tree import DecisionTreeClassifier # Import Decision Tree Classifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split # Import train_test_split function
from imblearn.over_sampling import RandomOverSampler #For over sampling
from sklearn import metrics
import sklearn.metrics as metrics #Import scikit-learn metrics module for accuracy calculation
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from sklearn.metrics.classification import cohen_kappa_score
from statistics import mode
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize

# Libraries to display decision tree
from pydotplus import graph_from_dot_data
from sklearn.tree import export_graphviz
import webbrowser

# #%%-----------------------------------------------------------------------
# import os
# os.environ["PATH"] += os.pathsep + '/Graphviz2.38/bin'
# #%%-----------------------------------------------------------------------
#
# # Libraries for GUI
# import sys
# from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QPushButton, QAction, QComboBox, QLabel,
#                              QGridLayout, QCheckBox, QGroupBox, QVBoxLayout, QHBoxLayout, QLineEdit, QPlainTextEdit)
# from PyQt5.QtGui import QIcon
# from PyQt5.QtCore import pyqtSlot
# from PyQt5.QtCore import pyqtSignal
# from PyQt5.QtCore import Qt
# from scipy import interp
# from itertools import cycle
# from PyQt5.QtWidgets import QDialog, QVBoxLayout, QSizePolicy, QMessageBox
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
# from matplotlib.figure import Figure

#set seed
seed = 100

# reading csv file data
import pandas as pd
movie_data_orig = pd.read_csv(r'C:\Users\Madhuri Yadav\PycharmProjects\Final-Project-Group8\Code\movies_metadata.csv')
# print(movie_data_orig)     # [45466 rows x 24 columns]

# removing 10 irrelevant columns
df_cleaned = movie_data_orig.drop(["adult", "belongs_to_collection", "homepage", "original_title", "overview", "poster_path", "production_countries",
                                   "spoken_languages", "status", "tagline", "video" ], axis=1)

# print(df_cleaned.columns)   #  'budget', 'genres', 'id', 'imdb_id' 'popularity', 'production_companies', 'release_date', 'revenue', 'runtime', 'title', 'vote_average', 'vote_count']
#df_cleaned.dtypes       # release_date is of object (i.e. string data type) instead of datetime

# budget column contains alpha-numeric characters, so need to fix it
df_cleaned['budget'] = df_cleaned['budget'].str.extract('(\d+)', expand=False)   # removing all non-numeric values from budget column
# changing budget column from object to float
df_cleaned["budget"] = df_cleaned["budget"].astype(float).fillna(0.0)
df_cleaned = df_cleaned.loc[(df_cleaned['budget'] > 100000) & (df_cleaned['revenue'] > 1000)]   # subsetting df to only movies with budget greater than $100,000 & revenue greater than $1000
# df_cleaned = df_cleaned.loc[]      # subsetting df to only movies with

# creating our target/label column showing status i.e success/flop movie.
df_cleaned["status"] = df_cleaned["revenue"]/df_cleaned["budget"]
# Our criteria for success is any value greater than 1 else flop
df_cleaned["New_status"] = np.nan      # creating a new empty target column called New_Status
df_cleaned["New_status"] = df_cleaned["New_status"].mask( df_cleaned["status"] > 1, 1)
df_cleaned["New_status"] = df_cleaned["New_status"].mask( df_cleaned["status"] <= 1, 0)
df_cleaned["New_status"] = df_cleaned["New_status"].astype("category")      # converting from float to categorical datatye

# there are many entries where the number of people who voted for a movie are 1, 2 , 3 etc. They need to be removed otherwise it will create bias
df_cleaned = df_cleaned.loc[(df_cleaned['vote_count'] > 100) & df_cleaned["vote_average"] > 0]      # subsetting df to only movies where atleast 100 people voted for a movie & vote_average > 0

# rearranging columns of dataframe
cols = df_cleaned.columns.tolist()
# Setting Genre as last col for easier manipulation
cols = ['budget', 'id', 'imdb_id', 'popularity', 'original_language', 'production_companies', 'release_date', 'revenue', 'runtime', 'title', 'vote_average', 'vote_count', 'status', 'New_status', 'genres']
df_cleaned = df_cleaned[cols]

# converting (genre) json column to normal string column
# Replacing null values with '{}'
df_cleaned['genres'] = df_cleaned['genres'].replace(np.nan,'{}',regex = True)
df_cleaned['genres'] = pd.DataFrame(df_cleaned['genres'].apply(eval))
# dividing all genres in a cell into separate cols/series, concating it to main df & then dropping the original "genres" column from df
df_cleaned = pd.concat([df_cleaned.drop(['genres'], axis=1), df_cleaned['genres'].apply(pd.Series)], axis=1)
# Removing all columns except the major genre type for each movie
df_cleaned.drop(df_cleaned.iloc[:, 15:], inplace = True, axis = 1)
# creating separate series for "id" & "name" and concating it to main df
df_cleaned = pd.concat([df_cleaned.drop([0], axis=1), df_cleaned[0].apply(pd.Series)], axis=1)
df_cleaned.drop(df_cleaned.iloc[:, 14:16], inplace = True, axis = 1)     # dropping extraneous cols
df_cleaned.rename(columns = {'name' : 'Genre'}, inplace = True)   # renaming col
df_cleaned = df_cleaned[~df_cleaned['Genre'].isnull()] # removing null containing rows



# rearranging columns of dataframe
cols = df_cleaned.columns.tolist()
# Setting Production_companies as last col for easier manipulation
cols = ['budget', 'imdb_id', 'popularity', 'original_language', 'release_date', 'revenue', 'runtime', 'title', 'vote_average', 'vote_count', 'status', 'New_status', 'Genre', 'production_companies']
df_cleaned = df_cleaned[cols]

# converting (production_companies) json column to normal string column
# Replacing null values with '{}'
df_cleaned['production_companies'] = df_cleaned['production_companies'].replace(np.nan,'{}',regex = True)
# Converting Strings to Dictionaries as it have multiple production companies in json format
df_cleaned['production_companies'] = pd.DataFrame(df_cleaned['production_companies'].apply(eval))
# Dividing all production companies into separate cols, concatenating these to the main df and dropping the original 'production companies' col
df_cleaned = pd.concat([df_cleaned.drop(['production_companies'], axis=1), df_cleaned['production_companies'].apply(pd.Series)], axis=1)
# Removing all production companies cols except major production company
df_cleaned.drop(df_cleaned.iloc[:, 14:], inplace = True, axis = 1)
# creating separate series for "name" & "id" and concating it to main df
df_cleaned = pd.concat([df_cleaned.drop([0], axis=1), df_cleaned[0].apply(pd.Series)], axis=1)
# dropping unnecessary cols
df_cleaned.drop(df_cleaned.iloc[:, 13:15], inplace = True, axis = 1)
# renaming newly created col
df_cleaned.rename(columns = {'name' : 'Production_Company'}, inplace = True)
df_cleaned = df_cleaned[~df_cleaned['Production_Company'].isnull()]
len(df_cleaned.Production_Company.unique())


# Adding Director col using imdb files
dir_id_imdb = pd.read_csv(r'C:\Users\Madhuri Yadav\PycharmProjects\Final-Project-Group8\Code\title_crew.tsv', sep='\t')
merged_inner = pd.merge(left=df_cleaned,right=dir_id_imdb, left_on='imdb_id', right_on='tconst')
dir_name_imdb = pd.read_csv(r'C:\Users\Madhuri Yadav\PycharmProjects\Final-Project-Group8\Code\name_basics.tsv', sep='\t')
merged_inner = pd.merge(left=merged_inner,right=dir_name_imdb, left_on='directors', right_on='nconst')
merged_inner = merged_inner.drop(["tconst", "directors", "nconst"], axis=1)     # removing irrelevant cols
merged_inner.rename(columns = {'primaryName' : 'Director'}, inplace = True)


# Adding Avg_ratings & Total votes cols using imdb files
ratings_imdb = pd.read_csv(r'C:\Users\Madhuri Yadav\PycharmProjects\Final-Project-Group8\Code\title_ratings.tsv', sep='\t')
merged_inner = pd.merge(left=merged_inner,right=ratings_imdb, left_on='imdb_id', right_on='tconst')
merged_inner = merged_inner.drop(["tconst", "vote_average", "vote_count"], axis=1)     # removing old vote_avg/count cols

# Adding Movie release year column from imdb file
releaseYr_imdb = pd.read_csv(r'C:\Users\Madhuri Yadav\PycharmProjects\Final-Project-Group8\Code\title_year.tsv', sep='\t')
merged_inner = pd.merge(left=merged_inner,right=releaseYr_imdb, left_on='imdb_id', right_on='tconst')
merged_inner = merged_inner.drop(["tconst"], axis=1)
cols = merged_inner.columns.tolist()

#Extracting Month from release date
merged_inner['release_date_temp'] = pd.to_datetime(merged_inner['release_date'],format='%Y-%m-%d', errors='coerce')  #Converting string to datetime
merged_inner['release_month'] = pd.to_datetime(merged_inner['release_date_temp']).dt.month #extracting month from datetime(Releasedate) column
#df_cleaned['release_month'] = pd.to_numeric(df_cleaned['release_month'],errors='coerce') #converting float to int
merged_inner['release_month'] = merged_inner['release_month'].astype('category')
print(merged_inner.dtypes)
merged_inner = merged_inner.drop(['release_date_temp'], axis=1)

# Setting StartYear col beside release_date col
cols = ['budget', 'imdb_id', 'popularity', 'release_date', 'startYear', 'release_month', 'revenue', 'runtime', 'title', 'Genre', 'Production_Company', 'Director', 'averageRating', 'numVotes', 'original_language','status', 'New_status',]
merged_inner = merged_inner[cols]
merged_inner["startYear"].min()

len(merged_inner.Director.unique())     # 1173


# finding missing values
# a = merged_inner.isnull().sum()           # returns 0 for each column meaning no missing values

merged_inner.dtypes       # release_date is of object (i.e. string data type) instead of datetime
merged_inner['release_date'] =  pd.to_datetime(merged_inner['release_date'])    # converting release_date to datetime object
merged_inner['startYear'] = merged_inner['startYear'].astype(str).astype(int)     # converting startYear to int instead of object

len(merged_inner)    # 2222

# Removing Duplicates
merged_inner.drop_duplicates(inplace = True)     # no duplicates btw
#
# merged_inner.to_csv(r"Cleaned_df.csv", index=None, header=True)

# =================================================================
# EDA
# =================================================================

summary = merged_inner.describe()

# dependent variable
ax = sns.countplot(merged_inner["New_status"])
ax.set(xlabel ='Labels', ylabel ='Frequency')
plt.title("Target Variable",fontsize=20)
plt.show()


# status column
max_profit = merged_inner["status"].max()    # 653 times
max_profit_movie = merged_inner.loc[merged_inner['status'] == max_profit]   # The way of the dragon (director Bruce Lee)

ax = sns.distplot(merged_inner["status"], bins=500, kde=False)
# control x and y limits
ax.set(xlabel ='Ratio', ylabel ='Frequency')
plt.title("Revenue/Budget Ratio",fontsize=20)
plt.ylim(0, 700)
plt.xlim(-1, 50)
plt.show()

# Getting "Not Normal results" p<0.05
# stat, p = shapiro(merged_inner["status"])
# print('Statistics=%.3f, p=%.3f' % (stat, p))

#1.  independent variable Year
merged_inner["startYear"].min()     # 1921
merged_inner["startYear"].max()     # 2017

decades = []
for each in merged_inner["startYear"]:
    decade = int(np.floor(each / 10) * 10)
    decades.append(decade)

ax = sns.countplot(decades)
ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
ax.set(xlabel ='Decades', ylabel ='Frequency')
plt.title("Movie Count by Decades",fontsize=20)
plt.show()


# 2. independent variable Runtime
ax = sns.distplot(merged_inner["runtime"])
ax.set(xlabel ='Duration in Minutes', ylabel ='Frequency')
plt.title("Movie Runtime",fontsize=20)
plt.show()


# 3. independent variable Vote Average
ax = sns.distplot(merged_inner["averageRating"])
ax.set(xlabel ='Average Rating of a movie', ylabel ='Frequency')
plt.title("Movie Rating",fontsize=20)
plt.show()

max_rating_movie = merged_inner.loc[merged_inner['averageRating'] == 9.3]   # The Shawshank Redemption

# 4. independent variable Vote Count
ax = sns.distplot(merged_inner["numVotes"])
ax.set(xlabel ='Vote Distribution', ylabel ='Frequency')
plt.title("Vote Count",fontsize=20)
plt.show()

max_vote_movie = merged_inner.loc[merged_inner['numVotes'] == 2162821]   # The Shawshank Redemption

# 5. Number of movies per Genre
# a = merged_inner["Genre"].unique()    # 18
ax = sns.countplot(merged_inner["Genre"])
ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
ax.set(xlabel ='Genre', ylabel ='Frequency')
plt.title("Movie Count by Genre",fontsize=20)
plt.show()


# 6. Movie Budget
ax = sns.distplot(merged_inner["budget"])
# ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
ax.set(xlabel ='Budget', ylabel ='Frequency')
xlabels = ['{:,.2f}'.format(x) + 'M' for x in ax.get_xticks()/1000000]
ax.set_xticklabels(xlabels)
plt.title("Movie Budget",fontsize=20)
plt.show()


# Correlation heatmap bw numerical cols
num_cols = merged_inner[['budget', 'startYear', 'revenue', 'runtime', 'popularity', 'averageRating', 'numVotes','status']]
# removing redundant upper half of heat map
mask = np.zeros(num_cols.corr().shape, dtype=bool)
mask[np.triu_indices(len(mask))] = True
sns.heatmap(num_cols.corr(), annot=True, vmin = -1, vmax = 1, center = 0, cmap = 'coolwarm', mask = mask)
plt.show()



#
# # Pair Plot
# df_x = df_cleaned[['budget','revenue','runtime','vote_average','vote_count','New_status']]
# sns.set(style = 'ticks')
# sns.pairplot(df_x, hue = 'New_status')
# plt.show()



# =================================================================
# Modeling
# =================================================================

# Spliting and encoding data
# split the dataset into input and target variables

X = merged_inner.loc[:,['runtime','averageRating','budget','Genre','Production_Company','release_month', 'popularity']]  #
y = merged_inner.loc[:,['New_status']]

scaler = MinMaxScaler()
X.loc[:,['runtime','averageRating','budget', 'popularity']]= scaler.fit_transform(X.loc[:,['runtime','averageRating','budget', 'popularity']])

# encloding the class with sklearn's LabelEncoder
le = LabelEncoder()
# fit and transform the class
y = le.fit_transform(y)
X = pd.get_dummies(X)


# split the dataset into train and test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
#print("X train: ", len(X_train))

# Over sampling
# RandomOverSampler (with random_state=0)
ros = RandomOverSampler(random_state=0)
X_train, y_train = ros.fit_sample(X_train, y_train)
print("after over sam X : ", len(X_train))
print("after over sam y : ", len(y_train))

# Decision Tree Gini
# perform training with giniIndex.
# creating the classifier object
clf_gini = DecisionTreeClassifier(criterion="gini", random_state=seed, min_samples_leaf=5)

# performing training
clf_gini.fit(X_train, y_train)

# predicton on test using gini
y_pred_gini = clf_gini.predict(X_test)

print("Classification Report For DT Gini: ")
print(classification_report(y_test,y_pred_gini))
print("Accuracy : ", accuracy_score(y_test, y_pred_gini.ravel()) * 100)

#Decision Tree Entropy
# perform training with Entropy.
# creating the classifier object
clf_entropy = DecisionTreeClassifier(criterion="entropy", random_state=seed, min_samples_leaf=5)

# performing training
clf_entropy.fit(X_train, y_train)

# predicton on test using gini
y_pred_entropy = clf_entropy.predict(X_test)

print("Classification Report for DT Entropy: ")
print(classification_report(y_test,y_pred_entropy.ravel()))
print("Accuracy : ", accuracy_score(y_test, y_pred_entropy) * 100)


#Random Forest
# specify random forest classifier
clf_rf = RandomForestClassifier(n_estimators=100,random_state=seed)

# perform training
clf_rf.fit(X_train, y_train)

# predicton on test using all features
y_pred_rf = clf_rf.predict(X_test)
y_pred_score = clf_rf.predict_proba(X_test)

print("Classification Report for DT Entropy: ")
print(classification_report(y_test,y_pred_rf))
print("Accuracy : ", accuracy_score(y_test, y_pred_rf) * 100)

#Applying ADA Boosting
classifier = AdaBoostClassifier(RandomForestClassifier(n_estimators=100,random_state=seed),n_estimators=100,random_state=seed)
classifier.fit(X_train, y_train)

# predicton on test using all features
y_pred_boost = classifier.predict(X_test)

print("Classification Report for boosting: ")
print(classification_report(y_test,y_pred_boost))
print("Accuracy : ", accuracy_score(y_test, y_pred_boost) * 100)


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

print("Classification Report for SVM:")
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
print("Classification Report for KNN: ")
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

print("Classification Report for NB: ")
print(classification_report(y_test,y_pred_nb))
print("\n")

print("Accuracy : ", accuracy_score(y_test, y_pred_nb) * 100)
print("\n")

#Ensembling
final_pred = np.array([])
for i in range(0,len(X_test)):
    final_pred = np.append(final_pred, mode([y_pred_rf[i], y_pred_gini[i], y_pred_entropy[i]]))

print("*"*50)
print("Accuracy DT Gini : ", accuracy_score(y_test, y_pred_gini) * 100)
print("Accuracy DT Entropy: ", accuracy_score(y_test, y_pred_entropy) * 100)
print("Accuracy SVM: ", accuracy_score(y_test, y_pred_svm) * 100)
print("Accuracy RF: ", accuracy_score(y_test, y_pred_rf) * 100)
print("Accuracy KNN: ", accuracy_score(y_test, y_pred_knn) * 100)
print("Accuracy NB: ", accuracy_score(y_test, y_pred_nb) * 100)
print("Accuracy Bagging with Mode method: ", accuracy_score(y_test, final_pred) * 100)
print("Accuracy ADA: ", accuracy_score(y_test, y_pred_boost) * 100)
print("*"*50)

#Printing results for our best model
print("ROC_AUC : ", roc_auc_score(y_test, y_pred_boost) * 100)
print("Accuracy K: ", cohen_kappa_score(y_test, y_pred_boost)* 100)

# ROC Graph
y_pred_score = classifier.predict_proba(X_test)
preds = y_pred_score[:,1]
fpr, tpr, threshold = metrics.roc_curve(y_test, preds)
roc_auc = metrics.auc(fpr, tpr)

# method I: plt
import matplotlib.pyplot as plt
plt.title('Receiver Operating Characteristic')
plt.plot(fpr, tpr, 'b', label = 'AUC = %0.2f' % roc_auc)
plt.legend(loc = 'lower right')
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0, 1])
plt.ylim([0, 1])
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.show()

# confusion matrix for AdaBoosting
conf_matrix = confusion_matrix(y_test, y_pred_boost)
class_names = merged_inner['New_status'].unique()

df_cm = pd.DataFrame(conf_matrix, index=class_names, columns=class_names )

plt.figure(figsize=(5,5))

hm = sns.heatmap(df_cm, cbar=False, annot=True, square=True, fmt='d', annot_kws={'size': 20}, yticklabels=df_cm.columns, xticklabels=df_cm.columns)

hm.yaxis.set_ticklabels(hm.yaxis.get_ticklabels(), rotation=0, ha='right', fontsize=20)
hm.xaxis.set_ticklabels(hm.xaxis.get_ticklabels(), rotation=0, ha='right', fontsize=20)
print("aaa")
plt.ylabel('True label',fontsize=20)
plt.xlabel('Predicted label',fontsize=20)
plt.title("Confusion Metrix AdaBoost Model")
plt.tight_layout()
plt.show()


# =================================================================
# GUI
# =================================================================


# class CanvasWindow(QMainWindow):
#     #::----------------------------------
#     # Creates a canvas containing the plot for the initial analysis
#     #;;----------------------------------
#     def __init__(self, parent=None):
#         super(CanvasWindow, self).__init__(parent)
#
#         self.left = 200
#         self.top = 200
#         self.Title = 'Distribution'
#         self.width = 500
#         self.height = 500
#         self.initUI()
#
#     def initUI(self):
#
#         self.setWindowTitle(self.Title)
#         self.setStyleSheet(font_size_window)
#
#         self.setGeometry(self.left, self.top, self.width, self.height)
#
#         self.m = PlotCanvas(self, width=5, height=4)
#         self.m.move(0, 30)
#
# class App(QMainWindow):
#     #::-------------------------------------------------------
#     # This class creates all the elements of the application
#     #::-------------------------------------------------------
#
#     def __init__(self):
#         super().__init__()
#         self.left = 100
#         self.top = 100
#         self.Title = 'Predicting Movie Success/Failure via ML'
#         self.width = 500
#         self.height = 300
#         self.initUI()
#
#     def initUI(self):
#         #::-------------------------------------------------
#         # Creates the manu and the items
#         #::-------------------------------------------------
#         self.setWindowTitle(self.Title)
#         self.setGeometry(self.left, self.top, self.width, self.height)
#
#         #::-----------------------------
#         # Create the menu bar
#         # and three items for the menu, File, EDA Analysis and ML Models
#         #::-----------------------------
#         mainMenu = self.menuBar()
#         mainMenu.setStyleSheet('background-color: lightblue')
#
#         fileMenu = mainMenu.addMenu('File')
#         EDAMenu = mainMenu.addMenu('EDA Analysis')
#         MLModelMenu = mainMenu.addMenu('ML Models')
#
#         #::--------------------------------------
#         # Exit application
#         # Creates the actions for the fileMenu item
#         #::--------------------------------------
#
#         exitButton = QAction(QIcon('enter.png'), 'Exit', self)
#         exitButton.setShortcut('Ctrl+Q')
#         exitButton.setStatusTip('Exit application')
#         exitButton.triggered.connect(self.close)
#
#         fileMenu.addAction(exitButton)
#
#         #::----------------------------------------
#         # EDA analysis
#         # Creates the actions for the EDA Analysis item
#         # Initial Assesment : Histogram about the level of happiness in 2017
#         # Happiness Final : Presents the correlation between the index of happiness and a feature from the datasets.
#         # Correlation Plot : Correlation plot using all the dims in the datasets
#         #::----------------------------------------
#
#         EDA1Button = QAction(QIcon('analysis.png'),'Initial Assesment', self)
#         EDA1Button.setStatusTip('Presents the initial datasets')
#         EDA1Button.triggered.connect(self.EDA1)
#         EDAMenu.addAction(EDA1Button)
#
#         # EDA2Button = QAction(QIcon('analysis.png'), 'Happiness Final', self)
#         # EDA2Button.setStatusTip('Final Happiness Graph')
#         # EDA2Button.triggered.connect(self.EDA2)
#         # EDAMenu.addAction(EDA2Button)
#
#         EDA4Button = QAction(QIcon('analysis.png'), 'Correlation Plot', self)
#         EDA4Button.setStatusTip('Features Correlation Plot')
#         EDA4Button.triggered.connect(self.EDA4)
#         EDAMenu.addAction(EDA4Button)
#
#         #::--------------------------------------------------
#         # ML Models for prediction
#         # There are two models
#         #       Decision Tree
#         #       Random Forest
#         #::--------------------------------------------------
#         # Decision Tree Model
#         #::--------------------------------------------------
#         MLModel1Button =  QAction(QIcon(), 'Decision Tree Entropy', self)
#         MLModel1Button.setStatusTip('ML algorithm with Entropy ')
#         MLModel1Button.triggered.connect(self.MLDT)
#
#         #::------------------------------------------------------
#         # Random Forest Classifier
#         #::------------------------------------------------------
#         MLModel2Button = QAction(QIcon(), 'Random Forest Classifier', self)
#         MLModel2Button.setStatusTip('Random Forest Classifier ')
#         MLModel2Button.triggered.connect(self.MLRF)
#
#         MLModelMenu.addAction(MLModel1Button)
#         MLModelMenu.addAction(MLModel2Button)
#
#         self.dialogs = list()
#
#     def EDA1(self):
#         #::------------------------------------------------------
#         # Creates the graph for number of movies per Genre
#
#         #::------------------------------------------------------
#         dialog = CanvasWindow(self)
#         dialog.m.plot()
#         dialog.m.ax.hist(df_cleaned['Genre'])
#         dialog.m.ax.set_title('Number of Movies per Genre')
#         dialog.m.ax.set_xlabel("Genres")
#         dialog.m.ax.set_ylabel("Frequency")
#         dialog.m.ax.grid(True)
#         dialog.m.draw()
#         self.dialogs.append(dialog)
#         dialog.show()
#
#
#     # def EDA2(self):
#     #     #::---------------------------------------------------------
#     #     # This function creates an instance of HappinessGraphs class
#     #     # This class creates a graph using the features in the dataset
#     #     # happiness vrs the score of happiness
#     #     #::---------------------------------------------------------
#     #     dialog = HappinessGraphs()
#     #     self.dialogs.append(dialog)
#     #     dialog.show()
#
#     def EDA4(self):
#         #::----------------------------------------------------------
#         # This function creates an instance of the CorrelationPlot class
#         #::----------------------------------------------------------
#         dialog = CorrelationPlot()
#         self.dialogs.append(dialog)
#         dialog.show()
#
#     def MLDT(self):
#         #::-----------------------------------------------------------
#         # This function creates an instance of the DecisionTree class
#         # This class presents a dashboard for a Decision Tree Algorithm
#         # using the happiness dataset
#         #::-----------------------------------------------------------
#         dialog = DecisionTree()
#         self.dialogs.append(dialog)
#         dialog.show()
#
#     def MLRF(self):
#         #::-------------------------------------------------------------
#         # This function creates an instance of the Random Forest Classifier Algorithm
#         # using the happiness dataset
#         #::-------------------------------------------------------------
#         dialog = RandomForest()
#         self.dialogs.append(dialog)
#         dialog.show()
#
# def main():
#     #::-------------------------------------------------
#     # Initiates the application
#     #::-------------------------------------------------
#     app = QApplication(sys.argv)
#     app.setStyle('Fusion')
#     ex = App()
#     ex.show()
#     sys.exit(app.exec_())
#
#
# def movie_prediction():
#     #::--------------------------------------------------
#     # Loads the dataset movies_metadata.csv ( Raw/Original dataset)
#     # Loads the dataset cleaned_df.csv
#     #::--------------------------------------------------
#
#     global final_movie
#     global features_list
#     global class_names
#
#     final_movie = pd.read_csv('Cleaned_df.csv')
#     features_list = df_cleaned.columns.tolist()
#     class_names = ['Success', 'Flop']
#
#
# if __name__ == '__main__':
#     #::------------------------------------
#     # First reads the data then calls for the application
#     #::------------------------------------
#     movie_prediction()
#     main()
#
#
