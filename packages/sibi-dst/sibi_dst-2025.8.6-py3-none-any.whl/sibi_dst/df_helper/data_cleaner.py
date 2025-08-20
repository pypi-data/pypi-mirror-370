import re
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import dask.dataframe as dd
from dask_ml.preprocessing import OneHotEncoder, LabelEncoder
import nltk

class DataCleaner:
    def __init__(self, dataframe):
        self.original_df = dataframe
        self.df = dataframe.copy()
        self.duplicates_df = None

    def handle_missing_values(self, strategy='mean'):
        if strategy == 'mean':
            self.df = self.df.fillna(self.df.mean())
        elif strategy == 'median':
            self.df = self.df.fillna(self.df.median())
        elif strategy == 'mode':
            self.df = self.df.fillna(self.df.mode().iloc[0])
        elif strategy == 'drop':
            self.df = self.df.dropna()
        return self

    def identify_duplicates(self, subset=None):
        self.duplicates_df = self.df.map_partitions(lambda df: df[df.duplicated(subset=subset, keep=False)])
        return self.duplicates_df

    def remove_duplicates(self):
        if self.duplicates_df is not None:
            self.df = self.df[~self.df.index.isin(self.duplicates_df.index)]
        return self

    def validate_date_fields(self, date_columns=None):
        if date_columns is None:
            date_columns = self.df.select_dtypes(include=['datetime', 'datetime64[ns]', 'datetime64[ns, UTC]']).columns
        for col in date_columns:
            print('Validating date field: ', col)
            self.df[col] = dd.to_datetime(self.df[col], errors='coerce')
        return self

    def clean_text(self, text_columns=None, language='english'):
        nltk.download('stopwords')
        stop_words = set(stopwords.words(language))
        stemmer = SnowballStemmer(language)

        def clean_text(text):
            if isinstance(text, str):
                text = text.strip().lower()  # Remove leading/trailing whitespace and convert to lowercase
                text = re.sub(r'[^\w\s]', '', text)  # Remove special characters and punctuation
                words = text.split()
                words = [word for word in words if word not in stop_words]  # Remove stop words
                words = [stemmer.stem(word) for word in words]  # Apply stemming
                return ' '.join(words)
            return text

        if text_columns is None:
            text_columns = self.df.select_dtypes(include=['object', 'string']).columns
            text_columns = [col for col in text_columns if self.df[col].dtype != 'bool']

        for col in text_columns:
            print('Cleaning text field: ', col)
            self.df[col] = self.df[col].map(clean_text, meta=('cleaned_text', 'object'))
        return self

    def validate_numeric_fields(self, int_columns=None, float_columns=None):
        if int_columns is None:
            int_columns = self.df.select_dtypes(include=['int64', 'int32']).columns
        if float_columns is None:
            float_columns = self.df.select_dtypes(include=['float64', 'float32']).columns

        for col in int_columns:
            print('Validating integer field: ', col)
            self.df[col] = dd.to_numeric(self.df[col], errors='coerce', downcast='integer')

        for col in float_columns:
            print('Validating float field: ', col)
            self.df[col] = dd.to_numeric(self.df[col], errors='coerce', downcast='float')

        return self

    def detect_categorical_columns(self, threshold=0.05):
        """
        Detect columns that can be converted to 'category' dtype.

        Parameters:
        threshold (float): The maximum ratio of unique values to total values for a column to be considered categorical.

        Returns:
        List of column names that can be converted to 'category' dtype.
        """
        categorical_columns = []

        def unique_ratio(partition, col):
            return partition[col].nunique() / len(partition)

        for col in self.df.columns:
            print("Detecting categorical columns: ", col)
            unique_ratios = self.df.map_partitions(unique_ratio, col=col).compute()
            overall_unique_ratio = unique_ratios.sum() / len(self.df)
            if overall_unique_ratio < threshold:
                print(f'Column {col} is categorical')
                categorical_columns.append(col)

        return categorical_columns

    def handle_categorical_variables(self, columns=None, method='onehot', threshold=0.05):
        if columns is None:
            columns = self.detect_categorical_columns(threshold)

        if method == 'onehot':
            for col in columns:
                self.df[col] = self.df[col].astype('category')
            encoder = OneHotEncoder(sparse_output=False)
            self.df = encoder.fit_transform(self.df)
        elif method == 'label':
            encoder = LabelEncoder()
            for col in columns:
                self.df[col] = encoder.fit_transform(self.df[col])
        return self

    def analyze_dtypes(self):
        return self.df.dtypes

    def get_cleaned_dataframe(self):
        return self.df

    def get_original_dataframe(self):
        return self.original_df

    def get_duplicates_dataframe(self):
        return self.duplicates_df