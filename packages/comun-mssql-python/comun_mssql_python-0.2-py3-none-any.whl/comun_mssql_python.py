import mssql_python


class Sql:
    def __init__(self, driver, servidor, database, user, passw):
        self.nombre = 'Server=' + servidor
        self.nombre = self.nombre + ';Database=' + database
        self.nombre = self.nombre + ';UID=' + user
        self.nombre = self.nombre + ';PWD=' + passw
        self.nombre = self.nombre + ';Encrypt=yes'
        self.nombre = self.nombre + ';TrustServerCertificate=yes'
        self.conexion = mssql_python.connect(self.nombre, autocommit=False)
        self.cursor = self.conexion.cursor()

    def cerrar_conexion(self):
        self.conexion.close()

    def ejecutar(self, texto, *parametros):
        try:
            if len(parametros):
                if type(parametros[0]) == tuple:
                    parametros = parametros[0]
            self.cursor.execute(texto,parametros)
            self.conexion.commit()
        except Exception as e:
            print(texto)
            print(parametros)
            print(e)
            raise Exception(e)

    def consultar(self, consulta, as_dict = True):
        self.cursor.execute(consulta)
        if as_dict:
            columns = [column[0] for column in self.cursor.description]
            results = []
            for row in self.cursor.fetchall():
                results.append(dict(zip(columns, row)))

            return results
        else:
            return self.cursor.fetchall()

