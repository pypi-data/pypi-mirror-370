import dbhydra.dbhydra_core as dh


db1=dh.MysqlDb("config-mysql.ini")
with db1.connect_to_db():
    
    nodes_table = dh.MysqlTable(db1, "nodes",columns=["id","name"],types=["int","int"])
    #nodes_table.create()
    
    db1.initialize_migrator()
    
    print(nodes_table.column_type_dict)
    
    new_column_type_dict={"id":"int","name":"nvarchar","age":"int"}
    
    migration1=db1.migrator.create_table_migration("nodes", nodes_table.column_type_dict, new_column_type_dict)
    db1.migrator.save_current_migration_to_json()
    migration2=db1.migrator.create_table_migration("nodes", new_column_type_dict, nodes_table.column_type_dict)
    db1.migrator.save_current_migration_to_json()    
    print(migration1)
    print(migration2)
    
    
    
    
    
    
