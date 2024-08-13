# evaluate the optimized SQL queries and provide feedback to the user.
# quivalence -> slabcity
# perfermence -> EXPLAIN
import json
import time
import textwrap
import psycopg2
from tabulate import tabulate
import csv

class Evaluate_rewrite_model:
    def __init__(self, db_file):
        self.db_file = db_file
    
    # 连接数据库并返回连接信息
    def connect_to_database(self):
        with open(self.db_file, 'r') as file:
            data = json.load(file)    
        # 设置连接参数
        conn_params = {
            'dbname': data['dbname'],
            'user': data['user'],
            'password': data['password'],
            'host': data['host'],
            'port': data['port']
        }
        # 在使用 psycopg2.connect(**conn_params) 时，
        # **conn_params 是一种 参数解包 的方式。它将字典中的键值对解包为函数参数，因此相当于如下调用：
        # conn = psycopg2.connect(dbname=data['dbname'], user=data['user'], password=data['password'], host=data['host'], port=data['port'])
        # print(conn_params)
        try:
            conn = psycopg2.connect(**conn_params)
            print("Database connection successful")
            return conn
        except psycopg2.Error as e:
            print(f"Database connection failed: {e}")
            return None
    
    # 执行 SQL 查询并返回执行时间
    def execute_query(self,conn, cursor, query):
        try:
            start_time = time.time()  # 记录开始时间
            explain_query = f"{query}"
            cursor.execute(explain_query)
            result = cursor.fetchall()
            end_time = time.time()  # 记录结束时间
            execution_cost = None
            query_latency = end_time - start_time

            for row in result:
                line = row[0]
                if "cost=" in line:
                    cost_part = line.split("cost=")[1].split()[0]
                    execution_cost = float(cost_part.split('..')[1].strip(')'))

            return execution_cost, query_latency

        except psycopg2.Error as e:
            print(f"Error executing query: {e}")
            return None, None


    def evalutate(self,input_query,rewrite_query):
        conn = self.connect_to_database()
        if conn is None:
            return
        
        # 创建游标对象
        cursor = conn.cursor()
        
        original_execution_cost, original_query_latency = self.execute_query(conn, cursor, input_query)
        if original_execution_cost is not None and original_query_latency is not None:
            print(f"Original Query Execution Cost: {original_execution_cost:.2f}")
            print(f"Original Query Latency: {original_query_latency:.2f} seconds\n")
        else:
            print("Failed to retrieve execution original cost or query latency.")
        
        rewrite_excution_cost, rewrite_query_latency = self.execute_query(conn, cursor, rewrite_query)
        if rewrite_excution_cost is not None and rewrite_query_latency is not None:
            print(f"Rewrite Query Execution Cost: {rewrite_excution_cost:.2f}")
            print(f"Rewrite Query Latency: {rewrite_query_latency:.2f} seconds\n")
        else:
            print("Failed to retrieve execution rewrite cost or query latency.")

        speed_up = (original_query_latency - rewrite_query_latency) / original_query_latency
        cursor.close()
        conn.close()
        
        return speed_up


# example usage
# input_query = "EXPLAIN (ANALYZE, COSTS) select 100.00 * sum(case when p_type like 'PROMO%' then l_extendedprice * (1 - l_discount) else 0 end) / sum(l_extendedprice * (1 - l_discount)) as promo_revenue from lineitem, part where l_partkey = p_partkey and l_shipdate >= date '1995-09-01' and l_shipdate < date '1995-09-01' + interval '1month';"
# rewrite_query_1 = "EXPLAIN (ANALYZE, COSTS) SELECT 100.00 * SUM(CASE WHEN p_type LIKE 'PROMO%' THEN l_extendedprice * (1 - l_discount) ELSE 0 END) / SUM(l_extendedprice * (1 - l_discount)) AS promo_revenue FROM lineitem JOIN part ON l_partkey = p_partkey WHERE l_shipdate >= DATE '1995-09-01' AND l_shipdate < DATE '1995-09-01' + INTERVAL '1' MONTH;"
# rewrite_query_2 = "EXPLAIN (ANALYZE, COSTS) WITH promo_revenue AS ( SELECT SUM(CASE WHEN p_type LIKE 'PROMO%' THEN l_extendedprice * (1 - l_discount) ELSE 0 END) AS promo_sum, SUM(l_extendedprice * (1 - l_discount)) AS total_sum FROM lineitem JOIN part ON l_partkey = p_partkey WHERE l_shipdate >= DATE '1995-09-01' AND l_shipdate < DATE '1995-09-01' + INTERVAL '1' MONTH) SELECT 100.00 * promo_sum / total_sum AS promo_revenue FROM promo_revenue;"

# test = Evaluate_rewrite_model("./postgres.json")
# speed_up = test.evalutate(input_query, rewrite_query_1)
# print(f"Speedup: {speed_up:.2f}")