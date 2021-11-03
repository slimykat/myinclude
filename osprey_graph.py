import mysql.connector
from mysql.connector import Error
import datetime, json
def rename(str_):
    return str_.replace(':', '_').replace('.', '_')

# def empty_graph(ap_group_id):
class osprey_network_toplology:
    def __init__(self, Edges:dict, Nodes:dict, ap_group_id:int, connection) -> None:
        self.R_node = Nodes["Router"]
        self.SW_node = Nodes["Switch"]
        self.host_node = Nodes["normalHost"].union(Nodes["normalHost_without_SNMP"])

        self.lnk = Edges
        self.id = ap_group_id
        self.conn = connection
    
    def debug(self):
        print(self.lnk)

    def db_update_link(self):
        cursor = self.conn.cursor()
        ap_group_id = self.id
        cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ## check out server nodes
        check_sql = 'SELECT server_id, level FROM server_to_ap_group WHERE ap_group_id = %s'
        cursor.execute(check_sql, (ap_group_id,))
        current_nodes = {}
        for v, level in cursor:
            current_nodes[v] = level

        ## delete datas in probe_server_link and then draw the new connections
        del_sql = "DELETE FROM `probe_server_link` WHERE `probe_server_link`.`ap_group_id` = %s"
        cursor.execute(del_sql, (ap_group_id,))
        self.conn.commit()

        # only update the relationship among those existed nodes
        sql = 'INSERT INTO probe_server_link (ap_group_id, server_id, server_link_id, level, created_at) VALUES (%s,%s,%s,%s,%s)'
        all_lnk = self.lnk["Router"].union(self.lnk["Switch"]).union(self.lnk["normalHost"])
        for v1,v2 in all_lnk:
            if rename(v1) in current_nodes and rename(v2) in current_nodes:
                if current_nodes[v1] != current_nodes[v2]:
                    cursor.execute(sql, (ap_group_id, rename(v1), rename(v2), int(self.node_lv[v1]), cur_time,))
        self.conn.commit()


        ## Store table for new graph plotting
        # nodes
        check_sql = 'SELECT id FROM VIS_graph_nodes WHERE id = %s and ap_group_id = %s'
        sql = 'INSERT INTO VIS_graph_nodes (ap_group_id, id, label, shape, size, color) VALUES (%s,%s,%s,%s,%s,%s)'
        for v in self.R_node:
            node_id = rename(v)
            cursor.execute(check_sql, (node_id, ap_group_id))
            if not cursor.fetchone():
                cursor.execute(sql, (ap_group_id, node_id, node_id, "dot", 25, '{"background":"aqua", "border" : "blue"}'))
        for v in self.SW_node:
            node_id = rename(v)
            cursor.execute(check_sql, (node_id, ap_group_id))
            if not cursor.fetchone():
                cursor.execute(sql, (ap_group_id, node_id, node_id, "dot", 15, '{"background":"orange", "border" : "brown"}'))
        for v in self.host_node:
            node_id = rename(v)
            cursor.execute(check_sql, (node_id, ap_group_id))
            if not cursor.fetchone():
                cursor.execute(sql, (ap_group_id, node_id, node_id, "dot", 8, '{"background":"white", "border" : "grey"}'))
        # edges
        bucket = []
        for v1,v2 in self.lnk["Switch"]:
            bucket.append({"from": rename(v1), "to": rename(v2), "width": 1.8})
        for v1,v2 in self.lnk["Router"]:
            bucket.append({"from": rename(v1), "to": rename(v2), "width": 2.5})
        for v1,v2 in self.lnk["normalHost"]:
            bucket.append({"from": rename(v1), "to": rename(v2), "width": 0.1})

        del_sql = 'DELETE FROM `VIS_graph_edges`  WHERE ap_group_id = %s'
        cursor.execute(del_sql, [ap_group_id])
        sql = 'INSERT INTO VIS_graph_edges (ap_group_id, edges) VALUES (%s,%s)'
        cursor.execute(sql, (ap_group_id, json.dumps(bucket)))
        self.conn.commit()


