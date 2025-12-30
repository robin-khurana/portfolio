import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE = 'goals.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                completed BOOLEAN NOT NULL CHECK (completed IN (0, 1)),
                type TEXT NOT NULL CHECK (type IN ('daily', 'long-term'))
            )
        ''')
        conn.commit()

@app.route('/api/goals', methods=['GET'])
def get_goals():
    goal_type = request.args.get('type')
    with get_db() as conn:
        if goal_type:
            goals = conn.execute('SELECT * FROM goals WHERE type = ?', (goal_type,)).fetchall()
        else:
            goals = conn.execute('SELECT * FROM goals').fetchall()
        return jsonify([dict(row) for row in goals])

@app.route('/api/goals', methods=['POST'])
def add_goal():
    data = request.json
    text = data.get('text')
    goal_type = data.get('type')
    if not text or not goal_type:
        return jsonify({'error': 'Missing text or type'}), 400
    
    with get_db() as conn:
        cursor = conn.execute(
            'INSERT INTO goals (text, completed, type) VALUES (?, ?, ?)',
            (text, 0, goal_type)
        )
        conn.commit()
        return jsonify({'id': cursor.lastrowid, 'text': text, 'completed': 0, 'type': goal_type}), 201

@app.route('/api/goals/<int:goal_id>', methods=['PUT'])
def toggle_goal(goal_id):
    data = request.json
    completed = data.get('completed')
    
    with get_db() as conn:
        conn.execute(
            'UPDATE goals SET completed = ? WHERE id = ?',
            (1 if completed else 0, goal_id)
        )
        conn.commit()
        return jsonify({'status': 'success'})

@app.route('/api/goals/<int:goal_id>', methods=['DELETE'])
def delete_goal(goal_id):
    with get_db() as conn:
        conn.execute('DELETE FROM goals WHERE id = ?', (goal_id,))
        conn.commit()
        return jsonify({'status': 'success'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
