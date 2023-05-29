from flask import Flask, render_template, request, session
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Possible colors for combinations
colores = {
    "Yellow": "#ffff00",
    "Black": "#000000",
    "Green": "#00ff00",
    "Red": "#ff0000",
    "Cyan": "#00ffff",
    "White": "#ffffff",
    "Purple": "#ff00ff",
    "Blue": "#0000ff"
}

# Generates a new secret combination
def nuevo_secreto(colores):
    secreto = []
    for _ in range(4):
        secreto.append(random.choice(list(colores.values())))
    return secreto

# Calculates the results of a guess
def calcula_resultado(intento, secreto):
    heridos = 0
    muertos = 0
    aciertos = [None] * 4
    indices_aciertos = []
    indices_misplaced = []
    secreto_copy = secreto.copy()

    for i in range(4):
        if intento[i] == secreto_copy[i]:
            muertos += 1
            aciertos[i] = True
            indices_aciertos.append(i)
            secreto_copy[i] = None  # Mark this position as matched to avoid counting it twice
            continue

        if intento[i] in secreto_copy:
            heridos += 1
            aciertos[i] = False
            indices_misplaced.append(secreto_copy.index(intento[i]))  # Find the index of the misplaced color in secreto_copy
            secreto_copy[secreto_copy.index(intento[i])] = None  # Mark this position as matched to avoid counting it twice

    resultado = {
        "muertos": muertos,
        "heridos": heridos,
        "aciertos": aciertos,
        "indices_aciertos": indices_aciertos,
        "indices_misplaced": indices_misplaced
    }

    session["intentos"].append({"intento": intento, "resultado": resultado})

    # If there are more than five attempts, remove the oldest one
    if len(session["intentos"]) > 5:
        session["intentos"].pop(0)

    return resultado


# Generates the next machine guess
def genera_intento_maquina(intento_anterior, resultado_anterior, colores_posibles):
    maquina_intento = []

    # If no previous aciertos, select four random colors
    if resultado_anterior["muertos"] == 0:
        for _ in range(4):
            maquina_intento.append(random.choice(list(colores_posibles.values())))
        return maquina_intento

    # If previous aciertos, choose new colors randomly
    colores_acertados = [intento_anterior[i] for i in range(4) if resultado_anterior["aciertos"][i] is True]
    num_colores_nuevos = 4 - len(colores_acertados)
    for _ in range(num_colores_nuevos):
        maquina_intento.append(random.choice(list(colores_posibles.values())))
    for color in colores_acertados:
        maquina_intento.append(color)
    random.shuffle(maquina_intento)
    return maquina_intento


@app.route('/', methods=['GET', 'POST'])
def play_game():
    if 'intentos' not in session:
        session['intentos'] = []

    secreto = session.get('secreto', None)
    if not secreto:
        secreto = nuevo_secreto(colores)
        session['secreto'] = secreto.copy()

    if request.method == 'POST':
        if len(session['intentos']) % 2 != 0:
            maquina_intento = []
            if len(session['intentos']) == 1:
                for _ in range(4):
                    maquina_intento.append(random.choice(list(colores.values())))
            else:
                anterior = session['intentos'][-2]
                maquina_intento = genera_intento_maquina(anterior['intento'], anterior['resultado'], colores)
            maquina_resultado = calcula_resultado(maquina_intento, secreto)
            session['intentos'].append({'intento': maquina_intento, 'resultado': maquina_resultado})

            if maquina_resultado['muertos'] == 4:
                return render_template('index.html', mensaje=f'¡La máquina ha acertado en {len(session["intentos"])} intentos!')

        else:
            intento = [request.form.get(f'intento[{i}]') for i in range(4)]
            resultado = calcula_resultado(intento, secreto)
            session['intentos'].append({'intento': intento, 'resultado': resultado})

    return render_template('index.html', colores=colores, intentos=session.get('intentos', []), secreto=secreto)

@app.route('/reiniciar', methods=['POST'])
def restart_game():
    session.clear()
    return render_template('index.html', colores=colores)


if __name__ == '__main__':
    app.run()
