# Projekt - 2 mikroserwisy z RabbitMQ

## Jak uruchomić

1. Uruchamianie projektu:
```powershell
cd projekt
docker-compose up --build -d
```

2. Skalowanie konsumerów - zmień parametr `replicas` w `docker-compose.yml`:
```yaml
consumer:
  deploy:
    replicas: 3  # liczba instancji konsumera
```

## Endpointy

### Serwis A (port 5000)
- `GET /health` - sprawdzenie czy serwis działa
- `POST /results` - zapisanie wyniku analizy
- `GET /results` - pobranie wszystkich wyników
- `GET /results/<id>` - pobranie pojedynczego wyniku
- `DELETE /results/<id>` - usunięcie wyniku

### Serwis B (port 5001)
- `GET /health` - sprawdzenie czy serwis działa
- `POST /analyze` - wysłanie URL obrazu do analizy

## Przykład użycia

```powershell
# Wysłanie obrazu do analizy
Invoke-RestMethod -Uri "http://localhost:5001/analyze" -Method Post -ContentType "application/json" -Body '{"image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Pedestrians_in_a_crosswalk%2C_New_York_City.jpg/800px-Pedestrians_in_a_crosswalk%2C_New_York_City.jpg"}'

# Sprawdzenie wyników
Invoke-RestMethod -Uri "http://localhost:5000/results"
```

## Testowanie projektu krok po kroku

1. Uruchom projekt: `cd projekt; docker-compose up --build -d`
2. Sprawdź status kontenerów: `docker-compose ps`
3. Sprawdź health serwisów:
   - `Invoke-RestMethod http://localhost:5000/health`
   - `Invoke-RestMethod http://localhost:5001/health`
4. Poczekaj ~30 sekund na pobranie modelu YOLO przez konsumerów
5. Wyślij obrazek do analizy:
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5001/analyze" -Method Post -ContentType "application/json" -Body '{"image_url": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=640"}'
   ```
6. Poczekaj ~10 sekund i sprawdź wyniki:
   ```powershell
   # Pobierz wszystkie wyniki
   Invoke-RestMethod http://localhost:5000/results
   
   # Pobierz pojedynczy wynik (np. id=1) - zobaczysz ile osób wykryto
   Invoke-RestMethod http://localhost:5000/results/1
   
   # Usuń wynik
   Invoke-RestMethod -Uri "http://localhost:5000/results/1" -Method Delete
   ```
7. Test retry strategy:
   - Zatrzymaj Serwis A: `docker stop serwis_a`
   - Wyślij kolejny obrazek do analizy:
     ```powershell
     Invoke-RestMethod -Uri "http://localhost:5001/analyze" -Method Post -ContentType "application/json" -Body '{"image_url": "https://images.unsplash.com/photo-1517486808906-6ca8b3f04846?w=640"}'
     ```
   - Uruchom Serwis A: `docker start serwis_a`
   - Poczekaj ~10 sekund aż konsumer ponowi próbę wysłania wyniku
   - Sprawdź czy wynik się zapisał: `Invoke-RestMethod http://localhost:5000/results`
8. Zatrzymanie projektu: `docker-compose down`

### Testy jednostkowe

```powershell
# Testy Serwisu A
cd projekt\serwis_a
pip install -r requirements.txt
pytest tests\test_app.py -v

# Testy Serwisu B
cd ..\serwis_b
pip install -r requirements.txt
pytest tests\test_app.py -v
```