import traceback
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.conf import settings  # Aggiungi questa riga per accedere alle impostazioni
from .models import AccessLog, ErrorLog

class LogMiddleware:
    LOGGING_PATH_PREFIX = ('/dashboard/logging/', '/static/', '/admin/', 'dashboard')
    LOGGING_PATH_POSTFIX = ('js', 'json', 'css')

    def __init__(self, get_response):
        """
        Inizializza il middleware con la funzione get_response che gestisce le richieste HTTP successive.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Metodo chiamato per ogni richiesta HTTP in arrivo.
        Registra un log dell'accesso al server e cattura eventuali eccezioni.
        """
        # Cattura la richiesta in arrivo
        response = self.get_response(request)
        
        if not (request.path.startswith(self.LOGGING_PATH_PREFIX) or request.path.endswith(self.LOGGING_PATH_POSTFIX)):
            ip_address = request.META.get('HTTP_X_REAL_IP', '')
            
            # Check if the IP address exists in the database
            if AccessLog.objects.filter(ip_address=ip_address).exists():

                # If the IP address exists, continue logging access as usual
                access_log = AccessLog(
                    ip_address=ip_address,
                    timestamp=timezone.now(),
                    request_path=request.path,
                    request_method=request.method,
                    response_code=response.status_code
                )
                access_log.save()
            else:
                # If the IP address does not exist, redirect to consent view
                return redirect('logging:consent_view')
        
        return response

    def process_exception(self, request, exception):
        """
        Metodo chiamato solo se si verifica un'eccezione durante l'elaborazione della richiesta.
        Cattura l'eccezione e registra un log dell'errore.
        """
        # Cattura l'eccezione e registra l'errore solo se DEBUG è False
        error_log = ErrorLog(
            ip_address=request.META.get('HTTP_X_REAL_IP', ''),  # Ottiene l'indirizzo IP del client
            timestamp=timezone.now(),  # Imposta il timestamp attuale
            request_path=request.path,  # Ottiene il percorso della richiesta
            request_method=request.method,  # Ottiene il metodo della richiesta (GET, POST, etc.)
            response_code=self.get_response(request).status_code,  # Ottiene il codice di stato della risposta del server
            error_message=str(exception),  # Ottiene il messaggio dell'eccezione
            stack_trace=traceback.format_exc()  # Ottiene lo stack trace dell'eccezione
        )

        error_log.save()  # Salva il log dell'errore nel database
