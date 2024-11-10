import flet as ft
import sqlite3
from fpdf import FPDF
import os
from datetime import datetime

# Function to create a database and table if needed
def create_db(personnel_name):
    db_name = f"{personnel_name.lower()}.db"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Create the table if it does not exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS vehicules (
                        id INTEGER PRIMARY KEY,
                        date TEXT,
                        heure TEXT,
                        immatriculation TEXT,
                        vehicule TEXT,
                        nom_prenom TEXT,
                        partenaire TEXT)''')
    conn.commit()
    return conn, cursor

# Function to generate a PDF from personnel data
def generate_pdf(records, filename):
    pdf = FPDF()
    pdf.add_page()

    # Add a logo (provide the correct path to your logo image)
    logo_path = "logo.jpg"
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=8, w=30)  # Position and size of the logo

    # Add title
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt="Rapport des Véhicules", ln=True, align="C")
    pdf.cell(200, 10, txt="ADMIN : SOUHAIL", ln=True, align="C")
    pdf.ln(20)  # Spacing after title
    

    # Define table headers
    pdf.set_font("Arial", "B", 10)
    headers = ["ID", "Date", "Heure", "Immatriculation", "Véhicule", "Nom/Prénom", "Partenaire"]
    column_widths = [10, 30, 20, 30, 30, 40, 30]

    for i, header in enumerate(headers):
        pdf.cell(column_widths[i], 10, txt=header, border=1, align="C")
    pdf.ln()

    # Add table rows from records
    pdf.set_font("Arial", size=10)
    for record in records:
        for i, item in enumerate(record):
            pdf.cell(column_widths[i], 10, txt=str(item), border=1, align="C")
        pdf.ln()

    pdf.output(filename)
   

# Fonction pour afficher les données du personnel dans une table avec tri par date et heure
def show_personnel_data(personnel_name, page, search_query=None):
    conn, cursor = create_db(personnel_name)
    
    # Appliquer un filtre de recherche et trier par date et heure
    if search_query:
        cursor.execute("SELECT * FROM vehicules WHERE vehicule LIKE ? ORDER BY date ASC, heure ASC", ('%' + search_query + '%',))
    else:
        cursor.execute("SELECT * FROM vehicules ORDER BY date ASC, heure ASC")
    
    records = cursor.fetchall()
    
    table_columns = [
        ft.DataColumn(ft.Text("ID")),
        ft.DataColumn(ft.Text("Date")),
        ft.DataColumn(ft.Text("Heure")),
        ft.DataColumn(ft.Text("Immatriculation")),
        ft.DataColumn(ft.Text("Véhicule")),
        ft.DataColumn(ft.Text("Nom/Prénom")),
        ft.DataColumn(ft.Text("Partenaire")),
        ft.DataColumn(ft.Text("Actions")),
    ]
    
    table_rows = []
    for record in records:
        row_id = record[0]
        
        edit_button = ft.IconButton(icon=ft.icons.EDIT, tooltip="Modifier", on_click=lambda e, id=row_id: edit_vehicle(id, personnel_name, page))
        delete_button = ft.IconButton(icon=ft.icons.DELETE, tooltip="Supprimer", on_click=lambda e, id=row_id: delete_vehicle(id, personnel_name, page))
        
        table_rows.append(ft.DataRow(cells=[
            ft.DataCell(ft.Text(str(record[0]))),
            ft.DataCell(ft.Text(record[1])),
            ft.DataCell(ft.Text(record[2])),
            ft.DataCell(ft.Text(record[3])),
            ft.DataCell(ft.Text(record[4])),
            ft.DataCell(ft.Text(record[5])),
            ft.DataCell(ft.Text(record[6])),
            ft.DataCell(ft.Row([edit_button, delete_button])),
        ]))
    
    def download_pdf(e):
        pdf_filename = f"{personnel_name}_vehicles.pdf"
        generate_pdf(records, pdf_filename)
        
        pdf_file_info = [
            ["Filename", pdf_filename],
            ["Size", f"{os.path.getsize(pdf_filename) / 1024:.2f} KB"],
            ["Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        ]
        
        pdf_table_columns = [
            ft.DataColumn(ft.Text("Attribute")),
            ft.DataColumn(ft.Text("Value"))
        ]
        pdf_table_rows = [ft.DataRow(cells=[ft.DataCell(ft.Text(info[0])), ft.DataCell(ft.Text(info[1]))]) for info in pdf_file_info]
        
        page.add(
            ft.Text(f"PDF généré: {pdf_filename}"),
            ft.DataTable(columns=pdf_table_columns, rows=pdf_table_rows)
        )
    
    page.add(
        ft.Text(f"Informations pour {personnel_name}:"),
        ft.Column(
            controls=[
                ft.DataTable(columns=table_columns, rows=table_rows),
            ],
            scroll="auto",  # Enable scrolling when the table is too big
            height=400,  # Set fixed height for the table view
        ),
        ft.ElevatedButton("Télécharger PDF", icon=ft.icons.DOWNLOAD, on_click=download_pdf)
    )
    
    conn.close()

def edit_vehicle(id, personnel_name, page):
    conn, cursor = create_db(personnel_name)
    cursor.execute("SELECT * FROM vehicules WHERE id = ?", (id,))
    record = cursor.fetchone()
    conn.close()
    
    if record:
        date = ft.TextField(label="Date", value=record[1])
        heure = ft.TextField(label="Heure", value=record[2])
        immatriculation = ft.TextField(label="Immatriculation", value=record[3])
        vehicule = ft.TextField(label="Véhicule", value=record[4])
        nom_prenom = ft.TextField(label="Nom/Prénom", value=record[5])
        partenaire = ft.TextField(label="Partenaire", value=record[6])

        def save_changes(e):
            conn, cursor = create_db(personnel_name)
            cursor.execute('''UPDATE vehicules SET date=?, heure=?, immatriculation=?, vehicule=?, nom_prenom=?, partenaire=? 
                              WHERE id=?''',
                           (date.value, heure.value, immatriculation.value, vehicule.value, nom_prenom.value, partenaire.value, id))
            conn.commit()
            conn.close()
            page.add(ft.Text("Modification sauvegardée."))
            page.clean()
            show_personnel_data(personnel_name, page)

        page.clean()
        page.add(
            ft.Text("Modifier Véhicule"),
            date, heure, immatriculation, vehicule, nom_prenom, partenaire,
            ft.ElevatedButton("Enregistrer", icon=ft.icons.SAVE, on_click=save_changes)
        )

def delete_vehicle(id, personnel_name, page):
    conn, cursor = create_db(personnel_name)
    cursor.execute("DELETE FROM vehicules WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    page.add(ft.Text("Véhicule supprimé avec succès."))
    page.clean()
    show_personnel_data(personnel_name, page)

def main(page: ft.Page):
    page.title = "Système de gestion de location de voiture"

    def go_to_login(e):
        page.clean()
        login_page()

    def login_page():
        logo = ft.Image(src="logo.jpg", width=100, height=100)
        username = ft.TextField(label="Nom d'utilisateur")
        password = ft.TextField(label="Mot de passe", password=True)
        role = ft.Dropdown(
            label="Rôle",
            options=[ft.dropdown.Option("admin"), ft.dropdown.Option("personnel")]
        )

        def login_action(e):
            if role.value == "admin" and username.value == "CERIZA" and password.value == "ceriza3010":
                page.clean()
                admin_page()
            elif role.value == "personnel":
                if username.value == "Anas" and password.value == "anas":
                    page.clean()
                    staff_page("Anas")
                elif username.value == "Jawad" and password.value == "jawad":
                    page.clean()
                    staff_page("Jawad")
                else:
                    page.add(ft.Text("Identifiant ou mot de passe du personnel incorrect.", color="red"))
            else:
                page.add(ft.Text("Nom d'utilisateur, mot de passe ou rôle incorrect.", color="red"))

        page.add(
            logo,
            ft.Text("Connexion", size=30, weight=ft.FontWeight.BOLD),
            username,
            password,
            role,
            ft.ElevatedButton("Connexion", icon=ft.icons.LOGIN, on_click=login_action),
        )

    def admin_page():
        logo = ft.Image(src="logo.jpg", width=100, height=100)
        date = ft.TextField(label="Date (JJ/MM/AAAA)", width=150)
        heure = ft.TextField(label="Heure (HH:MM)", width=150)
        immatriculation = ft.TextField(label="Immatriculation", width=150)
        vehicule = ft.TextField(label="Véhicule", width=150)
        nom_prenom = ft.TextField(label="Nom/Prénom", width=150)
        
        partner_dropdown = ft.Dropdown(
            label="Partenaire",
            width=150,
            options=[
                ft.dropdown.Option("CERIZA"),
                ft.dropdown.Option("FOX CAR"),
                ft.dropdown.Option("ZEZGO"),
                ft.dropdown.Option("IZI"),
                ft.dropdown.Option("DIRECT"),
            ],
        )
        
        personnel_dropdown = ft.Dropdown(
            label="Personnel responsable",
            width=150,
            options=[
                ft.dropdown.Option("Anas"),
                ft.dropdown.Option("Jawad")
            ],
        )
        
        search_field = ft.TextField(label="Recherche", width=150)

        def add_vehicle(e):
            personnel = personnel_dropdown.value
            if not personnel:
                page.add(ft.Text("Veuillez sélectionner un personnel.", color="red"))
                return
            
            conn, cursor = create_db(personnel)
            cursor.execute('''INSERT INTO vehicules (date, heure, immatriculation, vehicule, nom_prenom, partenaire)
                              VALUES (?, ?, ?, ?, ?, ?)''',
                           (date.value, heure.value, immatriculation.value, vehicule.value, nom_prenom.value, partner_dropdown.value))
            conn.commit()
            conn.close()
            
            page.add(ft.Text(f"Véhicule {vehicule.value} ajouté par {personnel} avec succès."))
            page.clean()
            admin_page()

        def refresh_table(e):
            show_personnel_data(personnel_dropdown.value, page, search_field.value)

        page.add(
            logo,
            ft.Text("Page Admin - Gestion des Véhicules", size=30, weight=ft.FontWeight.BOLD),
            date, heure, immatriculation, vehicule, nom_prenom, partner_dropdown, personnel_dropdown,
            search_field,
            ft.ElevatedButton("Ajouter véhicule", icon=ft.icons.ADD, on_click=add_vehicle),
            ft.ElevatedButton("Déconnexion", icon=ft.icons.LOGOUT, on_click=go_to_login),
        )

        search_field.on_change = refresh_table
        if personnel_dropdown.value:
            show_personnel_data(personnel_dropdown.value, page)
        
        page.update()

    def staff_page(name):
        logo = ft.Image(src="logo.jpg", width=100, height=100)
        show_personnel_data(name, page)
        page.add(
            logo,
            ft.Text(f"Page Personnel - {name}", size=30, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("Déconnexion", icon=ft.icons.LOGOUT, on_click=go_to_login),
        )

    login_page()
    page.update()

ft.app(target=main)
