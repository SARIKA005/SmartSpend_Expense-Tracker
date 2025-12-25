import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

DATABASE_NAME = "expense_tracker.db"

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Expenses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        date TEXT NOT NULL,
        description TEXT,
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Goals table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        target_amount REAL NOT NULL,
        current_amount REAL DEFAULT 0,
        deadline TEXT NOT NULL,
        priority TEXT DEFAULT 'Medium',
        description TEXT,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Savings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS savings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        date TEXT NOT NULL,
        source TEXT,
        purpose TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def add_expense(expense_data: Dict) -> bool:
    """Add a new expense"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO expenses (amount, category, date, description, tags)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            expense_data['amount'],
            expense_data['category'],
            expense_data['date'],
            expense_data.get('description', ''),
            expense_data.get('tags', '')
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding expense: {e}")
        return False

def get_expenses(month: Optional[str] = None) -> List[Dict]:
    """Get all expenses or filter by month (YYYY-MM)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if month:
            cursor.execute('''
                SELECT * FROM expenses 
                WHERE strftime('%Y-%m', date) = ?
                ORDER BY date DESC
            ''', (month,))
        else:
            cursor.execute('SELECT * FROM expenses ORDER BY date DESC')
        
        rows = cursor.fetchall()
        expenses = [dict(row) for row in rows]
        
        conn.close()
        return expenses
    except Exception as e:
        print(f"Error fetching expenses: {e}")
        return []

def add_goal(goal_data: Dict) -> bool:
    """Add a new financial goal"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO goals (name, target_amount, current_amount, deadline, priority, description, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            goal_data['name'],
            goal_data['target_amount'],
            goal_data.get('current_amount', 0),
            goal_data['deadline'],
            goal_data.get('priority', 'Medium'),
            goal_data.get('description', ''),
            goal_data.get('status', 'active')
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding goal: {e}")
        return False

def get_goals() -> List[Dict]:
    """Get all goals"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM goals ORDER BY priority DESC, deadline ASC')
        rows = cursor.fetchall()
        goals = [dict(row) for row in rows]
        
        conn.close()
        return goals
    except Exception as e:
        print(f"Error fetching goals: {e}")
        return []

def update_goal(goal_id: int, new_amount: float) -> bool:
    """Update goal current amount"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE goals 
        SET current_amount = ?
        WHERE id = ?
        ''', (new_amount, goal_id))
        
        conn.commit()
        
        # Check if goal is achieved
        cursor.execute('SELECT target_amount FROM goals WHERE id = ?', (goal_id,))
        row = cursor.fetchone()
        if row:
            target = row['target_amount']
            if new_amount >= target:
                cursor.execute('UPDATE goals SET status = "achieved" WHERE id = ?', (goal_id,))
                conn.commit()
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating goal: {e}")
        return False

def add_saving(saving_data: Dict) -> bool:
    """Add new savings record"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO savings (amount, date, source, purpose)
        VALUES (?, ?, ?, ?)
        ''', (
            saving_data['amount'],
            saving_data['date'],
            saving_data.get('source', ''),
            saving_data.get('purpose', '')
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding saving: {e}")
        return False

def get_savings() -> List[Dict]:
    """Get all savings"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM savings ORDER BY date DESC')
        rows = cursor.fetchall()
        savings = [dict(row) for row in rows]
        
        conn.close()
        return savings
    except Exception as e:
        print(f"Error fetching savings: {e}")
        return []