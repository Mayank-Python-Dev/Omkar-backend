from django.core.management.base import BaseCommand
import calendar, pandas as pd
from django.shortcuts import render
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
from django.db.models.functions import ExtractMonth, ExtractYear
from django_pandas.io import read_frame
from contract.models import Rental as ContractRental
import matplotlib.pyplot as plt, base64
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.core.mail import send_mail

class Command(BaseCommand):
    help = "This command is for running cronjob ..."

    def handle(self, *args, **kwargs):
        get_today_date = date.today() + relativedelta(months=1,day=1)
        get_next_year_date = get_today_date + relativedelta(months=11,day=31)
        get_contracts = ContractRental.objects.filter(gala__warehouse__company__name="Omkar",
            agreement_valid_end_date__range=[get_today_date.replace(day=1),get_next_year_date]
        ).annotate(
            month = ExtractMonth('agreement_valid_end_date'),year = ExtractYear('agreement_valid_end_date')
        ).values("month","gala__gala_area_size","gala__gala_number")
        get_contracts_df = read_frame(get_contracts)
        dates = pd.date_range(str(get_today_date.replace(day=1)),str(get_next_year_date),freq='M')
        df = pd.DataFrame()
        df['dates'] = dates
        df['month_name'] = df['dates'].dt.strftime('%b')
        df['month'] = df['dates'].dt.strftime('%m')
        df['month_year'] = df['dates'].dt.strftime('%Y')
        df['month'] = df['month'].astype(int)
        new_df = pd.merge(df, get_contracts_df, on='month',how="left")
        new_df = new_df.groupby(['month', 'month_year','month_name'], as_index=False).agg(free_gala_area_size=('gala__gala_area_size', 'sum'), gala_count=('gala__gala_number', 'count')).sort_values('month_year', ascending=True)
        new_df.fillna(0,inplace=True)
        new_df['month_year_name'] = new_df['month_name'] + ", " + new_df['month_year']
        new_df['message'] = "Count" + " : " + new_df['gala_count'].astype(str)
        get_unique_year = new_df['month_year'].unique()
        if len(get_unique_year) == 2:
            get_year = get_unique_year[0] + " - " +  get_unique_year[1]
        else:
            get_year = get_unique_year[0]
        colors = ["#ff638480","#36a2eb80","#ffce5680","#4bc0c080","#9966ff80","#ff9f4080","#98df58","#f9dd51","#ec6464","#24dcd4","#ec64a5","#3090f0"]
        years_list = new_df['month_year_name'].tolist()
        gala_free_area_list = new_df['free_gala_area_size'].tolist()
        fig = plt.figure()
        ax = fig.add_axes([0,0,1,1])
        c = ["#ff638480","#36a2eb80","#ffce5680","#4bc0c080","#9966ff80","#ff9f4080","#98df58","#f9dd51","#ec6464","#24dcd4","#ec64a5","#3090f0"]
        ax.bar(years_list,gala_free_area_list,color = c)
        ax.set_title(f'Gala Free Area Size ({get_year})')
        # addlabels(years_list, new_df['message'].to_list())
        plt.xticks(rotation=75)
        ax.bar_label(ax.containers[0],label_type='center', color='black',rotation=90, fontsize=9, padding=1)
        # ax.bar_label(bar_container,labels=new_df['message'].tolist(), label_type='center', color='black',rotation=90, fontsize=9, padding=1)
        plt.grid(color='grey', linewidth=0.2, axis='both',linestyle='-',)
        plt.savefig('media/bar-chart/bar_chart.pdf', dpi=120, format='pdf', bbox_inches='tight')
        # plt.savefig('media/bar-chart/barchart.png',bbox_inches='tight',dpi=120,format='png')
        plt.show()
        # pdf_file = model_instance.file  # <- here I am accessing the file attribute, which is a FileField
        # message = EmailMessage(
        #     "Bar Chart",
        #     "Hello world!"
        #     "kapilyadav@infograins.com",
        #     ["mayank.infograins@gmail.com"],
        # )
        # message.attach("media/bar-chart/bar_chart.pdf","application/pdf")
        # message.send(fail_silently=False) 
        start_date = datetime.strptime(str(get_today_date),"%Y-%m-%d").strftime("%d %B %Y")
        end_date = datetime.strptime(str(get_next_year_date),"%Y-%m-%d").strftime("%d %B %Y")
        message = f"Statistics from {start_date} to {end_date}"

        email = EmailMessage(
            'Statistics Bar Chart', message, 'kapilyadav@infograins.com', ['mayank.infograins@gmail.com'])
        email.attach_file('media/bar-chart/bar_chart.pdf')
        email.send()
        