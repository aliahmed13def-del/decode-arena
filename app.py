from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import sqlite3
import hashlib
from datetime import datetime
from database import get_db, init_db

app = Flask(__name__)
app.secret_key = 'scavenger_hunt_secret_2026'
ADMIN_KEY = 'admin2026'  # change this to something secret!
TOTAL_STAGES = 11

# ─────────────────────────────
# HELPER — get event status
# ─────────────────────────────
def get_event():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM event_control WHERE id=1')
    event = c.fetchone()
    conn.close()
    return event

def get_time_remaining():
    event = get_event()
    if not event or event['status'] == 'waiting':
        return event['duration_seconds'], 'waiting'
    if event['status'] == 'ended':
        return 0, 'ended'
    if event['status'] == 'running':
        started = datetime.strptime(event['started_at'], '%Y-%m-%d %H:%M:%S.%f')
        elapsed = (datetime.now() - started).total_seconds()
        remaining = max(0, event['duration_seconds'] - elapsed)
        if remaining <= 0:
            # auto end event
            conn = get_db()
            c = conn.cursor()
            c.execute('''UPDATE event_control
                         SET status="ended", ended_at=?
                         WHERE id=1''', (datetime.now(),))
            conn.commit()
            conn.close()
            return 0, 'ended'
        return int(remaining), 'running'
    return event['duration_seconds'], event['status']


# ─────────────────────────────
# HELPER — build stage_names dict for a trail
# ─────────────────────────────
def get_stage_names(trail):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT stage, question FROM puzzles WHERE trail=? ORDER BY stage ASC', (trail,))
    stage_names = {}
    for row in c.fetchall():
        q = row['question']
        first_line = q.split('\n')[0] if '\n' in q else q
        if '\u2014 ' in first_line:
            name = first_line.split('\u2014 ', 1)[1].strip()
        elif 'BOSS' in first_line:
            name = 'Protocol Zero'
        else:
            name = 'Stage ' + str(row['stage'])
        stage_names[row['stage']] = name
    conn.close()
    return stage_names

# ─────────────────────────────
# LOGIN
# ─────────────────────────────
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        team_name = request.form['team_name'].strip().upper()
        password  = request.form['password'].strip()
        hashed    = hashlib.md5(password.encode()).hexdigest()

        conn = get_db()
        c    = conn.cursor()
        c.execute('SELECT * FROM teams WHERE team_name=? AND password=?',
                  (team_name, hashed))
        team = c.fetchone()
        conn.close()

        if team:
            if team['disqualified']:
                error = 'Your team has been disqualified.'
            else:
                session['team_id']   = team['id']
                session['team_name'] = team['team_name']
                session['trail']     = team['trail']
                return redirect(url_for('dashboard'))
        else:
            error = 'Wrong team name or password.'

    return render_template('login.html', error=error)

# ─────────────────────────────
# DASHBOARD
# ─────────────────────────────
@app.route('/dashboard')
def dashboard():
    if 'team_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    c    = conn.cursor()

    c.execute('SELECT * FROM teams WHERE id=?', (session['team_id'],))
    team = c.fetchone()

    if team['disqualified']:
        session.clear()
        return redirect(url_for('login'))

    c.execute('SELECT * FROM puzzles WHERE trail=? AND stage=?',
              (team['trail'], team['current_stage']))
    puzzle = c.fetchone()

    c.execute('''SELECT * FROM submissions
                 WHERE team_id=?
                 ORDER BY submitted_at DESC LIMIT 10''',
              (session['team_id'],))
    logs = c.fetchall()
    conn.close()

    stage_names = get_stage_names(team['trail'])
    remaining, status = get_time_remaining()

    return render_template('dashboard.html',
                           team=team,
                           puzzle=puzzle,
                           logs=logs,
                           time_remaining=remaining,
                           event_status=status,
                           stage_names=stage_names)

# ─────────────────────────────
# TIMER API — called by dashboard every second
# ─────────────────────────────
@app.route('/api/timer')
def api_timer():
    remaining, status = get_time_remaining()
    return jsonify({'remaining': remaining, 'status': status})

# ─────────────────────────────
# SUBMIT
# ─────────────────────────────
@app.route('/submit', methods=['POST'])
def submit():
    if 'team_id' not in session:
        return redirect(url_for('login'))

    # block submissions if event not running
    remaining, status = get_time_remaining()
    if status == 'waiting':
        _team_w = get_team()
        return render_template('dashboard.html',
                               team=_team_w,
                               puzzle=get_puzzle(),
                               logs=[],
                               message='Hunt has not started yet!',
                               is_correct=False,
                               time_remaining=remaining,
                               event_status=status,
                               stage_names=get_stage_names(_team_w['trail']))
    if status == 'ended':
        _team_e = get_team()
        return render_template('dashboard.html',
                               team=_team_e,
                               puzzle=get_puzzle(),
                               logs=[],
                               message='Hunt has ended! No more submissions.',
                               is_correct=False,
                               time_remaining=0,
                               event_status=status,
                               stage_names=get_stage_names(_team_e['trail']))

    submitted = request.form['answer'].strip().upper()

    conn = get_db()
    c    = conn.cursor()

    c.execute('SELECT * FROM teams WHERE id=?', (session['team_id'],))
    team = c.fetchone()

    c.execute('SELECT * FROM puzzles WHERE trail=? AND stage=?',
              (team['trail'], team['current_stage']))
    puzzle = c.fetchone()

    if not puzzle:
        conn.close()
        return redirect(url_for('dashboard'))

    correct    = puzzle['answer'].strip().upper()
    is_correct = submitted == correct

    c.execute('''INSERT INTO submissions
                 (team_id, stage, answer_given, is_correct)
                 VALUES (?,?,?,?)''',
              (session['team_id'], team['current_stage'],
               submitted, 1 if is_correct else 0))

    if is_correct:
        # time based scoring
        elapsed_mins = (10800 - remaining) / 60
        if elapsed_mins <= 30:
            earned = puzzle['points']
        elif elapsed_mins <= 90:
            earned = puzzle['points'] * 0.8
        elif elapsed_mins <= 150:
            earned = puzzle['points'] * 0.6
        else:
            earned = puzzle['points'] * 0.5

        c.execute('''UPDATE teams
                     SET score=?, current_stage=?, puzzles_solved=?
                     WHERE id=?''',
                  (team['score'] + earned,
                   team['current_stage'] + 1,
                   team['puzzles_solved'] + 1,
                   session['team_id']))
    else:
        # negative marking — deduct 0.1 per wrong answer (floor at 0)
        new_score = max(0, team['score'] - 0.1)
        c.execute('UPDATE teams SET score=? WHERE id=?',
                  (new_score, session['team_id']))

    conn.commit()

    c.execute('SELECT * FROM teams WHERE id=?', (session['team_id'],))
    team = c.fetchone()

    c.execute('SELECT * FROM puzzles WHERE trail=? AND stage=?',
              (team['trail'], team['current_stage']))
    puzzle = c.fetchone()

    c.execute('''SELECT * FROM submissions WHERE team_id=?
                 ORDER BY submitted_at DESC LIMIT 10''',
              (session['team_id'],))
    logs = c.fetchall()
    conn.close()

    message = '✅ Correct! Next stage unlocked.' if is_correct else '❌ Wrong answer. Try again!'

    return render_template('dashboard.html',
                           team=team,
                           puzzle=puzzle,
                           logs=logs,
                           message=message,
                           is_correct=is_correct,
                           time_remaining=remaining,
                           event_status=status,
                           stage_names=get_stage_names(team['trail']))

# ─────────────────────────────
# LEADERBOARD
# ─────────────────────────────
@app.route('/leaderboard')
def leaderboard():
    conn = get_db()
    c    = conn.cursor()
    c.execute('''SELECT team_name, trail, score, puzzles_solved
                 FROM teams
                 WHERE disqualified=0
                 ORDER BY score DESC, puzzles_solved DESC''')
    teams = c.fetchall()
    conn.close()
    remaining, status = get_time_remaining()
    return render_template('leaderboard.html',
                           teams=teams,
                           session=session,
                           time_remaining=remaining,
                           event_status=status)

# ─────────────────────────────
# ADMIN PAGE
# ─────────────────────────────
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.args.get('key') != ADMIN_KEY:
        return '<h2 style="font-family:monospace;color:red;padding:40px">Access Denied</h2>', 403

    conn = get_db()
    c    = conn.cursor()

    # handle admin actions
    action = request.form.get('action')

    if action == 'start':
        c.execute('''UPDATE event_control
                     SET status="running", started_at=?
                     WHERE id=1''', (datetime.now(),))
        conn.commit()

    elif action == 'stop':
        c.execute('''UPDATE event_control
                     SET status="ended", ended_at=?
                     WHERE id=1''', (datetime.now(),))
        conn.commit()

    elif action == 'reset_event':
        c.execute('''UPDATE event_control
                     SET status="waiting", started_at=NULL,
                     ended_at=NULL WHERE id=1''')
        conn.commit()

    elif action == 'disqualify':
        team_id = request.form.get('team_id')
        c.execute('UPDATE teams SET disqualified=1 WHERE id=?', (team_id,))
        conn.commit()

    elif action == 'reinstate':
        team_id = request.form.get('team_id')
        c.execute('UPDATE teams SET disqualified=0 WHERE id=?', (team_id,))
        conn.commit()

    elif action == 'reset_team':
        team_id = request.form.get('team_id')
        c.execute('''UPDATE teams SET score=0, puzzles_solved=0,
                     current_stage=1 WHERE id=?''', (team_id,))
        c.execute('DELETE FROM submissions WHERE team_id=?', (team_id,))
        conn.commit()

    elif action == 'reset_all':
        c.execute('''UPDATE teams SET score=0, puzzles_solved=0,
                     current_stage=1''')
        c.execute('DELETE FROM submissions')
        conn.commit()

    # fetch all data
    c.execute('''SELECT * FROM teams
                 ORDER BY score DESC, puzzles_solved DESC''')
    teams = c.fetchall()

    c.execute('SELECT * FROM event_control WHERE id=1')
    event = c.fetchone()

    c.execute('''SELECT s.*, t.team_name, t.trail
                 FROM submissions s
                 JOIN teams t ON s.team_id = t.id
                 ORDER BY s.submitted_at DESC LIMIT 50''')
    submissions = c.fetchall()

    conn.close()
    remaining, status = get_time_remaining()

    return render_template('admin.html',
                           teams=teams,
                           event=event,
                           submissions=submissions,
                           time_remaining=remaining,
                           event_status=status,
                           admin_key=ADMIN_KEY)

# ─────────────────────────────
# LOGOUT
# ─────────────────────────────
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ─────────────────────────────
# RUN
# ─────────────────────────────
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)