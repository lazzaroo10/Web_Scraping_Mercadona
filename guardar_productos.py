
#SELENIUM
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager


#Move
from functions import retry_click_element , enter_postal_code , handle_popup ,search_and_submit 
#Work with products
from functions import guardar_productos , click_add_to_cart_by_name , click_add_to_cart_by_name_delete, guardar_productos_2
#Limpiar texto
import re
import os

#DF
import pandas as pd

import time
# https://sites.google.com/chromium.org/driver/

def take_product_screenshot(driver, wait, product_folder, sanitized_term):
    """Capture and save screenshot of product results"""
    try:
        # Wait for results to load
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div[data-testid="product-cell"]')
        ))
        
        # Take screenshot and save to product folder
        screenshot_path = os.path.join(product_folder, f"{sanitized_term}_screenshot.png")
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved: {screenshot_path}")
        return True
    except Exception as screenshot_error:
        print(f"Failed to take screenshot for {sanitized_term}: {screenshot_error}")
        return False


# Para que no corra minimizado comenta la línea de abajo
options = Options()
# options.add_argument("--headless")  # Ejecuta Chrome en modo headless
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)


# #Para que no corra minimizado comenta la linea de abajo
# options = Options()

# #options.add_argument("--headless")  # Run Chrome in headless mode

# service = Service(executable_path="chromedriver.exe")
# driver = webdriver.Chrome(service=service, options=options)

driver.get("https://www.mercadona.es/")

wait = WebDriverWait(driver, 5)  # Wait for up to 10 seconds

CODIGO_POSTAL = "46007"

#Producto de prueba que se usa para 
PRODUCTO_PRUEBA = 'Espárrago verde grueso'

LISTA_PRODUCTOS = ['manzanas','peras','gominolas','chocolate','leche','pan','agua','cerveza','vino','cava','coca cola','fanta','sprite','naranja']
print(LISTA_PRODUCTOS)

try:
    # Rechazar las cookies.
    cookies_closed = retry_click_element(driver,By.CSS_SELECTOR,'button.ui-button--tertiary.ui-button--positive',
    retries=3,wait_time=5)
    if cookies_closed:
        print("Botón 'Rechazar' de cookies clicado correctamente.")
    else:
        print("No se pudo clicar el botón 'Rechazar' tras varios intentos.")

    # Añade el Codigo Postal
    enter_postal_code(driver, wait, CODIGO_POSTAL)

    # Añade los productos al carro con "Añadir al carro" 
    # El primer producto saca un pop up, asi que se mete elemento de prueba que posteriormente se elimina.

    # search_and_submit(driver, wait, PRODUCTO_PRUEBA)
    # click_add_to_cart_by_name(driver,wait,PRODUCTO_PRUEBA,1,'ud','NaN')
    # # Handle the popup if it appears
    # handle_popup(driver, wait)
    
    # Buscar y seleccionar los productos de la lista

    # Create the folder if it doesn't exist
    main_folder = "excel_productos_headless"
    if not os.path.exists(main_folder):
        os.makedirs(main_folder)

    for i in range(0, len(LISTA_PRODUCTOS)):
        try:
            time.sleep(2)
            term = LISTA_PRODUCTOS[i]
            
            # Sanitize the term for folder/file names
            sanitized_term = term.replace(' ', '_').replace('/', '-')
            
            # Create product-specific folder path
            product_folder = os.path.join(main_folder, sanitized_term)
            
            # Create product folder if it doesn't exist
            os.makedirs(product_folder, exist_ok=True)

            search_and_submit(driver, wait, term)

            # Capture screenshot using dedicated function
            time.sleep(5)
            take_product_screenshot(driver, wait, product_folder, sanitized_term)

            df = guardar_productos_2(driver, wait, term)
            
            # Create file path inside the product folder
            file_name = f"{sanitized_term}.xlsx"
            file_path = os.path.join(product_folder, file_name)

            # Save the DataFrame to Excel
            df.to_excel(file_path, index=False)
            print(f"Excel file saved: {file_path}")

        except Exception as e:
            print(f"Error al procesar el producto '{term}': {e}. Continuando con el siguiente.")

    #Eliminar elemento de prueba
    #search_and_submit(driver, wait, PRODUCTO_PRUEBA)
    #click_add_to_cart_by_name_delete(driver,wait,PRODUCTO_PRUEBA,1,'ud','NaN',True)

except TimeoutException:
    print("El campo de código postal no se encontró dentro del tiempo de espera.")

# Mantener el navegador abierto hasta que el usuario presione Enter
input("Presiona Enter para cerrar el navegador...")