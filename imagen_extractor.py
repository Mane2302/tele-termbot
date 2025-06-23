import requests
from bs4 import BeautifulSoup

# URL de la página que quieres scrapear
url = 'https://coomer.su/onlyfans/user/redheadevelyn/post/1779649626'

# Enviar una solicitud HTTP a la URL
response = requests.get(url)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    # Parsear el contenido HTML de la página
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extraer el título de la página
    title = soup.title.string
    print(f'Título de la página: {title}')

    # Extraer todas las imágenes
    images = soup.find_all('img')
    for idx, img in enumerate(images, start=1):
        img_url = img.get('src')
        print(f'Imagen {idx}: {img_url}')
else:
    print(f'Error al acceder a la página. Código de estado: {response.status_code}')