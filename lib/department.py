from __init__ import CURSOR, CONN


class Department:

    # Dictionary to cache Department instances
    all_cache = {}

    def __init__(self, name, location, id=None):
        self.id = id
        self.name = name
        self.location = location

    def __repr__(self):
        return f"<Department {self.id}: {self.name}, {self.location}>"

    @classmethod
    def create_table(cls):
        """Create the departments table if it doesn't exist."""
        sql = """
            CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY,
            name TEXT,
            location TEXT)
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop the departments table."""
        sql = "DROP TABLE IF EXISTS departments;"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Insert the Department instance into the database and cache it."""
        sql = "INSERT INTO departments (name, location) VALUES (?, ?)"
        CURSOR.execute(sql, (self.name, self.location))
        CONN.commit()
        self.id = CURSOR.lastrowid
        type(self).all_cache[self.id] = self

    @classmethod
    def create(cls, name, location):
        """Create and save a new Department instance."""
        department = cls(name, location)
        department.save()
        return department

    def update(self):
        """Update the corresponding database row."""
        sql = "UPDATE departments SET name = ?, location = ? WHERE id = ?"
        CURSOR.execute(sql, (self.name, self.location, self.id))
        CONN.commit()

    def delete(self):
        """Delete the corresponding database row and remove from cache."""
        sql = "DELETE FROM departments WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        if self.id in type(self).all_cache:
            del type(self).all_cache[self.id]
        self.id = None

    @classmethod
    def instance_from_db(cls, row):
        """Return a Department instance from a database row and cache it."""
        if row[0] in cls.all_cache:
            dept = cls.all_cache[row[0]]
            dept.name = row[1]
            dept.location = row[2]
        else:
            dept = cls(row[1], row[2], row[0])
            cls.all_cache[row[0]] = dept
        return dept

    @classmethod
    def get_all(cls):
        """Return a list of all Department instances from the database."""
        sql = "SELECT * FROM departments"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id):
        """Return the Department instance with the given id."""
        sql = "SELECT * FROM departments WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        """Return the first Department instance with the given name."""
        sql = "SELECT * FROM departments WHERE name = ?"
        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_or_create_by(cls, name, location):
        """Find a Department by name and location, or create it if not found."""
        sql = "SELECT * FROM departments WHERE name = ? AND location = ?"
        row = CURSOR.execute(sql, (name, location)).fetchone()
        if row:
            return cls.instance_from_db(row)
        else:
            return cls.create(name, location)