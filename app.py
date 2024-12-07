from flask import Flask, request, render_template, redirect, url_for, session, flash, make_response
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, BigInteger, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask import send_from_directory
from datetime import datetime
import pandas as pd 
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time

load_dotenv()

# Configurazione dell'app Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Configurazione del database PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nome = Column(String)
    cognome = Column(String)
    citta = Column(String)
    data = Column(String)
    residenza = Column(String)
    sesso = Column(String)
    email = Column(String)
    carta_identita = Column(String)
    file = Column(String)
    approvato = Column(String)
    numero_tessera = Column(BigInteger)
    inviato = Column(String)
    manuale = Column(String)
    data_registrazione = Column(DateTime)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Middleware per gestire la lingua
@app.before_request
def set_language_context():
    session_language = session.get('language', 'it')  # Default italiano
    request.language = session_language

# Route per cambiare lingua
@app.route('/set_language/<lang_code>')
def set_language(lang_code):
    if lang_code in ['it', 'en']:
        session['language'] = lang_code
    else:
        flash("Lingua non supportata.", "error")
    return redirect(url_for('index'))

@app.route('/')
def index():
    language = session.get('language', 'it')  # Recupera la lingua corrente
    return render_template('form.html', language=language)

@app.route('/submit', methods=['POST'])
def submit():
    db_session = Session()
    try:
        email = request.form['email']

        # Controllo se l'email esiste già
        existing_user = db_session.query(User).filter_by(email=email).first()
        if existing_user:
            flash("Utente già registrato. Usa un'altra email.", "error")
            return redirect(url_for('index'))

        # Estrazione dati dal form
        nome = request.form['nome']
        cognome = request.form['cognome']
        citta = request.form['citta']
        data = request.form['data']
        residenza = request.form['residenza']
        sesso = request.form['sesso']
        carta_identita = request.form['carta_identita']
        file = request.files.get('file')

        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            file_name = file.filename
        else:
            file_name = None

        data_registrazione = datetime.now()
        new_user = User(
            nome=nome,
            cognome=cognome,
            citta=citta,
            data=data,
            residenza=residenza,
            sesso=sesso,
            carta_identita=carta_identita,
            email=email,
            file=file_name,
            approvato="NO",
            numero_tessera=None,
            inviato="NO",
            data_registrazione=data_registrazione
        )

        db_session.add(new_user)
        db_session.commit()

        if request.language == 'en':
            flash("Registration successful. After approval from the association, you will receive an email with your membership card.", "success")
        else:
            flash("Registrazione Avvenuta. Dopo l'approvazione dell'associazione riceverai una mail con la tessera associativa.", "success")

        return redirect(url_for('index'))


    except Exception as e:
        print("Errore durante l'inserimento:", e)
        return f"Si è verificato un errore durante l'inserimento dei dati: {e}", 500

    finally:
        db_session.close()



@app.route('/login', methods=['GET', 'POST'])
def login():
    pin = os.getenv('PIN')  
    if request.method == 'POST':
        input_pin = request.form['pin']
        if input_pin == pin:  
            session['authenticated'] = True 
            return redirect(url_for('view_users'))
        else:
            return "PIN errato!", 403
    return render_template('login.html')  

@app.route('/view_users')
def view_users():
    if 'authenticated' not in session:
        return redirect(url_for('login'))

    db_session = Session()
    try:
        # Ottieni i parametri di filtro dalla query string
        approvato = request.args.get('approvato', 'NO')
        inviato = request.args.get('inviato')
        manuale = request.args.get('manuale')

        query = db_session.query(User)

        # Filtro per approvato: solo applicato se il valore è diverso da ''
        if approvato:
            if approvato == 'SI':  # Filtro per approvato 'SI'
                query = query.filter(User.approvato == 'SI')
            elif approvato == 'NO':  # Filtro per approvato 'NO'
                query = query.filter(User.approvato == 'NO')

        # Altri filtri per inviato e manuale
        if inviato:
            query = query.filter(User.inviato == inviato)
        if manuale:
            query = query.filter(User.manuale == manuale)

        # Recupera gli utenti
        users = query.order_by(User.nome, User.cognome).all()

        total_users = db_session.query(User).filter(
            User.approvato == 'SI',
            User.inviato == 'SI').count()
        total_users_not_approved = db_session.query(User).filter(User.approvato == 'NO').count()
        approved_but_not_sent = db_session.query(User).filter(
            User.approvato == 'SI',
            User.inviato == 'NO').count()


        return render_template('view_users.html', users=users, total_users=total_users,total_users_not_approved=total_users_not_approved, approved_but_not_sent=approved_but_not_sent)
    except Exception as e:
        print("Errore nel recupero degli utenti:", e)
        return f"Si è verificato un errore nel recupero degli utenti: {e}", 500
    finally:
        db_session.close()     


@app.route('/update_card_number/<int:user_id>', methods=['POST'])
def update_card_number(user_id):
    db_session = Session()
    try:
        user = db_session.query(User).get(user_id)
        if user:
            numero_tessera = request.form['numero_tessera']
            if numero_tessera:
                user.numero_tessera = numero_tessera 
            else:
                max_numero_tessera = db_session.query(User).filter(User.numero_tessera.isnot(None)).order_by(User.numero_tessera.desc()).first()
                if max_numero_tessera:
                    user.numero_tessera = max_numero_tessera.numero_tessera + 1
                else:
                    user.numero_tessera = 1  
            db_session.commit()
        else:
            return "Utente non trovato.", 404 
    except Exception as e:
        print("Errore nell'aggiornamento del numero di tessera:", e)
        return f"Si è verificato un errore nell'aggiornamento del numero di tessera: {e}", 500
    finally:
        db_session.close()
    return redirect(url_for('view_users'))

@app.route('/update_approval/<int:user_id>', methods=['POST'])
def update_approval(user_id):
    db_session = Session()
    try:
        user = db_session.query(User).get(user_id)
        if user:
            user.approvato = "SI"  
            db_session.commit()
        else:
            return "Utente non trovato.", 404 
    except Exception as e:
        print("Errore nell'aggiornamento dell'approvazione:", e)
        return f"Si è verificato un errore nell'aggiornamento dell'approvazione: {e}", 500 
    finally:
        db_session.close()
    return redirect(url_for('view_users'))

@app.route('/update_manual/<int:user_id>', methods=['POST'])
def update_manual(user_id):
    db_session = Session()
    try:
        user = db_session.query(User).get(user_id)
        if user:
            user.manuale = request.form['manuale']  
            db_session.commit()
        else:
            return "Utente non trovato.", 404
    except Exception as e:
        print("Errore nell'aggiornamento del manuale:", e)
        return f"Si è verificato un errore nell'aggiornamento del manuale: {e}", 500
    finally:
        db_session.close()
    return redirect(url_for('view_users'))

@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    db_session = Session()
    try:
        user = db_session.query(User).get(user_id)
        if user:
            # Se l'utente esiste, lo eliminiamo
            db_session.delete(user)
            db_session.commit()
        else:
            return "Utente non trovato.", 404
    except Exception as e:
        print("Errore nella cancellazione dell'utente:", e)
        return f"Si è verificato un errore nella cancellazione dell'utente: {e}", 500
    finally:
        db_session.close()

    return redirect(url_for('view_users'))           

#STATISTICS
@app.route('/statistics', methods=['GET'])
def statistics():
    # Renderizza il template, passando la selezione del grafico se esiste
    return render_template('statistics.html')

# Connessione al database
def get_dataframe():
    db_session = Session()  # Create a new session
    try:
        query = "SELECT * FROM users;"
        # You can use pandas to execute the query through the session
        df = pd.read_sql(query, db_session.bind)  # Use db_session.bind as the connection
        df['data_registrazione'] = pd.to_datetime(df['data_registrazione'])
        return df
    except Exception as e:
        print(f"Errore nel recupero dei dati: {e}")
        return None
    finally:
        db_session.close()  # Always close the session when done

# Funzione per generare il grafico (assicurandoci che venga eseguita nel thread principale)
# Funzione per generare il grafico (assicurandoci che venga eseguita nel thread principale)
def generate_plot():
    plt.figure(figsize=(12, 6))

@app.route('/registrazioni_giornaliere_chart')
def registrazioni_giornaliere_chart():
    df = get_dataframe()
    registrazioni_giornaliere = df.groupby(df['data_registrazione'].dt.date).size()

    # Creiamo il grafico nel thread principale
    generate_plot()
    plt.plot(registrazioni_giornaliere.index, registrazioni_giornaliere.values, marker='o')
    plt.title("Andamento delle Registrazioni Giornaliere")
    plt.xlabel("Data")
    plt.ylabel("Numero di Registrazioni")

    xticks_labels = [
    f"{data.strftime('%Y-%m-%d')} ({data.strftime('%A')})"
    for data in registrazioni_giornaliere.index
    ]
    plt.xticks(ticks=registrazioni_giornaliere.index, labels=xticks_labels, rotation=45)

    plt.grid()

    # Modifica i margini
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

    # Applica tight_layout (se necessario)
    plt.tight_layout()
    #time.sleep(1)
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return make_response(img.read(), {'Content-Type': 'image/png'})

@app.route('/variazioni_percentuali_chart')
def variazioni_percentuali_chart():
    df = get_dataframe()
    registrazioni_giornaliere = df.groupby(df['data_registrazione'].dt.date).size().pct_change() * 100

    # Creiamo il grafico nel thread principale
    generate_plot()
    plt.plot(registrazioni_giornaliere.index, registrazioni_giornaliere.values, marker='o')
    plt.title("Andamento Percentuale delle Registrazioni")
    plt.xlabel("Data")
    plt.ylabel("Variazione %")

    xticks_labels = [
    f"{data.strftime('%Y-%m-%d')} ({data.strftime('%A')})"
    for data in registrazioni_giornaliere.index
    ]
    plt.xticks(ticks=registrazioni_giornaliere.index, labels=xticks_labels, rotation=45)

    plt.grid()
    plt.axhline(0, linestyle='--', color='red')

    # Modifica i margini
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

    # Applica tight_layout (se necessario)
    plt.tight_layout()
    #time.sleep(1)
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return make_response(img.read(), {'Content-Type': 'image/png'})

@app.route('/distribuzione_sesso_chart')
def distribuzione_sesso_chart():
    df = get_dataframe()
    n_uomini = df[df["sesso"] == "Maschile"].shape[0]
    n_donne = df[df["sesso"] == "Femminile"].shape[0]
    n_altro = df[df["sesso"] == "Altro"].shape[0]

    categorie = ['Uomini', 'Donne', 'Altro']
    valori = [n_uomini, n_donne, n_altro]

    # Creiamo il grafico nel thread principale
    generate_plot()
    plt.bar(categorie, valori, color=['lightblue', 'pink', 'grey'])
    plt.title("Distribuzione Sesso")
    plt.ylabel("Numero di Persone")
    for i, valore in enumerate(valori):
        plt.text(i, valore + 0.5, str(valore), ha='center')

    # Modifica i margini
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

    # Applica tight_layout (se necessario)
    plt.tight_layout()
    #time.sleep(1)
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return make_response(img.read(), {'Content-Type': 'image/png'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000)) 
    print(f"Starting app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)

