CREATE DATABASE medilinkPrueba;

USE medilinkPrueba;

-- Tabla de medicamentos
CREATE TABLE medicamentos (
    id_medicamento INT AUTO_INCREMENT PRIMARY KEY,
    nombre_producto VARCHAR(150) NOT NULL,
    clasificacion VARCHAR(100) NOT NULL,
    presentacion VARCHAR(100) NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL,
    numero_lote VARCHAR(50) UNIQUE,
    precio_lote DECIMAL(10,2),
    cantidad_mg INT NOT NULL,
    fecha_caducidad DATE,
    fecha_alta DATE,
    farmaceutica VARCHAR(150),
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de detalles de venta
CREATE TABLE ventas (
    id_venta INT AUTO_INCREMENT PRIMARY KEY,
    fecha_venta DATETIME DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10,2) NOT NULL,
    tipo_consulta VARCHAR(50) DEFAULT 'Ninguna'
);

-- Tabla detalles ventas
CREATE TABLE detalle_ventas (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_venta INT NOT NULL,
    id_medicamento INT NOT NULL,
    cantidad INT NOT NULL,
    precio_historico DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta),
    FOREIGN KEY (id_medicamento) REFERENCES medicamentos(id_medicamento)
);

-- Tabla clientes
CREATE TABLE clientes (
    id_cliente       INT AUTO_INCREMENT PRIMARY KEY,
    nombre           VARCHAR(100) NOT NULL,
    ap_paterno       VARCHAR(100) NOT NULL,
    ap_materno       VARCHAR(100),
    edad             INT NOT NULL,
    sexo             VARCHAR(50) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    peso             DECIMAL(5,2),
    talla            DECIMAL(5,2),
    oxigenacion      DECIMAL(5,2),
    presion          VARCHAR(20),
    temperatura      DECIMAL(5,2),
    correo           VARCHAR(150),
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla trabajadores
CREATE TABLE trabajadores (
    id_trabajador INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ap_paterno VARCHAR(100) NOT NULL,
    ap_materno VARCHAR(100),
    fecha_nacimiento DATE NOT NULL,
    genero VARCHAR(20) NOT NULL,
    curp VARCHAR(18) UNIQUE NOT NULL,
    rfc VARCHAR(13) UNIQUE NOT NULL,
    direccion TEXT,
    telefono VARCHAR(20),
    correo VARCHAR(150),
    puesto VARCHAR(50) NOT NULL,
    cedula_profesional VARCHAR(50),
    turno VARCHAR(20) NOT NULL,
    fecha_ingreso DATE NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Historial medico
CREATE TABLE historial_medico (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_medico INT,
    fecha DATE NOT NULL,
    diagnostico TEXT,
    tratamiento TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_medico) REFERENCES trabajadores(id_trabajador)
);

-- Ejemplos medicamentos
INSERT INTO medicamentos (
    nombre_producto, clasificacion, presentacion,
    precio_unitario, stock,
    numero_lote, precio_lote, cantidad_mg,
    fecha_caducidad, fecha_alta,
    farmaceutica, descripcion
)
VALUES
('Paracetamol', 'Analgésico', 'Tabletas', 10.50, 100, 'L001', 500.00, 500, '2026-12-31', '2026-04-26', 'Pfizer', 'Alivia dolor y fiebre'),
('Ibuprofeno', 'Analgésico', 'Tabletas', 12.00, 120, 'L002', 600.00, 400, '2026-10-15', '2026-04-26', 'Bayer', 'Antiinflamatorio y analgésico'),
('Aspirina', 'Analgésico', 'Tabletas', 8.00, 80, 'L003', 400.00, 500, '2027-01-20', '2026-04-26', 'Bayer', 'Reduce dolor y fiebre'),
('Naproxeno', 'Analgésico', 'Cápsulas', 15.00, 90, 'L004', 700.00, 250, '2026-11-10', '2026-04-26', 'Genomma Lab', 'Dolor e inflamación'),
('Ketorolaco', 'Analgésico', 'Inyección', 25.00, 50, 'L005', 900.00, 30, '2026-09-01', '2026-04-26', 'Pisa', 'Dolor fuerte'),

('Amoxicilina', 'Antibiótico', 'Cápsulas', 20.00, 150, 'L006', 1200.00, 500, '2026-08-20', '2026-04-26', 'Pfizer', 'Infecciones bacterianas'),
('Ciprofloxacino', 'Antibiótico', 'Tabletas', 22.00, 130, 'L007', 1300.00, 500, '2026-07-15', '2026-04-26', 'Roche', 'Antibiótico amplio espectro'),
('Azitromicina', 'Antibiótico', 'Tabletas', 30.00, 100, 'L008', 1500.00, 500, '2026-12-05', '2026-04-26', 'Pfizer', 'Infecciones respiratorias'),
('Penicilina', 'Antibiótico', 'Inyección', 18.00, 70, 'L009', 800.00, 1000, '2026-06-30', '2026-04-26', 'Pisa', 'Infecciones graves'),
('Clindamicina', 'Antibiótico', 'Cápsulas', 28.00, 85, 'L010', 1100.00, 300, '2026-11-22', '2026-04-26', 'Sanofi', 'Infecciones bacterianas'),

('Diclofenaco', 'Antiinflamatorio', 'Tabletas', 14.00, 110, 'L011', 650.00, 50, '2026-10-01', '2026-04-26', 'Novartis', 'Dolor muscular'),
('Meloxicam', 'Antiinflamatorio', 'Tabletas', 16.00, 95, 'L012', 700.00, 15, '2026-09-18', '2026-04-26', 'Pfizer', 'Artritis'),
('Celecoxib', 'Antiinflamatorio', 'Cápsulas', 35.00, 60, 'L013', 1400.00, 200, '2026-12-12', '2026-04-26', 'Pfizer', 'Dolor crónico'),
('Indometacina', 'Antiinflamatorio', 'Cápsulas', 18.00, 75, 'L014', 800.00, 25, '2026-08-25', '2026-04-26', 'Roche', 'Inflamación'),
('Piroxicam', 'Antiinflamatorio', 'Tabletas', 20.00, 65, 'L015', 900.00, 20, '2026-07-30', '2026-04-26', 'Bayer', 'Dolor e inflamación'),

('Loratadina', 'Antialérgico', 'Tabletas', 10.00, 140, 'L016', 500.00, 10, '2026-11-01', '2026-04-26', 'Bayer', 'Alergias'),
('Cetirizina', 'Antialérgico', 'Tabletas', 11.00, 130, 'L017', 550.00, 10, '2026-10-20', '2026-04-26', 'Pfizer', 'Alergias'),
('Desloratadina', 'Antialérgico', 'Jarabe', 13.00, 90, 'L018', 600.00, 5, '2026-09-15', '2026-04-26', 'Sanofi', 'Alergia infantil'),
('Fexofenadina', 'Antialérgico', 'Tabletas', 17.00, 80, 'L019', 700.00, 120, '2026-12-28', '2026-04-26', 'Roche', 'Alergias fuertes'),
('Clorfenamina', 'Antialérgico', 'Jarabe', 9.00, 100, 'L020', 400.00, 4, '2026-08-05', '2026-04-26', 'Genomma Lab', 'Alergia leve');

-- Insertar medicamentos
DELIMITER //

CREATE PROCEDURE sp_insertar_medicamento(
    IN p_nombre_producto VARCHAR(150),
    IN p_clasificacion VARCHAR(100),
    IN p_presentacion VARCHAR(100),
    IN p_precio_unitario DECIMAL(10,2),
    IN p_stock INT,
    IN p_numero_lote VARCHAR(50),
    IN p_precio_lote DECIMAL(10,2),
    IN p_cantidad_mg INT,
    IN p_fecha_caducidad DATE,
    IN p_fecha_alta DATE,
    IN p_farmaceutica VARCHAR(150),
    IN p_descripcion TEXT
)
BEGIN
    INSERT INTO medicamentos (
        nombre_producto, clasificacion, presentacion,
        precio_unitario, stock, numero_lote, precio_lote, cantidad_mg,
        fecha_caducidad, fecha_alta, farmaceutica, descripcion
    )
    VALUES (
        p_nombre_producto, p_clasificacion, p_presentacion,
        p_precio_unitario, p_stock, p_numero_lote, p_precio_lote, p_cantidad_mg,
        p_fecha_caducidad, p_fecha_alta, p_farmaceutica, p_descripcion
    );
END //

DELIMITER ;

-- Crear ventas
DELIMITER //

CREATE PROCEDURE sp_crear_venta(
    IN p_total DECIMAL(10,2),
    IN p_tipo_consulta VARCHAR(50),
    OUT p_id_venta INT
)
BEGIN
    INSERT INTO ventas (total, tipo_consulta)
    VALUES (p_total, p_tipo_consulta);
    SET p_id_venta = LAST_INSERT_ID();
END //

DELIMITER ;

-- Insertar detalles en medicamentos
DELIMITER //

CREATE PROCEDURE sp_insertar_detalle(
    IN p_id_venta INT,
    IN p_id_medicamento INT,
    IN p_cantidad INT,
    IN p_precio_historico DECIMAL(10,2),
    IN p_subtotal DECIMAL(10,2)
)
BEGIN
    INSERT INTO detalle_ventas (id_venta, id_medicamento, cantidad, precio_historico, subtotal)
    VALUES (p_id_venta, p_id_medicamento, p_cantidad, p_precio_historico, p_subtotal);

    UPDATE medicamentos
    SET stock = stock - p_cantidad
    WHERE id_medicamento = p_id_medicamento;
END //

DELIMITER ;

-- Insertar clientes
DELIMITER //

CREATE PROCEDURE sp_insertar_cliente(
    IN p_nombre           VARCHAR(100),
    IN p_ap_paterno       VARCHAR(100),
    IN p_ap_materno       VARCHAR(100),
    IN p_edad             INT,
    IN p_sexo             VARCHAR(50),
    IN p_fecha_nacimiento DATE,
    IN p_peso             DECIMAL(5,2),
    IN p_talla            DECIMAL(5,2),
    IN p_oxigenacion      DECIMAL(5,2),
    IN p_presion          VARCHAR(20),
    IN p_temperatura      DECIMAL(5,2),
    IN p_correo           VARCHAR(150)
)
BEGIN
    INSERT INTO clientes (
        nombre, ap_paterno, ap_materno, edad, sexo, fecha_nacimiento,
        peso, talla, oxigenacion, presion, temperatura, correo
    )
    VALUES (
        p_nombre, p_ap_paterno, p_ap_materno, p_edad, p_sexo, p_fecha_nacimiento,
        p_peso, p_talla, p_oxigenacion, p_presion, p_temperatura, p_correo
    );
END //

DELIMITER ;

-- Devuelve TODOS los campos para que la receta pueda enviar correo y el formulario de edición pueda cargar todos los datos
DELIMITER //

CREATE PROCEDURE sp_buscar_clientes_por_apellido(
    IN p_apellido VARCHAR(100)
)
BEGIN
    SELECT
        id_cliente,
        nombre,
        ap_paterno,
        ap_materno,
        edad,
        sexo,
        fecha_nacimiento,
        peso,
        talla,
        oxigenacion,
        presion,
        temperatura,
        correo
    FROM clientes
    WHERE ap_paterno LIKE CONCAT('%', p_apellido, '%')
       OR ap_materno LIKE CONCAT('%', p_apellido, '%')
    ORDER BY ap_paterno, ap_materno, nombre;
END //

DELIMITER ;

-- Insertar trabajadores
DELIMITER //

CREATE PROCEDURE sp_insertar_trabajador(
    IN p_nombre VARCHAR(100),
    IN p_ap_paterno VARCHAR(100),
    IN p_ap_materno VARCHAR(100),
    IN p_fecha_nacimiento DATE,
    IN p_genero VARCHAR(20),
    IN p_curp VARCHAR(18),
    IN p_rfc VARCHAR(13),
    IN p_direccion TEXT,
    IN p_telefono VARCHAR(20),
    IN p_correo VARCHAR(150),
    IN p_puesto VARCHAR(50),
    IN p_cedula_profesional VARCHAR(50),
    IN p_turno VARCHAR(20),
    IN p_fecha_ingreso DATE
)
BEGIN
    INSERT INTO trabajadores (
        nombre, ap_paterno, ap_materno, fecha_nacimiento, genero,
        curp, rfc, direccion, telefono, correo, puesto,
        cedula_profesional, turno, fecha_ingreso
    )
    VALUES (
        p_nombre, p_ap_paterno, p_ap_materno, p_fecha_nacimiento, p_genero,
        p_curp, p_rfc, p_direccion, p_telefono, p_correo, p_puesto,
        p_cedula_profesional, p_turno, p_fecha_ingreso
    );
END //

DELIMITER ;

-- Listar trabajadores
DELIMITER //

CREATE PROCEDURE sp_listar_trabajadores()
BEGIN
    SELECT * FROM trabajadores;
END //

DELIMITER ;

-- Actualizar trabajador.
DELIMITER //

CREATE PROCEDURE sp_actualizar_trabajador(
    IN p_id               INT,
    IN p_nombre           VARCHAR(100),
    IN p_ap_paterno       VARCHAR(100),
    IN p_ap_materno       VARCHAR(100),
    IN p_fecha_nacimiento DATE,
    IN p_genero           VARCHAR(20),
    IN p_curp             VARCHAR(18),
    IN p_rfc              VARCHAR(13),
    IN p_direccion        TEXT,
    IN p_telefono         VARCHAR(20),
    IN p_correo           VARCHAR(150),
    IN p_puesto           VARCHAR(50),
    IN p_cedula           VARCHAR(50),
    IN p_turno            VARCHAR(20),
    IN p_fecha_ingreso    DATE
)
BEGIN
    UPDATE trabajadores
    SET nombre             = p_nombre,
        ap_paterno         = p_ap_paterno,
        ap_materno         = p_ap_materno,
        fecha_nacimiento   = p_fecha_nacimiento,
        genero             = p_genero,
        curp               = p_curp,
        rfc                = p_rfc,
        direccion          = p_direccion,
        telefono           = p_telefono,
        correo             = p_correo,
        puesto             = p_puesto,
        cedula_profesional = p_cedula,
        turno              = p_turno,
        fecha_ingreso      = p_fecha_ingreso
    WHERE id_trabajador = p_id;
END //

DELIMITER ;

-- Insertar historial medico.

DELIMITER //

CREATE PROCEDURE sp_insertar_historial(
    IN p_id_cliente INT,
    IN p_id_medico INT,
    IN p_fecha DATE,
    IN p_diagnostico TEXT,
    IN p_tratamiento TEXT
)
BEGIN
    INSERT INTO historial_medico (id_cliente, id_medico, fecha, diagnostico, tratamiento)
    VALUES (p_id_cliente, p_id_medico, p_fecha, p_diagnostico, p_tratamiento);
END //

DELIMITER ;

-- Traer el nombre del médico que atendió
DELIMITER //

CREATE PROCEDURE sp_obtener_historial_cliente(
    IN p_id_cliente INT
)
BEGIN
    SELECT 
        h.id_historial,
        h.fecha,
        h.diagnostico,
        h.tratamiento,
        h.id_medico,
        CONCAT_WS(' ', t.nombre, t.ap_paterno, t.ap_materno) AS nombre_medico,
        t.cedula_profesional
    FROM historial_medico h
    LEFT JOIN trabajadores t ON h.id_medico = t.id_trabajador
    WHERE h.id_cliente = p_id_cliente
    ORDER BY h.fecha DESC, h.id_historial DESC;
END //

DELIMITER ;


DROP PROCEDURE IF EXISTS sp_buscar_clientes_por_apellido;
 
DELIMITER //
 
CREATE PROCEDURE sp_buscar_clientes_por_apellido(
    IN p_apellido VARCHAR(100)
)
BEGIN
    SELECT
        id_cliente,
        nombre,
        ap_paterno,
        ap_materno,
        edad,
        sexo,
        fecha_nacimiento,
        peso,
        talla,
        oxigenacion,
        presion,
        temperatura,
        correo
    FROM clientes
    WHERE ap_paterno LIKE CONCAT('%', p_apellido, '%')
       OR ap_materno LIKE CONCAT('%', p_apellido, '%')
    ORDER BY ap_paterno, ap_materno, nombre;
END //
 
DELIMITER ;
 
-- Actualizar SP de obtener historial. Ahora hace JOIN con trabajadores para traer el nombre del médico que atendió cada consulta.

DROP PROCEDURE IF EXISTS sp_obtener_historial_cliente;
 
DELIMITER //
 
CREATE PROCEDURE sp_obtener_historial_cliente(
    IN p_id_cliente INT
)
BEGIN
    SELECT 
        h.id_historial,
        h.fecha,
        h.diagnostico,
        h.tratamiento,
        h.id_medico,
        CONCAT_WS(' ', t.nombre, t.ap_paterno, t.ap_materno) AS nombre_medico,
        t.cedula_profesional
    FROM historial_medico h
    LEFT JOIN trabajadores t ON h.id_medico = t.id_trabajador
    WHERE h.id_cliente = p_id_cliente
    ORDER BY h.fecha DESC, h.id_historial DESC;
END //
 
DELIMITER ;
 
-- Obtener TODOS los clientes ordenados por apellido
DROP PROCEDURE IF EXISTS sp_obtener_todos_clientes;
DELIMITER //
CREATE PROCEDURE sp_obtener_todos_clientes()
BEGIN
    SELECT * FROM clientes
    ORDER BY ap_paterno, ap_materno, nombre;
END //
DELIMITER ;


-- Actualizar cliente por ID
DROP PROCEDURE IF EXISTS sp_actualizar_cliente;
DELIMITER //
CREATE PROCEDURE sp_actualizar_cliente(
    IN p_id_cliente       INT,
    IN p_nombre           VARCHAR(100),
    IN p_ap_paterno       VARCHAR(100),
    IN p_ap_materno       VARCHAR(100),
    IN p_edad             INT,
    IN p_sexo             VARCHAR(50),
    IN p_fecha_nacimiento DATE,
    IN p_peso             DECIMAL(5,2),
    IN p_talla            DECIMAL(5,2),
    IN p_oxigenacion      DECIMAL(5,2),
    IN p_presion          VARCHAR(20),
    IN p_temperatura      DECIMAL(5,2),
    IN p_correo           VARCHAR(150)
)
BEGIN
    UPDATE clientes
    SET nombre           = p_nombre,
        ap_paterno       = p_ap_paterno,
        ap_materno       = p_ap_materno,
        edad             = p_edad,
        sexo             = p_sexo,
        fecha_nacimiento = p_fecha_nacimiento,
        peso             = p_peso,
        talla            = p_talla,
        oxigenacion      = p_oxigenacion,
        presion          = p_presion,
        temperatura      = p_temperatura,
        correo           = p_correo
    WHERE id_cliente = p_id_cliente;
END //
DELIMITER ;

-- Buscar medicamentos por nombre (para la caja/ventas)
DROP PROCEDURE IF EXISTS sp_buscar_medicamentos;
DELIMITER //
CREATE PROCEDURE sp_buscar_medicamentos(
    IN p_termino VARCHAR(150)
)
BEGIN
    SELECT id_medicamento, nombre_producto, precio_unitario, stock
    FROM medicamentos
    WHERE nombre_producto LIKE CONCAT('%', p_termino, '%')
      AND stock > 0
    LIMIT 5;
END //
DELIMITER ;


-- Buscar farmacéuticas distintas (para autocomplete en alta de medicamento)
DROP PROCEDURE IF EXISTS sp_buscar_farmaceuticas;
DELIMITER //
CREATE PROCEDURE sp_buscar_farmaceuticas(
    IN p_termino VARCHAR(150)
)
BEGIN
    SELECT DISTINCT farmaceutica
    FROM medicamentos
    WHERE farmaceutica LIKE CONCAT('%', p_termino, '%')
      AND farmaceutica IS NOT NULL
    ORDER BY farmaceutica
    LIMIT 10;
END //
DELIMITER ;

-- Obtener TODOS los trabajadores
DROP PROCEDURE IF EXISTS sp_obtener_todos_trabajadores;
DELIMITER //
CREATE PROCEDURE sp_obtener_todos_trabajadores()
BEGIN
    SELECT * FROM trabajadores
    ORDER BY ap_paterno, ap_materno, nombre;
END //
DELIMITER ;


-- Actualizar trabajador (versión completa, ya estaba pero la dejamos consistente)
DROP PROCEDURE IF EXISTS sp_actualizar_trabajador;
DELIMITER //
CREATE PROCEDURE sp_actualizar_trabajador(
    IN p_id               INT,
    IN p_nombre           VARCHAR(100),
    IN p_ap_paterno       VARCHAR(100),
    IN p_ap_materno       VARCHAR(100),
    IN p_fecha_nacimiento DATE,
    IN p_genero           VARCHAR(20),
    IN p_curp             VARCHAR(18),
    IN p_rfc              VARCHAR(13),
    IN p_direccion        TEXT,
    IN p_telefono         VARCHAR(20),
    IN p_correo           VARCHAR(150),
    IN p_puesto           VARCHAR(50),
    IN p_cedula           VARCHAR(50),
    IN p_turno            VARCHAR(20),
    IN p_fecha_ingreso    DATE
)
BEGIN
    UPDATE trabajadores
    SET nombre             = p_nombre,
        ap_paterno         = p_ap_paterno,
        ap_materno         = p_ap_materno,
        fecha_nacimiento   = p_fecha_nacimiento,
        genero             = p_genero,
        curp               = p_curp,
        rfc                = p_rfc,
        direccion          = p_direccion,
        telefono           = p_telefono,
        correo             = p_correo,
        puesto             = p_puesto,
        cedula_profesional = p_cedula,
        turno              = p_turno,
        fecha_ingreso      = p_fecha_ingreso
    WHERE id_trabajador = p_id;
END //
DELIMITER ;


-- Obtener trabajador por ID (para autocompletar médico en la receta)
DROP PROCEDURE IF EXISTS sp_obtener_trabajador_por_id;
DELIMITER //
CREATE PROCEDURE sp_obtener_trabajador_por_id(
    IN p_id INT
)
BEGIN
    SELECT id_trabajador, nombre, ap_paterno, ap_materno,
           cedula_profesional, puesto
    FROM trabajadores
    WHERE id_trabajador = p_id;
END //
DELIMITER ;

-- Define qué hace que dos medicamentos sean "el mismo": mismo nombre + misma presentación + misma cantidad mg. Si ya existe, lo borramos para recrear limpio,
SET @tabla_medicamentos := 'medicamentos';
SET @nombre_indice := 'uk_medicamento_unico';

SET @existe := (SELECT COUNT(*) FROM information_schema.statistics
                WHERE table_schema = DATABASE()
                  AND table_name   = @tabla_medicamentos
                  AND index_name   = @nombre_indice);

SET @sql := IF(@existe > 0,
               CONCAT('ALTER TABLE ', @tabla_medicamentos, ' DROP INDEX ', @nombre_indice),
               'SELECT ''Indice no existia, se creara'' AS info');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

ALTER TABLE medicamentos
    ADD CONSTRAINT uk_medicamento_unico
    UNIQUE (nombre_producto, presentacion, cantidad_mg);

-- 2) SP: Buscar medicamento existente (para reabastecimiento). Devuelve el medicamento si ya existe con esos datos, o ningún registro si es nuevo.

DROP PROCEDURE IF EXISTS sp_buscar_medicamento_existente;
DELIMITER //
CREATE PROCEDURE sp_buscar_medicamento_existente(
    IN p_nombre        VARCHAR(150),
    IN p_presentacion  VARCHAR(100),
    IN p_cantidad_mg   INT
)
BEGIN
    SELECT id_medicamento, nombre_producto, presentacion, cantidad_mg,
           stock, precio_unitario, numero_lote, farmaceutica
    FROM medicamentos
    WHERE nombre_producto = p_nombre
      AND presentacion    = p_presentacion
      AND cantidad_mg     = p_cantidad_mg
    LIMIT 1;
END //
DELIMITER ;


-- Reabastecer medicamento existente. Suma stock al medicamento y actualiza datos de lote/precio.
DROP PROCEDURE IF EXISTS sp_reabastecer_medicamento;
DELIMITER //
CREATE PROCEDURE sp_reabastecer_medicamento(
    IN p_id_medicamento INT,
    IN p_stock_extra    INT,
    IN p_nuevo_lote     VARCHAR(50),
    IN p_precio_lote    DECIMAL(10,2),
    IN p_caducidad      DATE,
    IN p_precio_unit    DECIMAL(10,2)
)
BEGIN
    UPDATE medicamentos
    SET stock           = stock + p_stock_extra,
        numero_lote     = p_nuevo_lote,
        precio_lote     = p_precio_lote,
        fecha_caducidad = p_caducidad,
        precio_unitario = p_precio_unit
    WHERE id_medicamento = p_id_medicamento;
END //
DELIMITER ;

-- Detectar paciente duplicado. Busca por nombre + apellidos + fecha de nacimiento.
DROP PROCEDURE IF EXISTS sp_buscar_paciente_duplicado;
DELIMITER //
CREATE PROCEDURE sp_buscar_paciente_duplicado(
    IN p_nombre           VARCHAR(100),
    IN p_ap_paterno       VARCHAR(100),
    IN p_ap_materno       VARCHAR(100),
    IN p_fecha_nacimiento DATE
)
BEGIN
    SELECT id_cliente, nombre, ap_paterno, ap_materno, edad
    FROM clientes
    WHERE nombre           = p_nombre
      AND ap_paterno       = p_ap_paterno
      AND IFNULL(ap_materno, '') = IFNULL(p_ap_materno, '')
      AND fecha_nacimiento = p_fecha_nacimiento
    LIMIT 1;
END //
DELIMITER ;

-- Verificar si CURP/RFC ya existen en trabajadores
DROP PROCEDURE IF EXISTS sp_buscar_trabajador_por_curp_rfc;
DELIMITER //
CREATE PROCEDURE sp_buscar_trabajador_por_curp_rfc(
    IN p_curp VARCHAR(18),
    IN p_rfc  VARCHAR(13)
)
BEGIN
    SELECT id_trabajador, nombre, ap_paterno, curp, rfc
    FROM trabajadores
    WHERE curp = p_curp OR rfc = p_rfc
    LIMIT 1;
END //
DELIMITER ;

-- 30/04/2026 --
-- Autocompletado de medicamentos por nombre. Devuelve TODOS los datos para llenar el formulario completo al hacer clic en una sugerencia.
DROP PROCEDURE IF EXISTS sp_autocompletar_medicamentos;
DELIMITER //
CREATE PROCEDURE sp_autocompletar_medicamentos(
    IN p_termino VARCHAR(150)
)
BEGIN
    SELECT id_medicamento, nombre_producto, clasificacion, presentacion,
           precio_unitario, stock, numero_lote, precio_lote, cantidad_mg,
           fecha_caducidad, fecha_alta, farmaceutica, descripcion
    FROM medicamentos
    WHERE nombre_producto LIKE CONCAT('%', p_termino, '%')
    ORDER BY nombre_producto, presentacion, cantidad_mg
    LIMIT 8;
END //
DELIMITER ;


-- Listar TODOS los medicamentos (para la tabla)
DROP PROCEDURE IF EXISTS sp_obtener_todos_medicamentos;
DELIMITER //
CREATE PROCEDURE sp_obtener_todos_medicamentos()
BEGIN
    SELECT id_medicamento, nombre_producto, clasificacion, presentacion,
           precio_unitario, stock, numero_lote, precio_lote, cantidad_mg,
           fecha_caducidad, fecha_alta, farmaceutica, descripcion
    FROM medicamentos
    ORDER BY nombre_producto, presentacion, cantidad_mg;
END //
DELIMITER ;


-- Listar medicamentos filtrados por clasificación
DROP PROCEDURE IF EXISTS sp_filtrar_medicamentos_clasificacion;
DELIMITER //
CREATE PROCEDURE sp_filtrar_medicamentos_clasificacion(
    IN p_clasificacion VARCHAR(100)
)
BEGIN
    SELECT id_medicamento, nombre_producto, clasificacion, presentacion,
           precio_unitario, stock, numero_lote, precio_lote, cantidad_mg,
           fecha_caducidad, fecha_alta, farmaceutica, descripcion
    FROM medicamentos
    WHERE clasificacion = p_clasificacion
    ORDER BY nombre_producto, presentacion, cantidad_mg;
END //
DELIMITER ;

-- Actualizar medicamento existente. Solo se modifican datos NO identitarios(no nombre, presentación ni mg para no romper la unicidad)
DROP PROCEDURE IF EXISTS sp_actualizar_medicamento;
DELIMITER //
CREATE PROCEDURE sp_actualizar_medicamento(
    IN p_id_medicamento  INT,
    IN p_clasificacion   VARCHAR(100),
    IN p_precio_unit     DECIMAL(10,2),
    IN p_stock           INT,
    IN p_numero_lote     VARCHAR(50),
    IN p_precio_lote     DECIMAL(10,2),
    IN p_caducidad       DATE,
    IN p_farmaceutica    VARCHAR(150),
    IN p_descripcion     TEXT
)
BEGIN
    UPDATE medicamentos
    SET clasificacion   = p_clasificacion,
        precio_unitario = p_precio_unit,
        stock           = p_stock,
        numero_lote     = p_numero_lote,
        precio_lote     = p_precio_lote,
        fecha_caducidad = p_caducidad,
        farmaceutica    = p_farmaceutica,
        descripcion     = p_descripcion
    WHERE id_medicamento = p_id_medicamento;
END //
DELIMITER ;

-- Alteracion de la tabla trabajadores para que tenga el campo de estado.
ALTER TABLE trabajadores 
ADD estado ENUM('ACTIVO','INACTIVO') DEFAULT 'ACTIVO',
ADD observacion_salida TEXT;

-- Creacion del procedimiento almacenado para desahbilitar y reactivar al trabajador.
DROP PROCEDURE IF EXISTS sp_deshabilitar_trabajador;

DELIMITER //

CREATE PROCEDURE sp_deshabilitar_trabajador(
    IN p_id INT,
    IN p_obs TEXT
)
BEGIN
    UPDATE trabajadores
    SET 
        estado = 'INACTIVO',
        observacion_salida = p_obs
    WHERE id_trabajador = p_id;
END //

DELIMITER ;

-- Creacion del procedimiento almacenado para reactivar al trabajador.
DROP PROCEDURE IF EXISTS sp_activar_trabajador;

DELIMITER //

CREATE PROCEDURE sp_activar_trabajador(
    IN p_id INT
)
BEGIN
    UPDATE trabajadores
    SET 
        estado = 'ACTIVO',
        observacion_salida = NULL
    WHERE id_trabajador = p_id;
END //

DELIMITER ;

use medilinkprueba;
select * from trabajadores;

SHOW PROCEDURE STATUS WHERE Db = 'medilinkPrueba';

CALL sp_deshabilitar_trabajador(1, 'Renuncia voluntaria');
SELECT * FROM trabajadores WHERE id_trabajador = 1;


select * from clientes;
select * from medicamentos;
select * from trabajadores;
select * from historial;

-- 10/05/2026
-- ============================================================
-- SCRIPT DE CORRECCIONES Y MEJORAS PARA medilinkPrueba
-- ============================================================
-- Ejecutar SOBRE la base de datos existente. Limpia duplicados
-- y agrega los SPs y constraints que faltan.
-- ============================================================

use medilinkPrueba;

-- ============================================================
-- 1. AGREGAR CAMPO ESTADO A TRABAJADORES (si no existe)
-- ============================================================
SET @col_existe := (
    SELECT COUNT(*) FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name   = 'trabajadores'
      AND column_name  = 'estado'
);

SET @sql := IF(@col_existe = 0,
    'ALTER TABLE trabajadores
        ADD estado ENUM(''ACTIVO'',''INACTIVO'') DEFAULT ''ACTIVO'',
        ADD observacion_salida TEXT',
    'SELECT ''Columna estado ya existe'' AS info');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;


-- ============================================================
-- 2. ÍNDICES ÚNICOS PARA EVITAR DUPLICADOS A NIVEL BD
-- ============================================================

-- 2.1 Cliente: correo único (cuando no es NULL)
SET @existe := (SELECT COUNT(*) FROM information_schema.statistics
                WHERE table_schema = DATABASE()
                  AND table_name   = 'clientes'
                  AND index_name   = 'uk_cliente_correo');
SET @sql := IF(@existe > 0,
    'ALTER TABLE clientes DROP INDEX uk_cliente_correo',
    'SELECT ''Indice cliente correo no existia'' AS info');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

ALTER TABLE clientes ADD CONSTRAINT uk_cliente_correo UNIQUE (correo);


-- 2.2 Cliente: combinación nombre+apellidos+fecha_nacimiento única
SET @existe := (SELECT COUNT(*) FROM information_schema.statistics
                WHERE table_schema = DATABASE()
                  AND table_name   = 'clientes'
                  AND index_name   = 'uk_cliente_identidad');
SET @sql := IF(@existe > 0,
    'ALTER TABLE clientes DROP INDEX uk_cliente_identidad',
    'SELECT ''Indice cliente identidad no existia'' AS info');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

ALTER TABLE clientes
    ADD CONSTRAINT uk_cliente_identidad
    UNIQUE (nombre, ap_paterno, ap_materno, fecha_nacimiento);


-- 2.3 Trabajadores: correo único
SET @existe := (SELECT COUNT(*) FROM information_schema.statistics
                WHERE table_schema = DATABASE()
                  AND table_name   = 'trabajadores'
                  AND index_name   = 'uk_trabajador_correo');
SET @sql := IF(@existe > 0,
    'ALTER TABLE trabajadores DROP INDEX uk_trabajador_correo',
    'SELECT ''Indice trabajador correo no existia'' AS info');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

ALTER TABLE trabajadores ADD CONSTRAINT uk_trabajador_correo UNIQUE (correo);


-- ============================================================
-- 3. SPs NUEVOS Y CORREGIDOS
-- ============================================================

-- 3.1 Buscar cliente por correo
DROP PROCEDURE IF EXISTS sp_buscar_cliente_por_correo;
DELIMITER //
CREATE PROCEDURE sp_buscar_cliente_por_correo(
    IN p_correo VARCHAR(150)
)
BEGIN
    SELECT id_cliente, nombre, ap_paterno, ap_materno, correo
    FROM clientes
    WHERE LOWER(correo) = LOWER(p_correo)
    LIMIT 1;
END //
DELIMITER ;


-- 3.2 Buscar trabajador por correo
DROP PROCEDURE IF EXISTS sp_buscar_trabajador_por_correo;
DELIMITER //
CREATE PROCEDURE sp_buscar_trabajador_por_correo(
    IN p_correo VARCHAR(150)
)
BEGIN
    SELECT id_trabajador, nombre, ap_paterno, ap_materno, correo
    FROM trabajadores
    WHERE LOWER(correo) = LOWER(p_correo)
    LIMIT 1;
END //
DELIMITER ;


-- 3.3 Deshabilitar trabajador (faltaba como SP)
DROP PROCEDURE IF EXISTS sp_deshabilitar_trabajador;
DELIMITER //
CREATE PROCEDURE sp_deshabilitar_trabajador(
    IN p_id INT,
    IN p_observacion TEXT
)
BEGIN
    UPDATE trabajadores
    SET estado = 'INACTIVO',
        observacion_salida = p_observacion
    WHERE id_trabajador = p_id;
END //
DELIMITER ;


-- 3.4 Activar trabajador (estaba DUPLICADO en el script original)
DROP PROCEDURE IF EXISTS sp_activar_trabajador;
DELIMITER //
CREATE PROCEDURE sp_activar_trabajador(
    IN p_id INT
)
BEGIN
    UPDATE trabajadores
    SET estado = 'ACTIVO',
        observacion_salida = NULL
    WHERE id_trabajador = p_id;
END //
DELIMITER ;


-- 3.5 Procesar venta: versión con validación previa de stock (transaccional)
-- (Se mantiene sp_crear_venta y sp_insertar_detalle como antes,
--  la validación de stock se hace en Python con FOR UPDATE en consultas.py)


-- ============================================================
-- 4. TRIGGER: evitar stock negativo en medicamentos
-- ============================================================
DROP TRIGGER IF EXISTS trg_stock_no_negativo;
DELIMITER //
CREATE TRIGGER trg_stock_no_negativo
BEFORE UPDATE ON medicamentos
FOR EACH ROW
BEGIN
    IF NEW.stock < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El stock no puede ser negativo.';
    END IF;
END //
DELIMITER ;


-- ============================================================
-- 5. TRIGGER: evitar venta de medicamento caducado
-- ============================================================
DROP TRIGGER IF EXISTS trg_no_vender_caducado;
DELIMITER //
CREATE TRIGGER trg_no_vender_caducado
BEFORE INSERT ON detalle_ventas
FOR EACH ROW
BEGIN
    DECLARE v_caducidad DATE;
    DECLARE v_nombre VARCHAR(150);

    SELECT fecha_caducidad, nombre_producto
      INTO v_caducidad, v_nombre
    FROM medicamentos
    WHERE id_medicamento = NEW.id_medicamento;

    IF v_caducidad IS NOT NULL AND v_caducidad < CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'No se puede vender un medicamento caducado.';
    END IF;
END //
DELIMITER ;


-- ============================================================
-- 6. VERIFICACIONES
-- ============================================================
SELECT 'Script ejecutado correctamente' AS resultado;
SELECT COUNT(*) AS total_clientes        FROM clientes;
SELECT COUNT(*) AS total_medicamentos    FROM medicamentos;
SELECT COUNT(*) AS total_trabajadores    FROM trabajadores;

DELIMITER $$

CREATE PROCEDURE sp_buscar_cedula_medico(
    IN p_cedula VARCHAR(20)
)
BEGIN

    SELECT id_trabajador
    FROM trabajadores
    WHERE cedula_profesional = p_cedula
    AND puesto = 'Médico General'
    LIMIT 1;

END $$

DELIMITER ;

-- Buscar médico por cédula profesional (para validar unicidad)
DROP PROCEDURE IF EXISTS sp_buscar_cedula_medico;
DELIMITER //
CREATE PROCEDURE sp_buscar_cedula_medico(
    IN p_cedula VARCHAR(50)
)
BEGIN
    SELECT id_trabajador, nombre, ap_paterno, ap_materno,
           cedula_profesional, puesto
    FROM trabajadores
    WHERE cedula_profesional = p_cedula
      AND puesto = 'Médico General'
    LIMIT 1;
END //
DELIMITER ;

-- Opción con NULL (recomendado): guarda NULL en cedula cuando no es médico
ALTER TABLE trabajadores 
    ADD CONSTRAINT uk_cedula_profesional UNIQUE (cedula_profesional);
    
DROP PROCEDURE IF EXISTS sp_obtener_trabajador_por_id;
DELIMITER //
CREATE PROCEDURE sp_obtener_trabajador_por_id(
    IN p_id INT
)
BEGIN
    SELECT id_trabajador, nombre, ap_paterno, ap_materno,
           cedula_profesional, puesto, estado
    FROM trabajadores
    WHERE id_trabajador = p_id;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_obtener_trabajador_por_id;
DELIMITER //
CREATE PROCEDURE sp_obtener_trabajador_por_id(
    IN p_id INT
)
BEGIN
    SELECT id_trabajador, nombre, ap_paterno, ap_materno,
           cedula_profesional, puesto, estado
    FROM trabajadores
    WHERE id_trabajador = p_id;
END //
DELIMITER ;

select * from trabajadores;

-- Quitar la restricción que impide tener varios lotes del mismo medicamento
ALTER TABLE medicamentos DROP INDEX uk_medicamento_unico;

ALTER TABLE medicamentos
    ADD CONSTRAINT uk_medicamento_lote_unico
    UNIQUE (nombre_producto, presentacion, cantidad_mg, numero_lote);
    
-- 1) Agregar columna direccion a la tabla clientes
ALTER TABLE clientes
ADD COLUMN direccion VARCHAR(500) DEFAULT NULL;

-- 2) Reemplazar sp_insertar_cliente
DROP PROCEDURE IF EXISTS sp_insertar_cliente;
DELIMITER //
CREATE PROCEDURE sp_insertar_cliente(
    IN p_nombre           VARCHAR(100),
    IN p_ap_paterno       VARCHAR(100),
    IN p_ap_materno       VARCHAR(100),
    IN p_edad             INT,
    IN p_sexo             VARCHAR(20),
    IN p_fecha_nacimiento DATE,
    IN p_peso             DECIMAL(5,2),
    IN p_talla            DECIMAL(5,2),
    IN p_oxigenacion      DECIMAL(5,2),
    IN p_presion          VARCHAR(20),
    IN p_temperatura      DECIMAL(4,2),
    IN p_correo           VARCHAR(150),
    IN p_direccion        VARCHAR(500)
)
BEGIN
    INSERT INTO clientes (nombre, ap_paterno, ap_materno, edad, sexo,
                          fecha_nacimiento, peso, talla, oxigenacion,
                          presion, temperatura, correo, direccion)
    VALUES (p_nombre, p_ap_paterno, p_ap_materno, p_edad, p_sexo,
            p_fecha_nacimiento, p_peso, p_talla, p_oxigenacion,
            p_presion, p_temperatura, p_correo, p_direccion);
END //
DELIMITER ;

-- 3) Reemplazar sp_actualizar_cliente
DROP PROCEDURE IF EXISTS sp_actualizar_cliente;
DELIMITER //
CREATE PROCEDURE sp_actualizar_cliente(
    IN p_id_cliente       INT,
    IN p_nombre           VARCHAR(100),
    IN p_ap_paterno       VARCHAR(100),
    IN p_ap_materno       VARCHAR(100),
    IN p_edad             INT,
    IN p_sexo             VARCHAR(20),
    IN p_fecha_nacimiento DATE,
    IN p_peso             DECIMAL(5,2),
    IN p_talla            DECIMAL(5,2),
    IN p_oxigenacion      DECIMAL(5,2),
    IN p_presion          VARCHAR(20),
    IN p_temperatura      DECIMAL(4,2),
    IN p_correo           VARCHAR(150),
    IN p_direccion        VARCHAR(500)
)
BEGIN
    UPDATE clientes
    SET nombre           = p_nombre,
        ap_paterno       = p_ap_paterno,
        ap_materno       = p_ap_materno,
        edad             = p_edad,
        sexo             = p_sexo,
        fecha_nacimiento = p_fecha_nacimiento,
        peso             = p_peso,
        talla            = p_talla,
        oxigenacion      = p_oxigenacion,
        presion          = p_presion,
        temperatura      = p_temperatura,
        correo           = p_correo,
        direccion        = p_direccion
    WHERE id_cliente = p_id_cliente;
END //
DELIMITER ;

select * from clientes;
select * from trabajadores;

use medilinkprueba;

-- 1) Agregar columna estado a clientes
ALTER TABLE clientes
ADD COLUMN estado VARCHAR(20) DEFAULT 'ACTIVO';

-- 2) SP para deshabilitar cliente
DROP PROCEDURE IF EXISTS sp_deshabilitar_cliente;
DELIMITER //
CREATE PROCEDURE sp_deshabilitar_cliente(
    IN p_id_cliente  INT,
    IN p_observacion TEXT
)
BEGIN
    UPDATE clientes
    SET estado      = 'INACTIVO',
        observacion = p_observacion
    WHERE id_cliente = p_id_cliente;
END //
DELIMITER ;

-- 3) SP para reactivar cliente
DROP PROCEDURE IF EXISTS sp_activar_cliente;
DELIMITER //
CREATE PROCEDURE sp_activar_cliente(
    IN p_id_cliente INT
)
BEGIN
    UPDATE clientes
    SET estado      = 'ACTIVO',
        observacion = NULL
    WHERE id_cliente = p_id_cliente;
END //
DELIMITER ;

ALTER TABLE clientes
ADD COLUMN observacion TEXT DEFAULT NULL;

select * from clientes;