import requests  
from bs4 import BeautifulSoup  
import time  
import csv  
import random  

# URL base del sitio web a scrapear
BASE_URL = "https://www.filmaffinity.com"

# Lista para almacenar las calificaciones de las reseñas
comentariosNota = []  

# Lista para almacenar el texto de las reseñas
comentariosTexto = []  

# Funcion que construye la URL de reseñas de una pelicula segun su ID y el numero de pagina
def construct_review_url(movie_id, page_number):
    return f"{BASE_URL}/pe/reviews/{page_number}/{movie_id}.html"

# Funcion para hacer una solicitud con reintento en caso de error o demasiadas solicitudes
def request_with_retry(url):
    while True:  
        # Bucle infinito para intentar repetidamente la solicitud
        try:
            response = requests.get(url)  
            # Realiza la solicitud HTTP
            if response.status_code == 429:  
                print(f"Too Many Requests for URL {url}. Waiting 5 minutes before retrying.")
                time.sleep(300)  
            else:
                response.raise_for_status()  
                # Verifica si la solicitud fue exitosa
                return response  
                # Devuelve la respuesta si fue exitosa
        except requests.RequestException as e:
            print(f"Request error for URL {url}: {e}")  
            # Muestra el error
            break  

# Bucle principal para recorrer las paginas de clasificacion de peliculas
for npage in range(1, 2):  
    # Aqui solo se considera la primera pagina (rango hasta 2 es exclusivo)
    URLOrigin = f"{BASE_URL}/pe/rankings.php?p={npage}"  
    # Construye la URL para la pagina de clasificaciones
    try:
        pageMain = request_with_retry(URLOrigin)  
        # Intenta obtener la pagina principal
        if pageMain is None:
            continue  
            # Si no se pudo obtener, pasa a la siguiente iteracion

        soup = BeautifulSoup(pageMain.content, "html.parser")  
        # Analiza el contenido HTML de la pagina
        rankings = soup.find_all("ul", class_="rankings-list")  
        # Busca las listas de clasificaciones

        # Lista para almacenar las URLs de las peliculas en la pagina de clasificaciones
        mainpageRanks = []  

        for a in rankings:
            links = a.find_all('a')  
            # Encuentra todos los enlaces dentro de las listas de clasificaciones
            for link in links:
                if link.has_attr('href'):  
                    # Verifica si el enlace tiene el atributo 'href'
                    full_url = link['href']
                    if not full_url.startswith("http"):  
                        # Si el enlace es relativo, lo completa con la URL base
                        full_url = BASE_URL + full_url
                    mainpageRanks.append(full_url)  
                    # Añade el enlace completo a la lista

    except requests.RequestException as e:
        print(f"Error fetching page {URLOrigin}: {e}")
        continue  
        # Continua con la siguiente iteracion si hay error en la pagina principal

    # Bucle para recorrer cada enlace de pelicula en la lista de clasificaciones
    for x in mainpageRanks:
        try:
            page = request_with_retry(x)  
            # Intenta obtener la pagina de la pelicula
            if page is None:
                continue  
                # Si no se pudo obtener, pasa a la siguiente iteracion

            soup = BeautifulSoup(page.content, "html.parser")  
            # Analiza el contenido HTML de la pagina
            titulos = soup.find_all("div", class_="mc-title")  
            # Busca el titulo de la pelicula

            # Lista para almacenar las URLs de las peliculas especificas
            mainpage = []  

            for a in titulos:
                links = a.find('a')  
                # Encuentra el primer enlace en el div del titulo
                if links and links.has_attr('href'):
                    full_movie_url = links['href']
                    if not full_movie_url.startswith("http"):  
                        # Si el enlace es relativo, lo completa
                        full_movie_url = BASE_URL + full_movie_url
                    mainpage.append(full_movie_url)  
                    # Añade el enlace de la pelicula a la lista
            
            # Bucle para recorrer las URLs de peliculas y obtener reseñas
            for movie_url in mainpage:
                try:
                    movie_id = movie_url.split('/')[-1].replace('film', '').replace('.html', '')  
                    # Extrae el ID de la pelicula
                except IndexError:
                    print(f"Unexpected movie URL format: {movie_url}")  
                    # Maneja error si el formato de URL no es esperado
                    continue

                # Contador de pagina de reseñas para la pelicula actual
                cont = 1  
                while True:
                    # Construye la URL de reseñas para la pelicula y pagina actual
                    newMovie = construct_review_url(movie_id, cont)  
                    try:
                        moviePage = request_with_retry(newMovie)  
                        # Intenta obtener la pagina de reseñas
                        if moviePage is None:
                            break  
                            # Si no se pudo obtener, termina el bucle de reseñas para esta pelicula

                        soup_reviews = BeautifulSoup(moviePage.content, "html.parser")  
                        # Analiza el HTML de reseñas
                        new_comentariosNota = soup_reviews.find_all("div", class_="user-reviews-movie-rating")  
                        # Encuentra calificaciones
                        new_comentariosTexto = soup_reviews.find_all("div", class_="review-text1")  
                        # Encuentra textos de reseñas

                        if not new_comentariosNota and not new_comentariosTexto:
                            break  
                            # Si no encuentra mas reseñas, termina el bucle

                        comentariosNota.extend(new_comentariosNota)  
                        # Añade calificaciones a la lista
                        comentariosTexto.extend(new_comentariosTexto)  
                        # Añade textos de reseñas a la lista

                        cont += 1  
                        # Avanza al siguiente numero de pagina de reseñas

                    except requests.RequestException as e:
                        break  
                        # Termina el bucle en caso de error
                    time.sleep(random.uniform(1, 5))  
                    # Espera aleatoriamente entre 1 y 5 segundos

        except requests.RequestException as e:
            time.sleep(2)  
            # Espera 2 segundos en caso de error y continua con la siguiente pelicula

# Guardar las reseñas en un archivo CSV
with open('reviews.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Rating', 'Review'])  
    for nota, texto in zip(comentariosNota, comentariosTexto):
        rating = nota.get_text(strip=True)  
        # Extrae y limpia el texto de la calificacion
        review = texto.get_text(strip=True)  
        # Extrae y limpia el texto de la reseña
        writer.writerow([rating, review])  
        # Escribe la fila con calificacion y reseña en el CSV
