import sqlite3
import hashlib
import os

# ══════════════════════════════════════════════════════════════════
#  ON FINAL DAY — ONLY EDIT THIS SECTION
#  Change team names, passwords, and trails below.
#  Then run:  python load_data.py
#  That's it. Nothing else to touch.
# ══════════════════════════════════════════════════════════════════

TEAMS = [
    # (team_name,      password,    trail)
    # ── GREEN TRAIL ──────────────────────────
    ('TEAM_ALPHA',   'green123',  'Green'),
    ('TEAM_BETA',    'green456',  'Green'),
    ('TEAM_GAMMA',   'green789',  'Green'),
    ('TEAM_DELTA',   'green321',  'Green'),
    ('TEAM_ECHO',    'green654',  'Green'),
    ('TEAM_FOXTROT', 'green987',  'Green'),

    # ── BLUE TRAIL ───────────────────────────
    ('TEAM_GULF',    'blue123',   'Blue'),
    ('TEAM_HOTEL',   'blue456',   'Blue'),
    ('TEAM_INDIA',   'blue789',   'Blue'),
    ('TEAM_JULIET',  'blue321',   'Blue'),
    ('TEAM_KILO',    'blue654',   'Blue'),
    ('TEAM_LIMA',    'blue987',   'Blue'),

    # ── RED TRAIL ────────────────────────────
    ('TEAM_MIKE',    'red123',    'Red'),
    ('TEAM_NOVEMBER','red456',    'Red'),
    ('TEAM_OSCAR',   'red789',    'Red'),
    ('TEAM_PAPA',    'red321',    'Red'),
    ('TEAM_QUEBEC',  'red654',    'Red'),
    ('TEAM_ROMEO',   'red987',    'Red'),
    ('TEAM_SIERRA',  'red111',    'Red'),
    
]

# ══════════════════════════════════════════════════════════════════
#  PUZZLE DATA — update Google Drive links and answers here
# ══════════════════════════════════════════════════════════════════

PUZZLES = [

    # ────────────────────────────────────────────────
    # GREEN TRAIL — 10 stages + 1 boss
    # ────────────────────────────────────────────────

    ('Green', 1,
     'Stage 1 — First Signal\n\nYour first clue is waiting here:\nhttps://drive.google.com/drive/folders/1lqc7VKWiPVMtQnVgFWqAzawC-njKtnP4?usp=sharing\n\nDownload the file, decode it, and submit your answer below.',
     'NEXCORE SERVER ONE BREACHED TARGET IS POWERNODE ALPHA',
     10, 'The answer is buried deeper than it appears — look beyond the surface', 0),

    ('Green', 2,
     'Stage 2 — The Drop Point\n\nYour next clue:\nhttps://drive.google.com/drive/folders/169v7O9s3LctxySSXFN7-SaQZQ0W9Nmns?usp=sharing\n\nDecode and submit.',
     'ZERO HAS ENCRYPTED THE POWER GRID ACCESS CODE IS DARKNODE',
     10, 'Not everything is what it seems — peel back the layers carefully', 0),

    ('Green', 3,
     'Stage 3 — Physical Hunt\n\nYour teammate must find the physical clue on campus.\nThe location is revealed here:\nhttps://drive.google.com/drive/folders/1-UoLwGCKka9cfwH0V1PtVC_pFkZOJhKD?usp=sharing\n\nSolve the on-site puzzle and submit the answer.',
     'ZERO IS COMMUNICATING THROUGH ENCRYPTED CHANNEL FREQUENCY NINE',
     10, 'The clue will not come to you — someone must go find it', 1),

    ('Green', 4,
     'Stage 4 — The Cipher\n\nDecode this encrypted message:\nhttps://drive.google.com/drive/folders/1Xdz0Mk3rlXosFOP32hdSSZioOCZ4AGPa?usp=sharing\n\nSubmit the decoded answer below.',
     'ZERO SIGNATURE CONFIRMED NEXT TARGET BANKING SYSTEM DELTA',
     10, 'The message is scrambled — the key to unscrambling it is closer than you think', 0),

    ('Green', 5,
     'Stage 5 — CHECKPOINT ⚠️\n\nThis is a checkpoint stage. Choose carefully — one path leads forward, one leads to a dead end.\n\nOpen the clue:\nhttps://drive.google.com/drive/folders/1KTvEjluVVn8gJpUWRiNPCKZYMIZNRf27?usp=sharing\n\nSubmit: PATH A or PATH B + the decoded location.',
     'PATH A HOSPITAL MAINFRAME',
     10, 'Choose wisely — one path leads forward, the other leads nowhere', 0),

    ('Green', 6,
     'Stage 6 — The Archive\n\nA hidden message was found in a deleted file:\nhttps://drive.google.com/drive/folders/1R7kcQnPsmchz9NSmvj8qLJKteEbN-eH_?usp=sharing\n\nDecode and submit.',
     'ZERO LEFT A SIGNATURE IN THE IMAGE METADATA KEY IS GHOSTNET',
     10, 'The secret is hiding inside something else — dig deeper', 0),

    ('Green', 7,
     'Stage 7 — Physical Hunt 2\n\nYour second physical challenge awaits on campus.\nFind the location:\nhttps://drive.google.com/drive/folders/17QzoZi_rk_51WlQVANmuTo6ccWAM6-on?usp=sharing\n\nSolve on-site and submit.',
     'ZERO CORE LOCATION CONFIRMED SECTOR SEVEN NODE OMEGA',
     10, 'Divide and conquer — not everything can be solved from a screen', 1),

    ('Green', 8,
     'Stage 8 — The Hash\n\nA hash was found in the system logs:\nhttps://drive.google.com/drive/folders/1qzSowD6X52bgCsrWoWx0RpmXbQWxIyem?usp=sharing\nIdentify and crack it, then submit.',
     '6 9 18 5 23 1 12 12',
     10, 'The string looks broken — the right tool will reveal what it truly says', 0),

    ('Green', 9,
     'Stage 9 — Image Analysis\n\nAn image was posted online before the trail went cold.\nExamine it carefully:\nhttps://drive.google.com/drive/folders/1nmGu6YlXShR788s7CIDh2M1aVSZHbTVn?usp=sharing\n\nWhat is hidden inside? Submit your answer.',
     'ZERO IS IN THE MAINFRAME SHUT IT DOWN NOW',
     10, 'The image shows one thing, but hides another — look where no one usually looks', 0),

    ('Green', 10,
     'Stage 10 — The Final Piece\n\nOne last clue before the Boss Level.\nDecrypt this final transmission:\nhttps://drive.google.com/drive/folders/1iIB-Ii5fcXElX820qIKA8aV7keKTJVtd?usp=sharing\n\nThe answer unlocks the Boss Level.',
     'PROTOCOL ZERO INITIATED FINAL SEQUENCE BEGINS IN THREE MINUTES',
     10, 'Every skill you have picked up leads to this — trust the process', 0),

    ('Green', 11,
     '👾 BOSS LEVEL — Final Gateway\n\nYou have traced the trail to its end.\nThe final challenge awaits:\nhttps://drive.google.com/drive/folders/1d8SWLpihunFmPe0siS__lPjUIUqHAGfE?usp=sharing\n\nSolve the Boss puzzle and submit the final flag to win.',
     'PROTOCOL ZERO TERMINATED',
     19.6, 'This is the final lock — everything you have learned is the key', 0),


    # ────────────────────────────────────────────────
    # BLUE TRAIL — 10 stages + 1 boss
    # ────────────────────────────────────────────────

    ('Blue', 1,
     'Stage 1 — Signal Breach\n\n04:02 AM. CyberCom Network. ZERO breached the primary communication hub and left an encrypted status report on the compromised server. Our analysts intercepted it before it self-deleted. Decode it to confirm ZEROs position.\nhttps://drive.google.com/file/d/1Pr_vk3oZ9JXFKVu91gtxKWbDMRxsHuq5/view?usp=sharing\n\nDecode and submit your answer below.',
     'CYBERCOM NETWORK INFILTRATED ZERO IS INSIDE SECTOR BRAVO',
     10, 'The answer is hidden in plain sight — look more carefully', 0),

    ('Blue', 2,
     'Stage 2 — The Stolen Keys\n\n04:28 AM. ZERO has stolen the master encryption keys from the secure vault. Before the breach was detected, it transmitted this encoded message through a hidden channel. Decode it to find what ZERO took.\nhttps://drive.google.com/file/d/1RUzWZqjVhfk9t6nvL9u53X7R-ZUVjUsC/view?usp=sharing\n\nDecode and submit your answer below.',
     'ZERO HAS STOLEN THE ENCRYPTION KEYS ACCESS CODE IS SHADOWKEY',
     10, 'Not everything is what it seems — peel back the layers carefully', 0),

    ('Blue', 3,
     'Stage 3 — Phantom Documents\n\n05:11 AM. ZERO is actively decrypting classified documents using the stolen keys. This transmission was captured from its active session. The encryption key is hidden in Stage 2s answer — last word.\nhttps://drive.google.com/file/d/1sLQQFFl2qM3GdFH56TuI6ZLilP7ZtZhR/view?usp=sharing\n\nDecode and submit your answer below.',
     'ZERO IS USING STOLEN KEYS TO DECRYPT CLASSIFIED DOCUMENTS CODENAME PHANTOM',
     10, 'Someone needs to go out there — the answer will not decode itself', 1),

    ('Blue', 4,
     'Stage 4 — Firewall Down\n\n05:47 AM. ZERO has cracked the central firewall. This binary transmission was found embedded in the firewall logs moments before it went offline. Two layers protect the message.\nhttps://drive.google.com/file/d/1sqNPhc8P7DqSl_cK6Hxe-ksdEWttnkXm/view?usp=sharing\n\nDecode and submit your answer below.',
     'ZERO HAS CRACKED THE FIREWALL PASSWORD IS CIPHERLOCK',
     10, 'The message is scrambled — the key to unscrambling it is closer than you think', 0),

    ('Blue', 5,
     'Stage 5 — CHECKPOINT ⚠️\n\nZERO detected our surveillance and split its signal across two frequencies. Only one frequency carries the real target location. The other is a ghost signal designed to waste your time.\nhttps://drive.google.com/file/d/107Gqvp9MxVAKOZ633okxoiOMouZxsxYp/view?usp=sharing\n\nSubmit: PATH A or PATH B + decoded location.',
     'PATH A SATELLITE UPLINK',
     10, 'Think before you submit — one path is a trap', 0),

    ('Blue', 6,
     'Stage 6 — Dark Transmission\n\n06:14 AM. ZERO transmitted stolen data to an external server. Our packet sniffer caught this heavily encoded transmission. Two cipher layers protect the destination address.\nhttps://drive.google.com/file/d/1FJkaQK8CwjTLZjvGqy59MUnOp6eFmRwJ/view?usp=sharing\n\nDecode and submit your answer below.',
     'ZERO TRANSMITTED STOLEN DATA TO EXTERNAL SERVER ADDRESS GHOSTNODE',
     10, 'The output is scrambled using a zigzag pattern across 4 rails', 0),

    ('Blue', 7,
     'Stage 7 — The Upload\n\n06:52 AM. ZERO is actively uploading classified files to a dark web server. This Morse transmission was intercepted from its uplink channel — but the signal has been shifted to avoid detection.\nhttps://drive.google.com/file/d/1oOqJycsK3iNrhYYGQhuzcx8csALuk9XO/view?usp=sharing\n\nDecode and submit your answer below.',
     'ZERO IS UPLOADING CLASSIFIED FILES TO DARK WEB SERVER NINE',
     10, 'Decode Morse first — then apply Caesar shift', 1),

    ('Blue', 8,
     'Stage 8 — Hash Fingerprint\n\n07:03 AM. ZERO left a hash fingerprint in the satellite uplink registry — a remnant of its authentication bypass. Crack the hash, then encode the result to confirm the access key.\nhttps://drive.google.com/file/d/1gI_jQl44PwxTYBXSrCn1J3Bntz-jSU0F/view?usp=sharing\n\nDecode and submit your answer below.',
     '12 15 3 11 4 15 23 14',
     10, 'Crack the hash first, then convert each letter using A=1 B=2 ... Z=26', 0),

    ('Blue', 9,
     'Stage 9 — Core Coordinates\n\n07:31 AM. Our analysts traced ZEROs uplink signal back to its core node. This triple-encrypted transmission confirms the location. Three layers stand between you and the coordinates.\nhttps://drive.google.com/file/d/1Z-rrnWRimbNiqsHpQa_9iWV-CSow5xFP/view?usp=sharing\n\nDecode and submit your answer below.',
     'ZERO CORE NODE LOCATION CONFIRMED UPLINK STATION DELTA SEVEN',
     10, 'What you see is not all there is — something is concealed within', 0),

    ('Blue', 10,
     'Stage 10 — Final Sequence\n\n07:58 AM. ZERO has initiated its final upload sequence. This transmission was intercepted microseconds before the uplink completed. The key is hidden in Stage 3s answer — last word.\nhttps://drive.google.com/file/d/1iuHKWVTapBmvHsZIVtJREgjP10ySf7DP/view?usp=sharing\n\nDecode and submit your answer below.',
     'PROTOCOL ZERO FINAL SEQUENCE ACTIVE PREPARE TO TERMINATE',
     10, 'The binary is reversed — flip it first, then decode binary, then Vigenere with last word from Stage 3', 0),

    ('Blue', 11,
     '👾 BOSS LEVEL — Protocol Zero\n\nYou have traced ZEROs uplink to its core. The Cryptography Analysis Division has cracked every layer of ZEROs encryption. One final barrier remains. ZERO used its strongest encryption — three layers, two keys from your investigation.\nBreak it. End this.\nhttps://drive.google.com/file/d/11Eh5fKHWlnJIWvubG2i-9vnLGBqCaTKU/view?usp=sharing\n\nDecode and submit the final flag to win.',
     'CIPHER LOCK ENGAGED',
     19.6, 'The final gate — everything has led here', 0),


    # ────────────────────────────────────────────────
    # RED TRAIL — 10 stages + 1 boss
    # ────────────────────────────────────────────────

    ('Red', 1,
     'Stage 1 — Evidence Trail\n\n03:52 AM. Digital Forensics Division activated. ZERO has compromised the primary mainframe and left an encrypted status message in the system registry. Our team intercepted it before it was overwritten. Decode it to confirm the breach.\nhttps://drive.google.com/file/d/126QHA5Thv2m2cuB2bc0isbyKUEW0mEgI/view?usp=sharing\n\nDecode and submit your answer below.',
     'FORENSICS TEAM ONLINE ZERO HAS COMPROMISED MAINFRAME ALPHA',
     10, 'Numbers speak, but not directly. Convert each to its character, then remember: every face of a die has a partner. Walk the alphabet back by that many steps.', 0),

    ('Red', 2,
     'Stage 2 — The Backdoor\n\n04:19 AM. ZERO planted a backdoor in the central database before our team arrived. This encrypted transmission was found in the database commit logs. Two layers protect it. The key is the name of our division.\nhttps://drive.google.com/file/d/1HKZQVE5XqzM5xWr72W5YBOI83cAGTfm9/view?usp=sharing\n\nDecode and submit your answer below.',
     'ZERO PLANTED A BACKDOOR IN THE DATABASE ACCESS CODE IS REDKEY',
     10, 'Two locks, two keys. The first key is who you work for — use it to unscramble the order of the alphabet. The second key is a number every cryptographer knows by heart.', 0),

    ('Red', 3,
     'Stage 3 — Patient Zero\n\n04:58 AM. ZERO is exfiltrating sensitive patient records from a hospital server. This transmission was captured from the hospital network. Two cipher layers protect the location data.\nhttps://drive.google.com/file/d/1_KrA_G1gG2m99uBtmeVIAIu-MOLYDfG-/view?usp=sharing\n\nSolve on-site and submit your answer below.',
     'ZERO IS EXFILTRATING PATIENT RECORDS FROM HOSPITAL SERVER OMEGA',
     10, 'The numbers wear hexadecimal masks. Strip them off. What remains speaks in a mirror — A becomes Z, B becomes Y. Let the alphabet fold in half.', 1),

    ('Red', 4,
     'Stage 4 — Frequency Seven\n\n05:33 AM. ZERO\'s core signal has been detected on a specific frequency. Our forensics team captured this encoded transmission. Two layers protect the signal data. The key it reveals will be critical later.\nhttps://drive.google.com/file/d/1regeTR_xj5xxsX_FWE2O7lAc4ZqGQmnC/view?usp=sharing\n\nDecode and submit your answer below.',
     'ZERO CORE SIGNAL DETECTED AT FREQUENCY SEVEN KEY IS IRONWALL',
     10, 'The internets favourite disguise wraps the outside. Once unwrapped, the letters didnt disappear — they were redistributed. Think of a fence with three posts. Read across, not diagonally.', 0),

    ('Red', 5,
     'Stage 5 — CHECKPOINT — Two Paths ⚠️\n\nZERO has detected our forensics team closing in. It has created two decoy transmission channels to misdirect us. Our analysts have intercepted both signals. Only one leads to the real command center.\nhttps://drive.google.com/file/d/1i9AJ6xZGJAzx1vb3qvIWoxPvs1IQSJT7/view?usp=sharing\n\nSubmit: PATH A or PATH B + decoded location.',
     'PATH A COMMAND CENTER',
     10, 'Path A hides behind 0s and 1s, then slid 8 steps too far along the alphabet — slide them back.Path B was ROT-ted, then walked backwards. Only one path leads somewhere real.', 0),

    ('Red', 6,
     'Stage 6 — Military Files\n\n06:07 AM. ZERO has breached classified military files. This Morse transmission was intercepted from the military network — but ZERO encrypted it before transmitting. Two layers to crack.\nhttps://drive.google.com/file/d/1PVe5OflEkVZSXmymocEz-PtZL87NSur7/view?usp=sharing\n\nDecode and submit your answer below.',
     'ZERO ACCESSED CLASSIFIED MILITARY FILES LOCATION IS NODE ELEVEN',
     10, 'Listen for the dots and dashes first — thats layer one. Once decoded, the message still lies: the alphabet has been flipped on its axis. First becomes last.', 0),

    ('Red', 7,
     'Stage 7 — Evidence Destruction\n\n06:44 AM. ZERO is actively destroying forensic evidence. This binary transmission was captured from the backup server moments before it went offline. The key is the last word from Stage 4\'s answer.\nhttps://drive.google.com/file/d/1wDIp_SvPKE_MetaiAT2LrlKCN911TZwn/view?usp=sharing\n\nDecode and submit your answer below.',
     'ZERO IS DESTROYING EVIDENCE BACKUP SERVER IS OFFLINE SECTOR FOUR',
     10, 'The 0s and 1s are a shell. Crack them open. Inside, the text is locked with a key you already found — the final word ZERO revealed in Stage 4. A polyalphabetic cipher guards it.', 1),

    ('Red', 8,
     'Stage 8 — Hash Evidence\n\n07:12 AM. ZERO left a hash fingerprint in the command center registry during its override attempt. Our forensics team recovered it. Crack the hash and encode the result to confirm the override key.\nhttps://drive.google.com/file/d/1KJzzezjT9Slps9-KtSX_KPryhQwrSHGF/view?usp=sharing\n\nDecode and submit your answer below.',
     '15 22 5 18 18 9 4 5',
     10, 'A fingerprint was left behind. Every hash has a source — find it. Then speak the answer in numbers: A is 1, Z is 26. No letters, only their positions.', 0),

    ('Red', 9,
     'Stage 9 — Final Node\n\n07:41 AM. Our forensics team has pinpointed ZERO\'s final node. This triple-encrypted transmission confirms the coordinates. Three layers stand between you and ZERO\'s location.\nhttps://drive.google.com/file/d/1o9KiOHjFt-gqPyJNO4Cc9kXeUgq32_kz/view?usp=sharing\n\nDecode and submit your answer below.',
     'ZERO FINAL NODE CONFIRMED FORENSICS DIVISION CLOSE IN NOW',
     10, 'Hex conceals the first layer. Beneath it, the letters ran a zigzag course across four tracks — put them back in order. Then slide the whole thing 11 steps back toward A.', 0),

    ('Red', 10,
     'Stage 10 — Countdown\n\n07:55 AM. ZERO has initiated its final countdown. This triple-encrypted transmission was captured microseconds before the sequence locked. Use the access code from Stage 2 as your key.\nhttps://drive.google.com/file/d/1nYV5B45URQp1z9AU6GJMjocMAN0m05gp/view?usp=sharing\n\nDecode and submit your answer below.',
     'PROTOCOL ZERO FINAL COUNTDOWN INITIATED TERMINATE IN SIXTY SECONDS',
     10, 'Binary is the outermost shell. The middle layer needs a password — the access code ZERO left behind in Stage 2. The final layer: let A and Z trade places, and so on down the line.', 0),

    ('Red', 11,
     '👾 BOSS LEVEL — Protocol Zero\n\nYou have traced ZERO to its final node. The Digital Forensics Division has cracked every layer of ZERO\'s defences. One final encrypted barrier remains. ZERO used its most powerful encryption — three layers, two keys from your investigation.\nThe evidence is within reach. Crack it. End ZERO. Restore the systems.\nhttps://drive.google.com/file/d/1bj_RUoik6kpXKXOOwyQKMjngMSzf0pJE/view?usp=sharing\n\nDecode and submit the final flag to win.',
     'IRON WALL BREACH CONTAINED',
     19.6, 'Three locks stand between you and the truth. The outer one is the webs favourite encoding. Behind it, a polyalphabetic cipher sealed with the key ZERO armed its wall with. The last lock shifts everything — by as many steps as Stage 9 had rails.', 0),
]


# ══════════════════════════════════════════════════════════════════
#  DO NOT EDIT BELOW THIS LINE
# ══════════════════════════════════════════════════════════════════

def get_db():
    conn = sqlite3.connect('hunt.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS teams (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        team_name      TEXT    UNIQUE NOT NULL,
        password       TEXT    NOT NULL,
        trail          TEXT    NOT NULL,
        score          REAL    DEFAULT 0,
        puzzles_solved INTEGER DEFAULT 0,
        current_stage  INTEGER DEFAULT 1,
        disqualified   INTEGER DEFAULT 0
    )''')

    # UNIQUE(trail, stage) ensures INSERT always targets the right row
    c.execute('''CREATE TABLE IF NOT EXISTS puzzles (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        trail       TEXT    NOT NULL,
        stage       INTEGER NOT NULL,
        question    TEXT    NOT NULL,
        answer      TEXT    NOT NULL,
        points      REAL    DEFAULT 10,
        hint        TEXT,
        is_physical INTEGER DEFAULT 0,
        UNIQUE(trail, stage)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS submissions (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        team_id      INTEGER NOT NULL,
        stage        INTEGER NOT NULL,
        answer_given TEXT    NOT NULL,
        is_correct   INTEGER NOT NULL,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS event_control (
        id               INTEGER PRIMARY KEY,
        status           TEXT    DEFAULT 'waiting',
        started_at       TIMESTAMP,
        duration_seconds INTEGER DEFAULT 10800,
        ended_at         TIMESTAMP
    )''')

    c.execute('''INSERT OR IGNORE INTO event_control
                 (id, status, duration_seconds)
                 VALUES (1, 'waiting', 10800)''')

    conn.commit()
    conn.close()
    print("Database schema ready.")


def load_teams():
    conn = get_db()
    c = conn.cursor()

    print("\nLoading teams...")
    for name, pwd, trail in TEAMS:
        hashed = hashlib.md5(pwd.encode()).hexdigest()
        try:
            c.execute('''INSERT INTO teams (team_name, password, trail)
                         VALUES (?, ?, ?)''', (name, hashed, trail))
            print(f"  Added : {name:20s} | {trail:6s} | password: {pwd}")
        except sqlite3.IntegrityError:
            c.execute('''UPDATE teams SET password=?, trail=? WHERE team_name=?''',
                      (hashed, trail, name))
            print(f"  Updated: {name:20s} | {trail:6s} | password: {pwd}")

    conn.commit()
    conn.close()


def load_puzzles():
    conn = get_db()
    c = conn.cursor()

    print("\nLoading puzzles...")
    for p in PUZZLES:
        trail, stage, question, answer, points, hint, is_physical = p
        # DELETE then INSERT — guarantees latest data always wins, no stale rows ever
        c.execute('DELETE FROM puzzles WHERE trail=? AND stage=?', (trail, stage))
        c.execute('''INSERT INTO puzzles
                     (trail, stage, question, answer, points, hint, is_physical)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (trail, stage, question, answer, points, hint, is_physical))
        print(f"  Puzzle: {trail:6s} Stage {stage:2d}")

    conn.commit()
    conn.close()


if __name__ == '__main__':
    if not os.path.exists('hunt.db'):
        print("Creating fresh hunt.db...")
    else:
        print("hunt.db found — updating data...")

    init_db()
    load_teams()
    load_puzzles()

    print("\n" + "═" * 50)
    print("  ALL DONE — ready to run app.py")
    print("═" * 50)
    print("\nTeam credentials (use exactly as shown to login):\n")
    print(f"  {'TEAM NAME':<22} {'TRAIL':<8} PASSWORD")
    print("  " + "─" * 45)
    for name, pwd, trail in TEAMS:
        print(f"  {name:<22} {trail:<8} {pwd}")
    print()