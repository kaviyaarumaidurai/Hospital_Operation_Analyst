from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Root123",  
        database="hospital"
    )

@app.get("/")
def home():
    return {"message": "Hospital Dashboard Backend API is running!"}

@app.get("/metrics/billing")
def get_billing():
    conn = get_db_connection()
    query = """
    SELECT d.DeptName, SUM(b.TotalBill) as TotalRevenue
    FROM Fact_Billing b
    JOIN Fact_Admissions a ON b.AdmissionID = a.AdmissionID
    JOIN Dim_Departments d ON a.DeptID = d.DeptID
    GROUP BY d.DeptName
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df.to_dict(orient="records")

@app.get("/metrics/occupancy")
def get_occupancy():
    conn = get_db_connection()
    query = """
    SELECT (COUNT(a.AdmissionID) / (SELECT SUM(TotalBeds) FROM Dim_Departments)) * 100 as occupancy_rate
    FROM Fact_Admissions a
    LEFT JOIN Fact_Discharges d ON a.AdmissionID = d.AdmissionID
    WHERE d.DischargeDate IS NULL;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df.to_dict(orient="records")