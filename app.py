from flask import Flask, render_template_string, request, redirect
from datetime import datetime
import csv

app = Flask(__name__)

# HTML veidne formas ievadei un rezultāta izvadei
html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Rēķinu ģenerators</title>
</head>
<body>
    <h1>Rēķinu ģenerators koka lādītēm</h1>
    <form method="POST" action="/generate">
        <label>Klienta vārds:</label><br>
        <input type="text" name="klients" required><br><br>
        
        <label>Veltījuma teksts:</label><br>
        <input type="text" name="veltijums" required><br><br>
        
        <label>Lādītes platums (mm):</label><br>
        <input type="number" name="platums" required><br><br>

        <label>Lādītes garums (mm):</label><br>
        <input type="number" name="garums" required><br><br>

        <label>Lādītes augstums (mm):</label><br>
        <input type="number" name="augstums" required><br><br>
        
        <label>Kokmateriāla cena (EUR/m²):</label><br>
        <input type="number" step="0.01" name="materiala_cena" required><br><br>
        
        <input type="submit" value="Izveidot rēķinu">
    </form>

    {% if rekins %}
        <h2>Rēķins:</h2>
        <p><strong>Izveidošanas laiks:</strong> {{ rekins.laiks }}</p>
        <p><strong>Klients:</strong> {{ rekins.klients }}</p>
        <p><strong>Veltījums:</strong> {{ rekins.veltijums }}</p>
        <p><strong>Izmērs:</strong> {{ rekins.izmers[0] }}mm x {{ rekins.izmers[1] }}mm x {{ rekins.izmers[2] }}mm</p>
        <p><strong>Summa (ar PVN):</strong> {{ rekins.rekina_summa }} EUR</p>
    {% endif %}
</body>
</html>
'''

class Rekins:
    def __init__(self, klients, veltijums, izmers, materiala_cena):
        self.laiks = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.klients = klients
        self.veltijums = veltijums
        self.izmers = izmers
        self.materiala_cena = materiala_cena
        self.rekina_summa = self.aprekins()

    def aprekins(self):
        darba_samaksa = 15
        PVN = 21
        platums, garums, augstums = self.izmers
        produkta_cena = (len(self.veltijums) * 1.2) + \
                        ((platums/100) * (garums/100) * (augstums/100)) / 3 * self.materiala_cena
        PVN_summa = (produkta_cena + darba_samaksa) * PVN / 100
        return round(produkta_cena + darba_samaksa + PVN_summa, 2)

    def saglabat_csv(self):
        faila_nosaukums = f"rekins_{self.klients}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        with open(faila_nosaukums, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Laiks", "Klients", "Veltijums", "Izmers", "Summa"])
            writer.writerow([self.laiks, self.klients, self.veltijums, 
                             f"{self.izmers[0]}x{self.izmers[1]}x{self.izmers[2]}", 
                             f"{self.rekina_summa} EUR"])

@app.route('/', methods=['GET'])
def home():
    return render_template_string(html_template)

@app.route('/generate', methods=['POST'])
def generate():
    klients = request.form['klients']
    veltijums = request.form['veltijums']
    platums = int(request.form['platums'])
    garums = int(request.form['garums'])
    augstums = int(request.form['augstums'])
    materiala_cena = float(request.form['materiala_cena'])

    rekins = Rekins(klients, veltijums, [platums, garums, augstums], materiala_cena)
    rekins.saglabat_csv()

    return render_template_string(html_template, rekins=rekins)

if __name__ == '__main__':
    app.run(debug=True)
