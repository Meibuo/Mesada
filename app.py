from flask import Flask, render_template, request, jsonify, session
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = '30591bbfa70ae38582897d226608fd99'

# Dados dos jogadores
players = {}

class Player:
    def __init__(self, nome):
        self.nome = nome
        self.level = 1
        self.xp = 0
        self.xp_need = 100
        self.mesada = 0
        self.tasks_completed = 0
        self.skills = {
            'responsabilidade': 1,
            'organizacao': 1,
            'economia': 1
        }
        self.inventory = []
        self.last_login = datetime.now().isoformat()
    
    def add_xp(self, amount):
        self.xp += amount
        # Verificar level up
        while self.xp >= self.xp_need:
            self.level_up()
    
    def level_up(self):
        self.level += 1
        self.xp -= self.xp_need
        self.xp_need = int(self.xp_need * 1.5)  # Aumenta a XP necessária
        self.mesada += 5.00  # Aumenta mesada a cada level
        return f"🎉 Level UP! Agora você é nível {self.level}!"
    
    def complete_task(self, task_name, difficulty):
        xp_reward = difficulty * 25
        money_reward = difficulty * 2.00
        
        self.add_xp(xp_reward)
        self.mesada += money_reward
        self.tasks_completed += 1
        
        return {
            'xp': xp_reward,
            'money': money_reward,
            'message': f'Task "{task_name}" completa! +{xp_reward} XP +R${money_reward:.2f}'
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_player', methods=['POST'])
def create_player():
    nome = request.json['nome']
    players[nome] = Player(nome)
    return jsonify({'success': True, 'player': players[nome].__dict__})

@app.route('/complete_task', methods=['POST'])
def complete_task():
    nome = request.json['nome']
    task_name = request.json['task_name']
    difficulty = request.json['difficulty']
    
    if nome in players:
        result = players[nome].complete_task(task_name, difficulty)
        return jsonify({'success': True, 'result': result, 'player': players[nome].__dict__})
    
    return jsonify({'success': False})

@app.route('/battle', methods=['POST'])
def battle():
    nome = request.json['nome']
    battle_difficulty = request.json['difficulty']
    
    if nome in players:
        player = players[nome]
        
        # Simular batalha - chance de sucesso baseada no level
        success_chance = min(0.8, player.level * 0.1)
        victory = random.random() < success_chance
        
        if victory:
            xp_reward = battle_difficulty * 50
            money_reward = battle_difficulty * 5.00
            player.add_xp(xp_reward)
            player.mesada += money_reward
            
            return jsonify({
                'success': True,
                'victory': True,
                'message': f'🏆 Vitória na batalha! +{xp_reward} XP +R${money_reward:.2f}',
                'player': player.__dict__
            })
        else:
            return jsonify({
                'success': True,
                'victory': False,
                'message': '💀 Derrota na batalha! Tente novamente!',
                'player': player.__dict__
            })
    
    return jsonify({'success': False})

@app.route('/dashboard/<player_name>')
def dashboard(player_name):
    if player_name in players:
        return render_template('dashboard.html', player=players[player_name])
    return "Jogador não encontrado!"

if __name__ == '__main__':
    app.run(debug=True)