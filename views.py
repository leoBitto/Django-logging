from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
import plotly.graph_objs as go
from django.db.models import Count
from .models import AccessLog, ErrorLog
from django.db.models import Count
import pandas as pd
import numpy as np
from .forms import ConsentForm
from django.utils import timezone

class ConsentView(View):
    template_name = 'logging_app/consent.html'

    def get(self, request):
        form = ConsentForm()  # Crea un'istanza del form di consenso
        return render(request, self.template_name, {'form': form})  # Passa il form al template

    def post(self, request):
        form = ConsentForm(request.POST)  # Crea un'istanza del form con i dati inviati dal POST
        if form.is_valid():  # Controlla se il form è valido
            if form.cleaned_data['consent_given']:  # Verifica se il consenso è stato dato
                ip_address = request.META.get('REMOTE_ADDR', '')
                access_log = AccessLog(
                    ip_address=ip_address,
                    timestamp=timezone.now(),
                    request_path=request.path,
                    request_method=request.method,
                    response_code=200  # Codice di risposta di successo
                )
                access_log.save()
                return redirect('website:home')  # Reindirizza alla homepage se il consenso è stato dato
            else:
                return redirect('http://www.google.com')  # Reindirizza a Google se il consenso non è stato dato
        else:
            return render(request, self.template_name, {'form': form})  # Se il form non è valido, ricarica il template con il form e gli errori


class GraphsView(View):

    def get(self, request):

        # Recupera i dati per gli errori
        errors_by_date = ErrorLog.objects.values('timestamp').annotate(count=Count('id'))
        access_by_date = AccessLog.objects.values('timestamp').annotate(count=Count('id'))

        # Creazione dell'HTML per gli errori
        error_cum_chart_html = self.create_line_chart(errors_by_date, cumulative=True)
        access_cum_chart_html = self.create_line_chart(access_by_date, cumulative=True)

        error_line_chart_html = self.create_line_chart(errors_by_date, cumulative=False)
        access_line_chart_html = self.create_line_chart(access_by_date, cumulative=False)

        # Recupera i dati per la distribuzione dei codici di stato delle risposte
        response_codes = AccessLog.objects.values('response_code').annotate(count=Count('id'))
        # Creazione dell'HTML per la distribuzione dei codici di stato delle risposte
        response_code_chart_html = self.create_response_code_chart(response_codes)

        access_by_hour_chart = self.create_histogram_chart(access_by_date, 'hour')
        errors_by_hour_chart = self.create_histogram_chart(errors_by_date, 'hour')
        access_by_weekday_chart = self.create_histogram_chart(access_by_date, 'day')
        errors_by_weekday_chart = self.create_histogram_chart(errors_by_date, 'day')

        # Passa i dati al template della dashboard
        return render(request, 'logging_app/graphs.html', {
            'errors_line_chart_html': error_line_chart_html,
            'access_line_chart_html': access_line_chart_html,
            'errors_cum_chart_html': error_cum_chart_html,
            'access_cum_chart_html': access_cum_chart_html,
            'response_code_chart_html': response_code_chart_html,
            'access_by_hour_chart' : access_by_hour_chart,
            'errors_by_hour_chart' : errors_by_hour_chart,
            'access_by_weekday_chart' : access_by_weekday_chart,
            'errors_by_weekday_chart' : errors_by_weekday_chart,
        })


    def create_bar_chart(data, title, x_title, y_title):
        fig = go.Figure()
        fig.add_trace(go.Bar(x=[entry['hour'] for entry in data], y=[entry['count'] for entry in data]))
        fig.update_layout(title=title, xaxis_title=x_title, yaxis_title=y_title)
        return fig.to_html(full_html=False)

    def create_response_code_chart(self, response_codes):
        """
        Crea un grafico a torta che visualizza la distribuzione dei codici di stato delle risposte.
        """
        fig = go.Figure(data=[go.Pie(labels=[entry['response_code'] for entry in response_codes], values=[entry['count'] for entry in response_codes])])
        fig.update_layout(title='Response Code Distribution')
        return fig.to_html(full_html=False)

    def create_line_chart(self, data, cumulative=False):
        """
        Crea un grafico a linee che mostra il conteggio degli eventi nel tempo.

        Args:
            data (list): Una lista di dizionari contenente i dati da visualizzare nel grafico.
            cumulative (bool, optional): Se True, il grafico mostrerà il conteggio cumulativo nel tempo. Se False, mostrerà il conteggio non cumulativo. Default è False.

        Returns:
            str: HTML del grafico a linee.
        """
        if cumulative:
            # Calcola il conteggio cumulativo nel tempo

            data = list(data)
            data.sort(key=lambda x: x['timestamp'])

            # Calcola il conteggio cumulativo
            cumulative_data = np.cumsum([entry['count'] for entry in data])
            
            # Crea il grafico a linee con il conteggio cumulativo
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[entry['timestamp'] for entry in data], y=cumulative_data, mode='lines', name='Cumulative Count'))
            fig.update_layout(title='Cumulative Trend Over Time', xaxis_title='Date', yaxis_title='Cumulative Count')
        else:
            # Crea il grafico a linee con il conteggio non cumulativo
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[entry['timestamp'] for entry in data], y=[entry['count'] for entry in data], mode='lines', name='Count'))
            fig.update_layout(title='Trend Over Time', xaxis_title='Date', yaxis_title='Count')

        # Restituisce l'HTML del grafico
        return fig.to_html(full_html=False)

    
    def create_histogram_chart(self, data, interval='day'):
        """
        Crea un grafico a barre che mostra il conteggio degli eventi in base all'intervallo specificato (ora o giorno).

        Args:
            data (list): Una lista di dizionari contenente i dati da visualizzare nel grafico.
            interval (str, optional): L'intervallo temporale per aggregare i dati. Può essere 'hour' o 'day'. Default è 'day'.

        Returns:
            str: HTML del grafico a barre.
        """
        # Inizializza un dizionario per aggregare i dati
        aggregated_data = {}

        # Aggrega i dati in base all'intervallo specificato
        for entry in data:
            timestamp = entry['timestamp']
            if interval == 'hour':
                key = timestamp.strftime('%H:00:00')
            elif interval == 'day':
                key = timestamp.strftime('%A')
            else:
                raise ValueError("Interval must be 'hour' or 'day'")
            
            aggregated_data[key] = aggregated_data.get(key, 0) + entry['count']

        # Estrae le date e i conteggi aggregati
        dates = list(aggregated_data.keys())
        counts = list(aggregated_data.values())

        # Crea il grafico a barre
        fig = go.Figure(data=[go.Bar(x=dates, y=counts, name='Count')])

        # Aggiorna il layout del grafico
        if interval == 'hour':
            fig.update_layout(title='Count per Hour', xaxis_title='Hour', yaxis_title='Count')
        elif interval == 'day':
            fig.update_layout(title='Count per Day', xaxis_title='Day', yaxis_title='Count')

        # Restituisce l'HTML del grafico
        return fig.to_html(full_html=False)


class IPListView(View):
    def get(self, request):
        # Recupera i log per la lista dei log
        IP_list = AccessLog.objects.all()
        
        # Creare un DataFrame con i dati ottenuti
        df = pd.DataFrame(IP_list.values('ip_address', 'request_path', 'request_method', 'timestamp', 'response_code'))
        graph = self.create_graph(df)

        # Passa i dati al template della dashboard
        return render(request, 'logging_app/IPlist.html', {
            'graph': graph,
            'ip_list': IP_list.order_by('-timestamp')[:20] # Passa il percorso dell'immagine del grafico al template
        })


    def create_graph(self, df):
        # Creare il grafico utilizzando Plotly
        ip_counts = df['ip_address'].value_counts().head(10)
        max_value = ip_counts.max()  # Trova il massimo valore tra i conteggi degli accessi

        data = [go.Bar(x=ip_counts.index, y=ip_counts.values)]
        layout = go.Layout(xaxis=dict(title='IP Address'), yaxis=dict(title='Number of Accesses', range=[0, max_value * 1.1]))  # Imposta il range dell'asse y
        fig = go.Figure(data=data, layout=layout)
        return fig.to_html(full_html=False)



class AEListView(View):
    def get(self, request):

        # Recupera i log per la lista dei log
        accesslogs = AccessLog.objects.all().order_by('-timestamp')[:50]
        errorlogs = ErrorLog.objects.all().order_by('-timestamp')[:50]

        # Passa i dati al template della dashboard
        return render(request, 'logging_app/AElist.html', {
            'accesslogs': accesslogs,
            'errorlogs': errorlogs,
        })


class AccessLogDetailView(View):
    def get(self, request, log_id):
        # Recupera il log specifico
        log = get_object_or_404(AccessLog, pk=log_id)

        # Passa il log al template dei dettagli del log
        return render(request, 'logging_app/log_detail.html', {'log': log})


class ErrorLogDetailView(View):
    def get(self, request, log_id):
        # Recupera il log specifico
        log = get_object_or_404(ErrorLog, pk=log_id)

        # Passa il log al template dei dettagli del log
        return render(request, 'logging_app/log_detail.html', {'log': log})
