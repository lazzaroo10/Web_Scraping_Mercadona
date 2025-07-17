#SELENIUM
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

import time

#Limpiar texto
import re

import pandas as pd

def retry_click_element(driver, by, selector, retries=3, wait_time=2):
    """
    Tries to click an element specified by a selector multiple times.
    Args:
        driver: Selenium WebDriver instance.
        by: The locator strategy (e.g., By.CSS_SELECTOR).
        selector: The CSS selector or locator for the element.
        retries: Maximum number of retries.
        wait_time: Time to wait between retries in seconds.
    Returns:
        True if the click is successful, False otherwise.
    """
    for attempt in range(retries):
        try:
            WebDriverWait(driver, wait_time).until(
                EC.element_to_be_clickable((by, selector))
            ).click()
            print(f"Elemento clicado correctamente en el intento {attempt + 1}.")
            return True
        except (TimeoutException, NoSuchElementException):
            print(f"Intento {attempt + 1} fallido. Reintentando...")
    return False

#Auxiliares

def enter_postal_code(driver, wait , postal_code):
    """
    Handles entering the postal code and clicking the submit button.
    Args:
        driver: Selenium WebDriver instance.
        postal_code: Postal code to be entered in the input field.
    """

    # Wait for the postal code input field to be present
    input_codigo_postal = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[aria-label="Código postal"]'))
    )
    input_codigo_postal.clear()  # Clear the field before entering the postal code
    input_codigo_postal.send_keys(postal_code)  # Enter the postal code
    print("Código postal ingresado correctamente.")

    # Wait for the submit button to be clickable
    boton_entrar = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input.postal-code-form__button[type="submit"]'))
    )
    boton_entrar.click()  # Click the button
    print("Botón de entrada presionado correctamente.")

def handle_popup(driver, wait):
    """
    Handles the popup that asks "¿Ya tienes cuenta?" and clicks "Ahora no" if it appears.
    Args:
        driver: Selenium WebDriver instance.
        wait: WebDriverWait instance for explicit waits.
    """
    try:
        boton_ahora_no = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.ui-button--quaternary.ui-button--positive.ui-button--full-width'))
        )
        boton_ahora_no.click()
        print("Botón 'Ahora no' clicado correctamente.")
    except TimeoutException:
        print("El popup '¿Ya tienes cuenta?' no apareció. Continuando...")

def retry_find_elements(wait, selector, max_attempts=3):
    """Retry mechanism to find elements with specified selector"""
    attempt = 0
    while attempt < max_attempts:
        try:
            elements = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
            )
            return elements
        except (StaleElementReferenceException, TimeoutException) as e:
            attempt += 1
            print(f"Attempt {attempt} failed with error: {e}. Retrying...")
            time.sleep(2)
    raise Exception(f"Unable to locate elements with selector '{selector}' after {max_attempts} attempts")

#Comprar productos

def click_add_to_cart_by_name(driver, wait, term, cantidad, etiqueta, etiqueta_2):
    """
    Clicks the "Añadir al carro" button for a product matching the specified name
    and adds it to the cart the specified number of times, with label and additional checks.

    Args:
        driver: Selenium WebDriver instance.
        wait: WebDriverWait instance for explicit waits.
        term: The name of the product to search for.
        cantidad: The quantity to add. Only allows up to 10.
        etiqueta: The expected label for the product (e.g., 'ud' or 'pack').
        etiqueta_2: Additional condition to check inside the product details (e.g., '6 mini bricks x 200 ml').
                    If it's NaN, this condition is ignored.
    """
    term = term.strip()
    cantidad = min(cantidad, 10)  # Limit the addition to a maximum of 10

    try:
        
        # Wait for the product cells to load
        product_cells = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-testid="product-cell"]'))
        )

        for product in product_cells:
            # Find the product name element inside the current product cell
            name_element = product.find_element(By.CSS_SELECTOR, 'h4[data-testid="product-cell-name"]')
            product_name = name_element.text.strip()
            print('********************************************************************************')
            print(product_name)

            # Find the product label element
            label_element = product.find_element(By.CSS_SELECTOR, 'p.product-price__extra-price.subhead1-r')
            product_label = re.sub(r'[^a-zA-Z]', '', label_element.text)  # Extract and normalize the label

            # Check if etiqueta_2 is not NaN, and validate its presence in the span element
            etiqueta_2_condition_met = True
            if etiqueta_2 and str(etiqueta_2).lower() != 'nan':
                try:
                    detail_element = product.find_element(By.CSS_SELECTOR, 'span.footnote1-r')
                    product_details = detail_element.text.strip()
                    etiqueta_2_condition_met = etiqueta_2 in product_details
                except Exception:
                    etiqueta_2_condition_met = False  # Fail the condition if the element is missing

            # Check if the product name, etiqueta, and etiqueta_2 (if provided) match
            if product_name == term and product_label == etiqueta and etiqueta_2_condition_met:
                print(f"Producto encontrado: '{product_name}' con etiqueta '{product_label}' y detalle '{etiqueta_2}'.")
                print(f"Intentando añadir al carro {cantidad} veces.")

                for i in range(cantidad):
                    try:
                        if i == 0:
                            # For the first addition, click the "Añadir al carro" button
                            add_button = product.find_element(By.CSS_SELECTOR, 'button[data-testid="product-quantity-button"]')
                        else:
                            # For subsequent additions, click the "+" icon
                            add_button = product.find_element(By.CSS_SELECTOR, 'i.icon-plus-28[data-testid="icon"]')

                        driver.execute_script("arguments[0].scrollIntoView(true);", add_button)  # Ensure it's visible
                        wait.until(EC.element_to_be_clickable(add_button)).click()
                        print(f"Añadido al carro {i + 1} de {cantidad} veces para '{product_name}' con etiqueta '{etiqueta}'.")
                    
                    except Exception as e:
                        print(f"No se pudo añadir al carro en la iteración {i + 1} para '{product_name}': {e}")
                        break
                return  # Exit after adding the product
        else:
            print(f"Producto '{term}' no encontrado o no coincide con la etiqueta '{etiqueta}' y detalle '{etiqueta_2}'.")
    except TimeoutException:
        print("No se pudieron cargar los productos dentro del tiempo de espera.")

def click_add_to_cart_by_name_2(driver, wait, term, cantidad, etiqueta, etiqueta_2):
    """
    Clicks the "Añadir al carro" button for a product matching the specified name,
    label, and additional details, then adds it to the cart a specified number of times.
    
    Args:
        driver: Selenium WebDriver instance.
        wait: WebDriverWait instance for explicit waits.
        term: The product name to search for.
        cantidad: Number of times to add the product (max 10).
        etiqueta: Expected label (e.g., 'ud' or 'pack').
        etiqueta_2: Additional condition for product details (e.g., '6 mini bricks x 200 ml').
                    Ignored if it is NaN.
    """
    term = term.strip()
    cantidad = min(cantidad, 10)  # Limit to a maximum of 10

    try:
        # Wait for the product cells to be visible on the page
        product_cells = wait.until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'div[data-testid="product-cell"]'))
        )
        print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        print(product_cells)
        print(f"Productos encontrados: {len(product_cells)}")

        for product in product_cells:
            try:
                # Fetch the product name element
                name_element = product.find_element(By.CSS_SELECTOR, 'h4[data-testid="product-cell-name"]')
                product_name = name_element.text.strip()
            except StaleElementReferenceException:
                # If the element is stale, re-fetch the product cells and skip this iteration
                product_cells = wait.until(
                    EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'div[data-testid="product-cell"]'))
                )
                continue
            
            print('********************************************************************************')
            print(product_name)

            # Get and normalize the product label
            label_element = product.find_element(By.CSS_SELECTOR, 'p.product-price__extra-price.subhead1-r')
            product_label = re.sub(r'[^a-zA-Z]', '', label_element.text)

            # Check the additional detail condition if provided
            etiqueta_2_condition_met = True
            if etiqueta_2 and str(etiqueta_2).lower() != 'nan':
                try:
                    detail_element = product.find_element(By.CSS_SELECTOR, 'span.footnote1-r')
                    product_details = detail_element.text.strip()
                    etiqueta_2_condition_met = etiqueta_2 in product_details
                except Exception:
                    etiqueta_2_condition_met = False

            # Verify that the product matches the criteria
            if product_name == term and product_label == etiqueta and etiqueta_2_condition_met:
                print(f"Producto encontrado: '{product_name}' con etiqueta '{product_label}' y detalle '{etiqueta_2}'.")
                print(f"Intentando añadir al carro {cantidad} veces.")

                for i in range(cantidad):
                    try:
                        if i == 0:
                            # For the first addition, click the main button
                            add_button = product.find_element(By.CSS_SELECTOR, 'button[data-testid="product-quantity-button"]')
                        else:
                            # For subsequent additions, click the "+" icon
                            add_button = product.find_element(By.CSS_SELECTOR, 'i.icon-plus-28[data-testid="icon"]')

                        # Ensure the button is visible and clickable
                        driver.execute_script("arguments[0].scrollIntoView(true);", add_button)
                        wait.until(EC.element_to_be_clickable(add_button))
                        add_button.click()
                        print(f"Añadido al carro {i + 1} de {cantidad} veces para '{product_name}'.")
                    except Exception as e:
                        print(f"No se pudo añadir al carro en la iteración {i + 1} para '{product_name}': {e}")
                        break
                return  # Exit once the product has been processed

        print(f"Producto '{term}' no encontrado o no coincide con la etiqueta '{etiqueta}' y detalle '{etiqueta_2}'.")

    except TimeoutException:
        print("No se pudieron cargar los productos dentro del tiempo de espera.")

def click_add_to_cart_by_name_delete(driver, wait, term, cantidad, etiqueta, etiqueta_2, delete=False):
    """
    Clicks the "Añadir al carro" button for a product matching the specified name,
    adds it to the cart the specified number of times, or deletes it if delete is True.

    Args:
        driver: Selenium WebDriver instance.
        wait: WebDriverWait instance for explicit waits.
        term: The name of the product to search for.
        cantidad: The quantity to add. Only allows up to 10. Ignored if delete is True.
        etiqueta: The expected label for the product (e.g., 'ud' or 'pack').
        etiqueta_2: Additional condition to check inside the product details (e.g., '6 mini bricks x 200 ml').
                    If it's NaN, this condition is ignored.
        delete: Whether to delete the product from the cart. Defaults to False.
    """
    term = term.strip()
    cantidad = 1 if delete else min(cantidad, 10)  # Ensure cantidad is 1 if delete is True

    try:
        # Wait for the product cells to load
        product_cells = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-testid="product-cell"]'))
        )

        for product in product_cells:
            # Find the product name element inside the current product cell
            name_element = product.find_element(By.CSS_SELECTOR, 'h4[data-testid="product-cell-name"]')
            product_name = name_element.text.strip()

            # Find the product label element
            label_element = product.find_element(By.CSS_SELECTOR, 'p.product-price__extra-price.subhead1-r')
            product_label = re.sub(r'[^a-zA-Z]', '', label_element.text)  # Extract and normalize the label

            # Check if etiqueta_2 is not NaN, and validate its presence in the span element
            etiqueta_2_condition_met = True
            if etiqueta_2 and str(etiqueta_2).lower() != 'nan':
                try:
                    detail_element = product.find_element(By.CSS_SELECTOR, 'span.footnote1-r')
                    product_details = detail_element.text.strip()
                    etiqueta_2_condition_met = etiqueta_2 in product_details
                except Exception:
                    etiqueta_2_condition_met = False  # Fail the condition if the element is missing

            # Check if the product name, etiqueta, and etiqueta_2 (if provided) match
            if product_name == term and product_label == etiqueta and etiqueta_2_condition_met:
                if delete:
                    print(f"Producto encontrado: '{product_name}' con etiqueta '{product_label}' y detalle '{etiqueta_2}'. Intentando eliminar del carro.")
                    try:
                        # Click the delete button
                        delete_button = product.find_element(By.CSS_SELECTOR, 'i.icon-delete-28[data-testid="icon"]')
                        driver.execute_script("arguments[0].scrollIntoView(true);", delete_button)  # Ensure it's visible
                        wait.until(EC.element_to_be_clickable(delete_button)).click()
                        print(f"Producto '{product_name}' eliminado del carro exitosamente.")
                    except Exception as e:
                        print(f"No se pudo eliminar el producto '{product_name}': {e}")
                else:
                    print(f"Producto encontrado: '{product_name}' con etiqueta '{product_label}' y detalle '{etiqueta_2}'.")
                    print(f"Intentando añadir al carro {cantidad} veces.")
                    for i in range(cantidad):
                        try:
                            if i == 0:
                                # For the first addition, click the "Añadir al carro" button
                                add_button = product.find_element(By.CSS_SELECTOR, 'button[data-testid="product-quantity-button"]')
                            else:
                                # For subsequent additions, click the "+" icon
                                add_button = product.find_element(By.CSS_SELECTOR, 'i.icon-plus-28[data-testid="icon"]')

                            driver.execute_script("arguments[0].scrollIntoView(true);", add_button)  # Ensure it's visible
                            wait.until(EC.element_to_be_clickable(add_button)).click()
                            print(f"Añadido al carro {i + 1} de {cantidad} veces para '{product_name}' con etiqueta '{etiqueta}'.")
                        
                        except Exception as e:
                            print(f"No se pudo añadir al carro en la iteración {i + 1} para '{product_name}': {e}")
                            break
                return  # Exit after adding or deleting the product
        else:
            print(f"Producto '{term}' no encontrado o no coincide con la etiqueta '{etiqueta}' y detalle '{etiqueta_2}'.")
    except TimeoutException:
        print("No se pudieron cargar los productos dentro del tiempo de espera.")

def guardar_productos(driver, wait, producto):

    product_cells = wait.until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-testid="product-cell"]'))
    )

    productos = []

    for product in product_cells:

        # Find the product name element inside the current product cell
        name_element = product.find_element(By.CSS_SELECTOR, 'h4[data-testid="product-cell-name"]')
        product_name = name_element.text.strip()

        # Find the product label element
        label_element = product.find_element(By.CSS_SELECTOR, 'p.product-price__extra-price.subhead1-r')
        product_label = re.sub(r'[^a-zA-Z]', '', label_element.text)

        # Find the product format element

        format_element = product.find_element(By.CSS_SELECTOR, 'div.product-format.product-format__size--cell')
        product_format = format_element.text

        # Extract the product price (e.g., "1,60 €")
        price_element = product.find_element(By.CSS_SELECTOR, 'p.product-price__unit-price[data-testid="product-price"]')
        product_price = price_element.text

        productos.append({
        'Nombre_producto': product_name,
        'Precio': product_price,
        'etiqueta': product_label,
        'formato': product_format
        })

        print('Nombre_producto',product_name,'Precio',product_price, 'etiqueta', product_label,'formato',product_format)
    df = pd.DataFrame(productos)
    return df

def guardar_productos_2(driver, wait, producto, max_attempts=3):
    """Main function to gather and process product data"""
    # Get product cells with retry mechanism
    product_cells = retry_find_elements(
        wait,
        'div[data-testid="product-cell"]',
        max_attempts
    )

    # Process all product cells
    productos = []
    for product in product_cells:
        try:
            # Extract product name
            name_element = product.find_element(By.CSS_SELECTOR, 'h4[data-testid="product-cell-name"]')
            product_name = name_element.text.strip()

            # Extract and clean product label
            label_element = product.find_element(By.CSS_SELECTOR, 'p.product-price__extra-price.subhead1-r')
            product_label = re.sub(r'[^a-zA-Z]', '', label_element.text)

            # Extract product format
            format_element = product.find_element(By.CSS_SELECTOR, 'div.product-format.product-format__size--cell')
            product_format = format_element.text

            # Extract product price
            price_element = product.find_element(By.CSS_SELECTOR, 'p.product-price__unit-price[data-testid="product-price"]')
            product_price = price_element.text

            # Print and store the data
            print('Nombre_producto', product_name, 'Precio', product_price, 
                 'etiqueta', product_label, 'formato', product_format)
            
            productos.append({
                'Nombre_producto': product_name,
                'Precio': product_price,
                'etiqueta': product_label,
                'formato': product_format
            })
        except Exception as e:
            print(f"Error processing product: {e}")

    return pd.DataFrame(productos)

def search_and_submit(driver, wait, term):
    """
    Searches for each term in a given list by entering it into the search input field
    and clicking the search button.
    
    Args:
        driver: Selenium WebDriver instance.
        wait: WebDriverWait instance for explicit waits.
        search_terms: List of strings to search for.
    """
    try:
        # Locate the search input field
        search_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-testid="search-input"]'))
        )
        search_input.clear()  # Clear any existing text
        search_input.send_keys(term)  # Enter the search term
        print(f"Término '{term}' ingresado en el campo de búsqueda.")

        # Locate and click the search button
        search_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'span.search__button'))
        )
        search_button.click()
        print(f"Búsqueda realizada para el término '{term}'.")
        #click_add_to_cart(driver,wait)
        #time.sleep(1)  # Add a short delay to allow the results to load
    except TimeoutException:
        print(f"No se pudo completar la búsqueda para el término '{term}'.")

