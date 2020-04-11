#!/usr/bin/env python3

'''
    https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide
'''

import datetime
import locale

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import AutoLocator

import pandas
import requests

import pylab

# 歐盟疾病管理署，COVID19 開放資料下載網頁: https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide
EU_COVID19_CSV = 'https://opendata.ecdc.europa.eu/covid19/casedistribution/csv'
COVID19_FILENAME = 'covid19.csv'

# G20 Industrial Countries
COUNTRIES = ('Russia', 'United_States_of_America', 'United_Kingdom', 'Japan', 'Germany', 'France',
        'India', 'China', 'Canada', 'Italy', 'Brazil', 'South_Africa', 'Mexico', 'Argentina',
        'Turkey', 'Saudi_Arabia', 'South_Korea', 'Indonesia', 'Australia')

# 歐洲國家 Countries in European.
'''
COUNTRIES = ('United_Kingdom', 'Spain', 'Germany', 'Italy', 'France', 'Austria', 'Poland',
        'Portugal', 'Sweden', 'Switzerland', 'Finland', 'Greece', 'Greenland', 'Iceland',
        'Denmark', 'Belgium', 'Netherlands')
'''


# 台灣周圍 Countries around Taiwan
COUNTRIES = ('China', 'Japan', 'Taiwan', 'Vietnam', 'South_Korea', 'Thailand', 'Philippines', 'New_Zealand')

# 中東國家，中亞 Middle East and Central Asia
# COUNTRIES = ('Saudi_Arabia', 'Iraq', 'Iran', 'Turkey', 'Israel')

# 非洲國家 Countries around Africa
'''
COUNTRIES = ('Eswatini', 'Uganda', 'Egypt', 'Congo', 'Democratic_Republic_of_the_Congo',
        'Ethiopia', 'Ghana', 'Kenya')
'''

# 人口較多的國家 Countries with the most population according to Wikipedia.
'''
COUNTRIES = ('Russia', 'Canada', 'United_States_of_America', 'Mexico', 'United_Kingdom', 'Japan',
        'Germany', 'Italy', 'Israel', 'France', 'Australia', 'Brazil', 'India',  'Nigeria',
        'Saudi_Arabia', 'China', 'Indonesia', 'Vietnam', 'South_Korea', 'Malaysia', 'Singapore',
        'Philippines', 'Pakistan', 'Argentina', 'Thailand', 'Cambodia', 'Kenya', 'Turkey')
'''


class ReadCovid19:
    ANNOTATE_OFFSET = 10

    def __init__(self):
        self.csv_file = pandas.read_csv(COVID19_FILENAME, encoding='UTF-8', parse_dates=True,
                date_parser=pandas.io.date_converters.parse_date_time)

        self.csv_file = pandas.DataFrame(self.csv_file,
                columns=['dateRep', 'cases',  'deaths', 'year', 'month', 'day',
                    'countriesAndTerritories', 'geoId', 'countryterritoryCode'])

        last_us = self.csv_file[self.csv_file['geoId'] == 'US'].head(1)
        last_date = datetime.datetime(year=last_us.year, month=last_us.month, day=last_us.day)
        now = datetime.datetime.now()

        if (now - last_date).days > 1:
            self.update()

        # convert %d/%m/%Y datetime string to datetime object
        self.csv_file['dateRep'] = pandas.to_datetime(self.csv_file['dateRep'], format='%d/%m/%Y')

        # Original data is in datetime descending order, so we have to reverse it to ascending data order
        self.csv_file = self.csv_file.iloc[::-1]
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

        self.first_date = self.csv_file['dateRep'].min()
        self.last_date = self.csv_file['dateRep'].max()

    def update(self):
        try:
            res = requests.get(EU_COVID19_CSV, allow_redirects=True)

            if res.status_code != 200:
                return

            with open(COVID19_FILENAME, 'wb') as f:
                f.write(res.content)

            self.csv_file = pandas.read_csv(COVID19_FILENAME, encoding='UTF-8', parse_dates=True,
                    date_parser=pandas.io.date_converters.parse_date_time)

        except Exception as e:
            print("Tried to update csv file with errors: {}".format(e))

    def get_csv(self):
        return self.csv_file

    def head(self):
        print('\nhead')
        print(self.csv_file.head())
        print('\n')

    def tail(self):
        print('tail')
        print(self.csv_file.tail())
        print('\n')

    def count(self):
        print('count')
        print(self.csv_file.count())
        print('\n')

    def describe(self):
        print('describe')
        print(self.csv_file.describe())
        print('\n')

    def test(self):
        self.head()
        self.tail()
        self.count()
        self.describe()

    def show_indivisual_country_plot(self):
        for country in COUNTRIES:
            country_obj = self.csv_file[csv_obj['countriesAndTerritories'] == country]
            ax = country_obj.plot(kind='line', style='--o',  x='dateRep', y=['cases', 'deaths'], title=country, figsize=(14, 6))

            max_cases = country_obj[country_obj['cases'] == country_obj['cases'].max()]
            max_deaths = country_obj[country_obj['deaths'] == country_obj['deaths'].max()]

            ax.annotate('{:,}'.format(max_cases.cases.values[0]), xy=(max_cases.dateRep.values[0], max_cases.cases.values[0] + self.ANNOTATE_OFFSET))
            ax.annotate('{:,}'.format(max_deaths.deaths.values[0]), xy=(max_deaths.dateRep.values[0], max_deaths.deaths.values[0] + self.ANNOTATE_OFFSET))

            xlabel = "Date: {} ~ {} (Month/Day)".format(self.first_date.strftime('%Y/%m/%d'), self.last_date.strftime('%Y/%m/%d'))
            ax.set(xlabel=xlabel, ylabel="Number of People", title=country)
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
            ax.xaxis.set_major_locator(AutoLocator())
            ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
            for label in ax.get_xticklabels():
                label.set_horizontalalignment('right')

            pylab.show()

    def show_global_plot(self):
        # Daily groupby sum of global cases and deaths
        global_country_frames_sum = self.csv_file.groupby('dateRep').sum()

        max_cases = global_country_frames_sum[global_country_frames_sum['cases'] == global_country_frames_sum['cases'].max()]
        max_deaths = global_country_frames_sum[global_country_frames_sum['deaths'] == global_country_frames_sum['deaths'].max()]

        ax = global_country_frames_sum.plot(kind='line', style='--o', y=['cases', 'deaths'], figsize=(14, 6))

        ax.annotate('{:,}'.format(max_cases.cases.values[0]), xy=(max_cases.index.values[0], max_cases.cases.values[0] + self.ANNOTATE_OFFSET))
        ax.annotate('{:,}'.format(max_deaths.deaths.values[0]), xy=(max_deaths.index.values[0], max_deaths.deaths.values[0] + self.ANNOTATE_OFFSET))

        ax.set(xlabel="Date: (Month/Day)", ylabel="Number of People", title='Global Total cases/deaths')
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
        ax.xaxis.set_major_locator(AutoLocator())
        ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        for label in ax.get_xticklabels():
            label.set_horizontalalignment('right')
        pylab.show()

        # Daily groupby cumulative sum of global cases and deaths
        global_country_frames_sum['cases_sum'] = global_country_frames_sum['cases'].cumsum()
        global_country_frames_sum['deaths_sum'] = global_country_frames_sum['deaths'].cumsum()

        max_cases = global_country_frames_sum[global_country_frames_sum['cases_sum'] == global_country_frames_sum['cases_sum'].max()]
        max_deaths = global_country_frames_sum[global_country_frames_sum['deaths_sum'] == global_country_frames_sum['deaths_sum'].max()]

        ax = global_country_frames_sum.plot(kind='line', style='--o', y=['cases_sum', 'deaths_sum'], figsize=(14, 6))

        ax.annotate('{:,}'.format(max_cases.cases_sum.values[0]), xy=(max_cases.index.values[0], max_cases.cases_sum.values[0] + self.ANNOTATE_OFFSET))
        ax.annotate('{:,}'.format(max_deaths.deaths_sum.values[0]), xy=(max_deaths.index.values[0], max_deaths.deaths_sum.values[0] + self.ANNOTATE_OFFSET))

        ax.set(xlabel="Date: (Month/Day)", ylabel="Number of People", title='Global Accumulative sum cases/deaths')
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
        ax.xaxis.set_major_locator(AutoLocator())
        ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        for label in ax.get_xticklabels():
            label.set_horizontalalignment('right')
        pylab.show()

    def show_plot(self):
        '''
            Use matplotlib with pandas bindings to plot charts.
        '''
        self.show_indivisual_country_plot()
        self.show_global_plot()

    def show_numbers(self):
        countries = self.csv_file['geoId'].nunique()

        print('總共 {} 個國家有武漢肺炎確診者。'.format(countries))

        total_cases = self.csv_file.cases.sum()
        total_deaths = self.csv_file.deaths.sum()
        print('全球確診病例數 = {:,}'.format(total_cases))
        print('全球確診病例死亡數 = {:,}'.format(total_deaths))
        print('全球確診病例死亡率 = {} %'.format(round((total_deaths / total_cases) * 100, 2)))

        for country in COUNTRIES:
            confirmed_cases = self.csv_file[self.csv_file['countriesAndTerritories'] == country].cases.sum()
            print('\n{} 確診病例數 = {:,}'.format(country, confirmed_cases))

            confirmed_deaths = self.csv_file[self.csv_file['countriesAndTerritories'] == country].deaths.sum()
            print('{} 確診死亡人數 = {:,}'.format(country, confirmed_deaths))
            print('{} 確診死亡率 = {} %\n'.format(country, round(confirmed_deaths / confirmed_cases, 4)))

    def show_last_date(self):
        print(self.last_date.strftime('公元 %Y 年 %m 月 %d 日'))

    def show(self):
        self.show_plot()
        self.show_last_date()
        self.show_numbers()


if __name__ == '__main__':
    covid = ReadCovid19()
    csv_obj = covid.get_csv()
    print([c for c in csv_obj['countriesAndTerritories'].unique()])
    covid.show()
