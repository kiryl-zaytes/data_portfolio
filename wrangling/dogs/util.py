import pandas as pd
import numpy as np
import re


class Utils:
    @staticmethod
    def get_intersection(df1, df2, on):
        """
        :param df1: data set
        :param df2: data set
        :param on: feature to find intersection on two data frames
        :return: series with common data
        """
        return pd.Series(list(set(df1[on]) & set(df2[on])))

    @staticmethod
    def check_url(urls):
        """
        :param urls: column with urls
        :return: filtered out all url not satisfied to regex.
        """
        p = re.compile("https://twitter.com/dog_rates/status/\d+/photo/\d")
        url_list = str(urls).split(',')
        url_list = set(url_list)
        filtered_urls = [u for u in url_list if re.match(p, u) is not None]
        return ''.join(filtered_urls)

    @staticmethod
    def concat_dropna(df, feature, column_range, new_type):
        """

        :param df: data frame
        :param feature: to be created instead of range of columns
        :param column_range: columns to be merged in one feature
        :param new_type: type of newly created column
        :return:
        """
        df[feature] = df.loc[:, column_range].apply(lambda x: ''.join(x.dropna().tolist()), 1)
        df[feature].replace('', np.nan, inplace=True)
        df.type = df.type.astype(new_type)

    @staticmethod
    def drop_inplace(df, columns):
        """
        :param df: data frame
        :param columns: columns/features to drop
        :return: changed set
        """
        df.drop(columns, axis=1, inplace=True)

    @staticmethod
    def drop_index_by_condition(df, df_to_drop):
        """
        :param df: data frame
        :param df_to_drop: set of rows to drop
        :return: changed data set
        """
        df.drop(df_to_drop.index, inplace=True)

    @staticmethod
    def to_datetime(df, feature):
        """
        To cut ending 00000 and convert to datetime format
        :param df: data frame
        :param feature: column to be converted to dt
        :return: df with applied type change
        """
        df[feature] = df[feature].str[:-6]
        df[feature] = pd.to_datetime(df[feature])
        return df

    @staticmethod
    def direct_cell_change(df, feature, row, values):
        """
        :param df: data frame
        :param feature: column name
        :param row: rows to change value in
        :param values: new values for provided rows
        :return:
        """
        for i, r in enumerate(row):
            df.at[row[i], feature] = values[i]

    @staticmethod
    def extract_desc(df):
        """
        :param df: data frame
        :return: data frame with text extracted from column text and applied back to column
        """
        desc = df.text.str.extract('(?P<desc>.*[.,?! ])\s?(?P<rating>\d+/\d+)?\s(?P<text_link>.*[^https://])',
                                   expand=True)
        desc['desc'] = desc['desc'].str.strip()
        df['text'] = desc['desc']

    @staticmethod
    def extract_named(df, name):
        """
        :param df: data frame
        :param name: name value to search rows to extract real names from
        :return: data frame with found names applied to name column
        """
        a_names = df[df.name == name][['text', 'name']]
        a_names = a_names[a_names['text'].str.contains('named')]
        a_names.name = a_names.text.str.extract('(?:This is a )(\w+ .*)(?:named) (?P<Name>\w+)', expand=True).Name
        for ind in a_names.index:
            df.at[ind, 'name'] = a_names.loc[ind][1]

    @staticmethod
    def string_prettify(df, feature):
        """
        :param df:
        :param feature: string feature
        :return: capitalized values in data set column
        """
        return df[feature].str.lower().str.capitalize()

    @staticmethod
    def to_nan(df, feature, values):
        """
        :param feature: column to look values within
        :param values: values to drop
        :return: changed df
        """
        return df[feature].replace(values, np.nan)

    @staticmethod
    def split_capitalize(x):
        """
        :param x: row to be split by (_)
        :return: capitalized first letter in each word
        """
        l = x.split('_')
        r = ''
        for s in l:
            r += s.capitalize() + ' '
        return r
