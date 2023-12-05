# MainApp/views.py
import json
import pandas as pd
import asyncio
from asgiref.sync import sync_to_async
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from .forms import UploadFileForm
from .models import Candle

class UploadFileView(View):
    template_name = 'upload_file.html'

    async def get(self, request, *args, **kwargs):
        form = UploadFileForm()
        return render(request, self.template_name, {'form': form})

    @sync_to_async
    def process_csv(self, file, timeframe):
        # Implement your logic to process CSV and convert to candles asynchronously
        # For simplicity, this example assumes CSV columns are 'open', 'high', 'low', 'close', 'date'
        df = pd.read_csv(file)
        candles = []
        for index, row in df.iterrows():
            candle = Candle(open=row['open'], high=row['high'], low=row['low'],
                            close=row['close'], date=row['date'])
            candles.append(candle)
        # Implement your logic to convert candles to the given timeframe asynchronously
        return candles

    async def post(self, request, *args, **kwargs):
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            file = form.cleaned_data['file']
            timeframe = form.cleaned_data['timeframe']

            # Process the CSV file asynchronously
            candles = await self.process_csv(file, timeframe)

            # Save converted data to JSON file
            json_data = json.dumps([{
                'id': c.id,
                'open': float(c.open),
                'high': float(c.high),
                'low': float(c.low),
                'close': float(c.close),
                'date': c.date.isoformat()
            } for c in candles])

            with open('converted_data.json', 'w') as json_file:
                json_file.write(json_data)

            # Provide the JSON file for download
            response = HttpResponse(json_data, content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename="converted_data.json"'
            return response

        return render(request, self.template_name, {'form': form})
