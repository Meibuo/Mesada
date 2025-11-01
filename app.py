from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Dados simples (em produção use banco de dados)
mesadas = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/adicionar_mesada', methods=['POST'])
def adicionar_mesada():
    try:
        nome = request.form['nome']
        valor = float(request.form['valor'])
        
        mesadas[nome] = {
            'valor': valor,
            'saldo': valor,
            'transacoes': []
        }
        
        return jsonify({'success': True})
    except:
        return jsonify({'success': False})

@app.route('/registrar_gasto', methods=['POST'])
def registrar_gasto():
    try:
        nome = request.form['nome']
        valor = float(request.form['valor'])
        descricao = request.form['descricao']
        
        if nome in mesadas and mesadas[nome]['saldo'] >= valor:
            mesadas[nome]['saldo'] -= valor
            mesadas[nome]['transacoes'].append({
                'tipo': 'gasto',
                'valor': valor,
                'descricao': descricao
            })
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Saldo insuficiente ou usuário não encontrado'})
    except:
        return jsonify({'success': False})

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', mesadas=mesadas)

if __name__ == '__main__':
    app.run(debug=True)