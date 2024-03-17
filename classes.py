from __future__ import annotations
from sqlite3 import connect

__all__ = ['User']


class User:
    db = connect('db.sqlite', check_same_thread=False)
    cursor = db.cursor()

    users: list[User] = []

    def __init__(self, username: str | None, *args) -> None:
        """User(id: str | None, [f_name: str], [l_name: str], [pass_hash: Callable[[], bytes]])"""
        self.immunizations = []
        self.allergies = []
        self.meds = []
        self.vitals = []
        self.appointments = []

        if len(args) == 0:
            # Load in existing user
            self.username: str = username
            self.f_name: str = User.cursor.execute(
                'SELECT f_name FROM users WHERE username = ?;', (username,)).fetchone()[0]
            self.m_name: str = User.cursor.execute(
                'SELECT m_name FROM users WHERE username = ?;', (username,)).fetchone()[0]
            self.l_name: str = User.cursor.execute(
                'SELECT l_name FROM users WHERE username = ?;', (username,)).fetchone()[0]
            self.age: str = User.cursor.execute(
                'SELECT age FROM users WHERE username = ?;', (username,)).fetchone()[0]
            self.sex: str = User.cursor.execute(
                'SELECT sex FROM users WHERE username = ?;', (username,)).fetchone()[0]
            self.pass_hash: bytes = User.cursor.execute(
                'SELECT pass_hash FROM users WHERE username = ?;', (username,)).fetchone()[0]

            for immunization in User.cursor.execute('SELECT * from immunizations WHERE username = ?;', (username,)):
                self.immunizations.append(immunization)
            for allergy in User.cursor.execute('SELECT * from allergies WHERE username = ?;', (username,)):
                self.allergies.append(allergy)
            for med in User.cursor.execute('SELECT * from meds WHERE username = ?;', (username,)):
                self.meds.append(med)
            for vital in User.cursor.execute('SELECT * from vitals WHERE username = ?;', (username,)):
                self.vitals.append(vital)
            for appointment in User.cursor.execute('SELECT * from appointments WHERE user = ?;', (username,)):
                self.appointments.append(appointment)
            User.users.append(self)
        else:
            # Create new member
            self.f_name: str = args[0]
            self.m_name: str = args[1]
            self.l_name: str = args[2]
            self.age: str = args[3]
            self.sex: str = args[4]
            self.pass_hash: bytes = args[5]
            self.username: str = username
            User.users.append(self)
        self.save()

    def save(self):
        User.cursor.execute('INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?, ?, ?, ?);', (
            self.f_name, self.m_name, self.l_name, self.age, self.sex, self.pass_hash, self.username))

        # Permanent Records
        User.cursor.executemany('INSERT OR REPLACE INTO immunizations VALUES (?, ?, ?, ?);', [
            tuple(t) for t in self.immunizations])
        User.cursor.executemany('INSERT OR REPLACE INTO allergies VALUES (?, ?, ?);', [
            tuple(t) for t in self.allergies])
        User.cursor.executemany('INSERT OR REPLACE INTO meds VALUES (?, ?, ?);', [
            tuple(t) for t in self.meds])
        User.cursor.executemany('INSERT OR REPLACE INTO vitals VALUES (?, ?, ?, ?);', [
            tuple(t) for t in self.vitals])

        User.db.commit()

    @classmethod
    def get_user(cls, id: str):
        for member in cls.users:
            if member.username == id:
                return member

    @classmethod
    def close(cls):
        for member in cls.users:
            member.save()
        cls.db.commit()
        cls.cursor.close()
        cls.db.close()
