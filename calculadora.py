import math
from scipy.stats import t

# --- LÓGICA CENTRAL REUTILIZABLE ---

def calcular_un_volumen_corregido(masa_g, factores):
    """
    Aplica la fórmula principal para convertir una única medición de masa (en g)
    a un volumen corregido (en µL).
    """
    masa_kg = masa_g / 1000.0
    
    # V_20 = m * (1/(ρ_w - ρ_a)) * (1 - α(t_w - 20))
    # Se elimina el factor 'pesa' (Z2) de la fórmula principal, según el análisis del documento del cliente.
    # La fórmula ahora es: V_20 = masa_kg * Z1 * Z3
    volumen_m3 = masa_kg * factores['flotacion'] * factores['dilatacion']
    # Convertir de m³ a µL (1 m³ = 1e9 µL) y redondear
    # Se elimina el redondeo intermedio para mantener la máxima precisión.
    return volumen_m3 * 1e9

def calcular_factores_de_correccion(promedios_ambientales, constantes):
    """
    Calcula los factores de corrección (P65, P70, P78) para un aforo específico,
    basado en sus condiciones ambientales promedio.
    """
    p_temp_agua = promedios_ambientales['temp_agua']
    p_temp_aire = promedios_ambientales['temp_amb']
    p_presion_hpa = promedios_ambientales['presion']
    p_humedad_rel = promedios_ambientales['humedad']

    c = constantes # constantes del frontend (contiene tanaka_a1, etc.)

    # Densidad del Agua (ρ_A) - Ecuación de Tanaka según el documento
    # PA = a5 * [1 - ((ta + a1)² * (ta + a2)) / (a3 * (ta + a4))]
    numerador = (p_temp_agua + c['tanaka_a1'])**2 * (p_temp_agua + c['tanaka_a2'])
    denominador = c['tanaka_a3'] * (p_temp_agua + c['tanaka_a4'])
    rho_agua = c['tanaka_a5'] * (1 - (numerador / denominador))

    # Densidad del Aire (ρ_a) - Fórmula CIPM-2007 (implementación del Excel)
    # Esta fórmula usa las constantes del frontend que ya están cargadas
    exp_term = math.exp(c['rho_aire_o53'] * p_temp_aire)
    rho_aire = ((c['rho_aire_o51'] * p_presion_hpa) - (c['rho_aire_o52'] * p_humedad_rel * exp_term)) / (273.15 + p_temp_aire)
    
    factor_flotacion = 1 / (rho_agua - rho_aire) if (rho_agua - rho_aire) != 0 else 1
    factor_pesa = 1 - (rho_aire / c['rho_pesa_n74'])
    factor_dilatacion = 1 - (c['alpha_material_pp'] * (p_temp_agua - 20))
    
    return {
        'flotacion': factor_flotacion,
        'pesa': factor_pesa,
        'dilatacion': factor_dilatacion,
        'rho_agua': rho_agua,
        'rho_aire': rho_aire
    }

def corregir_y_promediar_condiciones(mediciones_ambientales, constantes):
    """
    Toma las 10 mediciones ambientales de un aforo, aplica la fórmula de corrección
    cuadrática a cada una y devuelve el promedio de cada magnitud.
    """
    if not mediciones_ambientales:
        return {'temp_agua': 0, 'temp_amb': 0, 'presion': 0, 'humedad': 0}

    num_mediciones = len(mediciones_ambientales)

    # 1. Calcular el promedio de los valores brutos
    promedio_temp_agua = sum(med['temp_agua'] for med in mediciones_ambientales) / num_mediciones
    promedio_temp_amb = sum(med['temp_amb'] for med in mediciones_ambientales) / num_mediciones
    promedio_presion = sum(med['presion'] for med in mediciones_ambientales) / num_mediciones
    promedio_humedad = sum(med['humedad'] for med in mediciones_ambientales) / num_mediciones

    # 2. Aplicar la corrección cuadrática al promedio (restando, según el documento)
    # CORRECCIÓN: Se revierte a la suma para coincidir con el comportamiento del Excel validado.
    corr_t_agua = (constantes['corr_ta_y']['a'] * promedio_temp_agua**2) + (constantes['corr_ta_y']['b'] * promedio_temp_agua) + constantes['corr_ta_y']['c']
    temp_agua_final = promedio_temp_agua + corr_t_agua

    corr_t_amb = (constantes['corr_tamb_y']['a'] * promedio_temp_amb**2) + (constantes['corr_tamb_y']['b'] * promedio_temp_amb) + constantes['corr_tamb_y']['c']
    temp_amb_final = promedio_temp_amb + corr_t_amb

    corr_presion = (constantes['corr_patm_y']['a'] * promedio_presion**2) + (constantes['corr_patm_y']['b'] * promedio_presion) + constantes['corr_patm_y']['c']
    presion_final = promedio_presion + corr_presion

    corr_humedad = (constantes['corr_hr_y']['a'] * promedio_humedad**2) + (constantes['corr_hr_y']['b'] * promedio_humedad) + constantes['corr_hr_y']['c']
    humedad_final = promedio_humedad + corr_humedad

    return {
        'temp_agua': temp_agua_final,
        'temp_amb': temp_amb_final,
        'presion': presion_final,
        'humedad': humedad_final,
    }

def generar_textos_reporte(entradas_generales, resultados_aforos, especificaciones_patrones, site_config):
    """
    Genera los textos dinámicos del reporte.
    """
    # Construir el párrafo descriptivo inicial
    eg = entradas_generales
    texto_intro = f"Los resultados que a continuación se emiten, corresponden al servicio de {eg.get('descripcion_instrumento', '')} tipo {eg.get('tipo_instrumento', '')}"
    
    if eg.get('marca_instrumento') and eg.get('marca_instrumento').lower() not in ['s/m', 'na', 'n.a', 'n/a']:
        texto_intro += f", marca: {eg.get('marca_instrumento')}"
    if eg.get('modelo_instrumento') and eg.get('modelo_instrumento').lower() not in ['s/m', 'na', 'n.a', 'n/a']:
        texto_intro += f", modelo: {eg.get('modelo_instrumento')}"
    if eg.get('serie_instrumento') and eg.get('serie_instrumento').lower() not in ['s/n', 'na', 'n.a', 'n/a']:
        texto_intro += f", número de serie: {eg.get('serie_instrumento')}"
    if eg.get('id_instrumento') and eg.get('id_instrumento').lower() not in ['s/i', 'na', 'n.a', 'n/a']:
        texto_intro += f", identificación: {eg.get('id_instrumento')}"

    # Volumen nominal o intervalo
    vol_min = eg.get('intervalo_min_reporte')
    vol_max = eg.get('intervalo_max_reporte')
    unidades = eg.get('unidades', '')
    if vol_min and vol_max:
        texto_intro += f", con intervalo de medida de {vol_min} a {vol_max} {unidades}"
    elif vol_min:
        texto_intro += f", con volumen nominal de {vol_min} {unidades}"

    # Tipo de calibración (Contener/Entregar)
    tipo_cal = "contener." if eg.get('tipo_calibracion', '').upper() == 'TC' else "entregar."
    texto_intro += f", calibrado para {tipo_cal}"

    # Crear una versión del texto para el certificado
    texto_intro_certificado = texto_intro.replace("servicio de", "calibración de", 1)


    # Generar el texto de Observaciones
    unidades = eg.get('unidades', 'ul')
    valores_nominales = [f"{a['valor_nominal']:.0f} {unidades}" for a in resultados_aforos]
    cond_iniciales = eg.get('condiciones_iniciales', {})
    resultados_iniciales = [
        f"{cond_iniciales.get('promedio1', 0):.2f} {unidades}",
        f"{cond_iniciales.get('promedio2', 0):.2f} {unidades}",
        f"{cond_iniciales.get('promedio3', 0):.2f} {unidades}",
    ]
    
    palabra_clave = "ajuste" if eg.get('ajuste_realizado') == 'S' else "calibración"
    
    observaciones_texto = (f"Los resultados obtenidos antes de la {palabra_clave} del instrumento para {', '.join(valores_nominales)} "
                           f"fueron respectivamente {', '.join(resultados_iniciales)}.")

    # Buscar la especificación del patrón principal
    codigo_patron_principal = entradas_generales.get('patron_seleccionado')
    especificacion_principal = especificaciones_patrones.get(codigo_patron_principal, {}).get('descripcion', "Especificación no encontrada.")

    # Buscar especificaciones de los patrones auxiliares
    codigo_patron_ta = entradas_generales.get('auxiliar_ta')
    especificacion_ta = especificaciones_patrones.get(codigo_patron_ta, {}).get('descripcion', "Especificación no encontrada.")

    codigo_patron_ca = entradas_generales.get('auxiliar_ca')
    especificacion_ca = especificaciones_patrones.get(codigo_patron_ca, {}).get('descripcion', "Especificación no encontrada.")

    # Obtener el lugar de servicio desde la configuración del sitio
    lugar_servicio = site_config.get('lugar_servicio', 'Lugar no especificado.')

    # Obtener la trazabilidad nacional
    trazabilidad_nacional = site_config.get('trazabilidad_metrologica_nacional', 'Trazabilidad no especificada.')

    # Obtener el procedimiento utilizado
    procedimiento_utilizado = site_config.get('procedimiento_utilizado', 'Procedimiento no especificado.')

    # Obtener la lista de mantenimientos realizados
    mantenimientos_realizados = entradas_generales.get('mantenimientos', [])

    # Obtener las notas y observaciones para el certificado
    notas_certificado = site_config.get('notas_observaciones_certificado', [])

    return {
        "introduccion": texto_intro,
        "introduccion_certificado": texto_intro_certificado,
        "observaciones": observaciones_texto,
        "especificacion_principal": especificacion_principal,
        "especificacion_ta": especificacion_ta,
        "especificacion_ca": especificacion_ca,
        "lugar_servicio": lugar_servicio,
        "trazabilidad_nacional": trazabilidad_nacional,
        "procedimiento_utilizado": procedimiento_utilizado,
        "mantenimientos": mantenimientos_realizados,
        "notas_certificado": notas_certificado,
        "unidades": eg.get('unidades', 'µL')
    }

def buscar_emt(valor_nominal_ul, emt_config, clase_instrumento):
    """
    Busca el Error Máximo Tolerado (EMT) en la configuración para una coincidencia exacta del volumen.
    """
    # Usar la tabla de la clase específica si existe, si no, usar la 'default'.
    tabla_emts = emt_config.get(clase_instrumento, emt_config.get('default', []))

    # Busca una coincidencia exacta como BUSCARV con el último argumento en 0 o FALSO.
    for limite in tabla_emts:
        if valor_nominal_ul == limite['alcance_ul']:
            return limite['emt_ul']

    # Si no se encuentra una coincidencia exacta, devuelve 0 o un valor por defecto.
    return 0

# --- FUNCIÓN PRINCIPAL ---

def procesar_todos_los_aforos(data):
    """
    Función principal que orquesta todo el proceso de cálculo.
    """
    constantes = data['constantes']
    entradas_generales = data['entradas_generales']
    especificaciones_patrones = data.get('especificaciones_patrones', {})
    debug_mode = entradas_generales.get('debug_mode', False)
    emts_config = data.get('emts_config', {})
    # Añadir la resolución del instrumento a las constantes para usarla en el cálculo de incertidumbre
    tolerancia_instrumento = entradas_generales.get('tolerancia', 0)
    constantes['div_min_valor'] = entradas_generales.get('div_min_valor', 0)

    site_config = data.get('site_config', {})
    resultados_por_aforo = []

    promedios_ambientales_aforos = []

    # --- CÁLCULO DE EMT COMÚN PARA TODOS LOS CANALES ---
    # 1. Encontrar el valor nominal máximo de los tres aforos.
    max_valor_nominal = max(data['aforo1']['valor_nominal'], data['aforo2']['valor_nominal'], data['aforo3']['valor_nominal'])
    
    # 2. Buscar el EMT una sola vez usando ese valor máximo.
    clase_instrumento = entradas_generales.get('clase_instrumento', 'default').lower()
    emt_comun = buscar_emt(max_valor_nominal, emts_config, clase_instrumento)

    # Obtener el valor nominal del último aforo, que se usará como divisor para el error porcentual
    valor_nominal_ref_porcentaje = data['aforo3']['valor_nominal']

    # --- Lógica de dos cerebros: uno para la pantalla, otro para los cálculos ---
    # 1. Constantes para la corrección interna (lógica PDF)
    constantes_pdf = {
        'corr_ta_y': { 'a': 0.0005, 'b': 0.0025, 'c': 0.05 },
        'corr_tamb_y': { 'a': 0.0109, 'b': -0.45, 'c': 4.6637 },
        'corr_hr_y': { 'a': 0.0008, 'b': -0.1635, 'c': 5.7469 },
        'corr_patm_y': { 'a': 0.0001, 'b': -0.1526, 'c': 60.12 },
    }

    def corregir_para_pdf(promedios_brutos):
        # Esta función aplica la lógica de corrección del PDF (restando)
        temp_agua = promedios_brutos['temp_agua'] - ((constantes_pdf['corr_ta_y']['a'] * promedios_brutos['temp_agua']**2) + (constantes_pdf['corr_ta_y']['b'] * promedios_brutos['temp_agua']) + constantes_pdf['corr_ta_y']['c'])
        temp_amb = promedios_brutos['temp_amb'] - ((constantes_pdf['corr_tamb_y']['a'] * promedios_brutos['temp_amb']**2) + (constantes_pdf['corr_tamb_y']['b'] * promedios_brutos['temp_amb']) + constantes_pdf['corr_tamb_y']['c'])
        presion = promedios_brutos['presion'] - ((constantes_pdf['corr_patm_y']['a'] * promedios_brutos['presion']**2) + (constantes_pdf['corr_patm_y']['b'] * promedios_brutos['presion']) + constantes_pdf['corr_patm_y']['c'])
        humedad = promedios_brutos['humedad'] - ((constantes_pdf['corr_hr_y']['a'] * promedios_brutos['humedad']**2) + (constantes_pdf['corr_hr_y']['b'] * promedios_brutos['humedad']) + constantes_pdf['corr_hr_y']['c'])
        return {'temp_agua': temp_agua, 'temp_amb': temp_amb, 'presion': presion, 'humedad': humedad}
    # --- Fin de la lógica de dos cerebros ---

    for i in range(1, 4):
        aforo_key = f'aforo{i}'
        aforo_data = data[aforo_key]
        
        promedios_ambientales = corregir_y_promediar_condiciones(
            aforo_data['mediciones_ambientales'],
            constantes
        )
        promedios_ambientales_aforos.append(promedios_ambientales)
        
        # Calcular promedios brutos para la lógica interna
        num_mediciones = len(aforo_data['mediciones_ambientales'])
        promedios_brutos = {
            'temp_agua': sum(med['temp_agua'] for med in aforo_data['mediciones_ambientales']) / num_mediciones,
            'temp_amb': sum(med['temp_amb'] for med in aforo_data['mediciones_ambientales']) / num_mediciones,
            'presion': sum(med['presion'] for med in aforo_data['mediciones_ambientales']) / num_mediciones,
            'humedad': sum(med['humedad'] for med in aforo_data['mediciones_ambientales']) / num_mediciones,
        }
        promedios_internos_pdf = corregir_para_pdf(promedios_brutos)

        factores = calcular_factores_de_correccion(
            promedios_internos_pdf, # <-- Usamos los valores corregidos según el PDF
            constantes
        )

        volumenes_corregidos_ul = [
            calcular_un_volumen_corregido(masa_g, factores)
            for masa_g in aforo_data['mediciones_masa']
        ]
        
        # Asegurarnos de que espec_patron sea un diccionario, incluso si no se encuentra.
        patron_key = entradas_generales.get('patron_seleccionado')
        espec_patron = especificaciones_patrones.get(patron_key) if patron_key else {}
        if espec_patron is None or not isinstance(espec_patron, dict):
            espec_patron = {}
        
        # --- CÁLCULO DE INCERTIDUMBRE (Lógica corregida y unificada) ---
        # PASO 6: INCERTIDUMBRES ESTÁNDAR u(x)
        u_R_kg = 2.8867e-8
        u_C_kg = 7.5e-8
        u_E_kg = 2.31e-8
        u_M_kg = math.sqrt(u_R_kg**2 + u_C_kg**2 + u_E_kg**2)
        
        u_tA_C = 0.0757
        d_rhoA_dtA = -0.2236
        u_CmPA_kg_m3 = 4.15e-4
        u_rho_A_kg_m3 = math.sqrt((d_rhoA_dtA * u_tA_C)**2 + u_CmPA_kg_m3**2)
        
        u_rho_a_kg_m3_sq = 1.9688e-6
        u_rho_a_kg_m3 = math.sqrt(u_rho_a_kg_m3_sq)
        
        rho_B = constantes['rho_pesa_n74']
        u_rho_B_kg_m3 = (rho_B * 0.03) / math.sqrt(12)
        
        gamma = constantes['alpha_material_pp']
        u_gamma_C = (gamma * 0.2) / math.sqrt(12)
        
        tr = promedios_ambientales['temp_agua']
        u_tr_C = 0.0786
        
        volumenes_corregidos_m3 = [v / 1e9 for v in volumenes_corregidos_ul]
        if len(volumenes_corregidos_m3) > 1:
            media_vol = sum(volumenes_corregidos_m3) / len(volumenes_corregidos_m3)
            desv_est_vol = math.sqrt(sum([(v - media_vol)**2 for v in volumenes_corregidos_m3]) / (len(volumenes_corregidos_m3) - 1))
            u_Crep_m3 = desv_est_vol / math.sqrt(len(volumenes_corregidos_m3))
        else:
            u_Crep_m3 = 0
            
        u_Cres_m3 = (constantes.get('div_min_valor', 0) / 1e9) / math.sqrt(12)
        u_Crepro_m3 = 0.23 / 1e9
        
        # PASO 7: COEFICIENTES DE SENSIBILIDAD cᵢ
        V20_prom_m3 = sum(volumenes_corregidos_m3) / len(volumenes_corregidos_m3) if volumenes_corregidos_m3 else 0
        masas_kg = [m / 1000.0 for m in aforo_data['mediciones_masa']]
        masa_aparente_prom_kg = sum(masas_kg) / len(masas_kg) if masas_kg else 0
        
        rho_A = factores['rho_agua']
        rho_a = factores['rho_aire']
        
        c_Mo = -V20_prom_m3 / masa_aparente_prom_kg if masa_aparente_prom_kg != 0 else 0
        c_Mi = V20_prom_m3 / masa_aparente_prom_kg if masa_aparente_prom_kg != 0 else 0
        c_rho_A = -V20_prom_m3 / (rho_A - rho_a) if (rho_A - rho_a) != 0 else 0
        c_rho_a = V20_prom_m3 * (1/(rho_A - rho_a) - 1/(rho_B - rho_a)) if (rho_A - rho_a) != 0 and (rho_B - rho_a) != 0 else 0
        c_rho_B = V20_prom_m3 * rho_a / (rho_B * (rho_B - rho_a)) if rho_B != 0 and (rho_B - rho_a) != 0 else 0
        c_gamma = -V20_prom_m3 * (tr - 20) / (1 - gamma * (tr - 20)) if (1 - gamma * (tr - 20)) != 0 else 0
        c_tr = -V20_prom_m3 * gamma / (1 - gamma * (tr - 20)) if (1 - gamma * (tr - 20)) != 0 else 0
        
        # PASO 8: INCERTIDUMBRE COMBINADA u_c(V₂₀)
        u_y_Mo = c_Mo * u_M_kg
        u_y_Mi = c_Mi * u_M_kg
        u_y_rho_A = c_rho_A * u_rho_A_kg_m3
        u_y_rho_a = c_rho_a * u_rho_a_kg_m3
        u_y_rho_B = c_rho_B * u_rho_B_kg_m3
        u_y_gamma = c_gamma * u_gamma_C
        u_y_tr = c_tr * u_tr_C
        u_y_Crep = u_Crep_m3      # Coeficiente de sensibilidad es 1
        u_y_Cres = u_Cres_m3      # Coeficiente de sensibilidad es 1
        u_y_Crepro = u_Crepro_m3  # Coeficiente de sensibilidad es 1
        
        u_c_sq = (u_y_Mo**2 + u_y_Mi**2 + u_y_rho_A**2 + u_y_rho_a**2 + u_y_rho_B**2 +
                  u_y_gamma**2 + u_y_tr**2 + u_y_Crep**2 + u_y_Cres**2 + u_y_Crepro**2)
        u_c_m3 = math.sqrt(u_c_sq)
        
        # PASO 9: INCERTIDUMBRE EXPANDIDA U
        v_rep = len(masas_kg) - 1 if len(masas_kg) > 1 else float('inf')
        if u_c_m3 > 0 and v_rep != float('inf') and u_y_Crep != 0:
            denominador_v_eff = (u_y_Crep**4) / v_rep
            v_eff = (u_c_m3**4) / denominador_v_eff if denominador_v_eff > 0 else float('inf')
        else:
            v_eff = float('inf')

        k = 2.0 if v_eff >= 100 else t.ppf(1 - 0.0455 / 2, df=max(1, round(v_eff))) # Usar k=2 para v_eff grandes
        incertidumbre = (u_c_m3 * k) * 1e9
        
        if debug_mode:
            print(f"\n\n=== DIAGNÓSTICO UNIFICADO CANAL {i} ===")
            print("\n--- PASO 6: INCERTIDUMBRES ESTÁNDAR (u_i) ---")
            print(f"  u(Masa): {u_M_kg:.6e} kg")
            print(f"  u(Temp Agua): {u_tA_C:.6f} °C")
            print(f"  u(Densidad Agua): {u_rho_A_kg_m3:.6f} kg/m³")
            print(f"  u(Densidad Aire): {u_rho_a_kg_m3:.6f} kg/m³")
            print(f"  u(Densidad Pesa): {u_rho_B_kg_m3:.6f} kg/m³")
            print(f"  u(Gamma): {u_gamma_C:.6e} °C⁻¹")
            print(f"  u(Temp Recipiente): {u_tr_C:.6f} °C")
            print(f"  u(Repetibilidad): {u_Crep_m3:.6e} m³")
            print(f"  u(Resolución): {u_Cres_m3:.6e} m³")
            print(f"  u(Reproducibilidad): {u_Crepro_m3:.6e} m³")

            print("\n--- VALORES INTERMEDIOS CLAVE ---")
            print(f"  Densidad del Agua (ρ_A) calculada: {rho_A:.4f} kg/m³")
            print(f"  Densidad del Aire (ρ_a) calculada: {rho_a:.4f} kg/m³")
            print(f"  Factor Flotación (Z1) calculado: {factores['flotacion']:.6f}")
            print(f"  Factor Dilatación (Z3) calculado: {factores['dilatacion']:.6f}")
            
            print("\n--- PASO 7: COEFICIENTES DE SENSIBILIDAD (c_i) ---")
            print(f"  c(Masa): {c_Mi:.6f} m³/kg")
            print(f"  c(Densidad Agua): {c_rho_A:.6e} m³/ (kg/m³)")
            # ... (se pueden añadir más si es necesario)

            print("\n--- PASO 8 y 9: RESULTADOS ---")
            print(f"  Incertidumbre Combinada (u_c): {u_c_m3 * 1e9:.6f} µL")
            print(f"  Grados de Libertad (v_eff): {v_eff:.2f}")
            print(f"  Factor de Cobertura (k): {k:.4f}")
            print(f"  Incertidumbre Expandida (U): {incertidumbre:.6f} µL")

        if not volumenes_corregidos_ul:
            promedio_volumen = 0
        else:
            promedio_volumen = sum(volumenes_corregidos_ul) / len(volumenes_corregidos_ul)
            
        error_medida = promedio_volumen - aforo_data['valor_nominal']
        
        # Calcular el error de medida en porcentaje
        # Se usa el valor nominal del Aforo 3 como divisor para todos, según la fórmula del Excel.
        error_porcentaje = 0
        if valor_nominal_ref_porcentaje != 0:
            error_porcentaje = abs(error_medida / valor_nominal_ref_porcentaje) * 100

        if debug_mode:
            print(f"\n--- CÁLCULO ERROR % CANAL {i} ---")
            print(f"  Error de Medida (µL) [J83]: {error_medida:.6f}")
            print(f"  Valor Nominal Canal 3 (µL) [D85]: {valor_nominal_ref_porcentaje:.2f}")
            print(f"  Fórmula: abs({error_medida:.6f} / {valor_nominal_ref_porcentaje:.2f}) * 100")
            print(f"  Resultado Error %: {error_porcentaje:.4f}")

        resultados_por_aforo.append({
            "valor_nominal": aforo_data['valor_nominal'],
            "promedio_volumen_ul": promedio_volumen,
            "error_medida_ul": error_medida,
            "mediciones_volumen_ul": volumenes_corregidos_ul,
            "error_medida_porcentaje": error_porcentaje,
            "incertidumbre_expandida": incertidumbre,
            "emt": emt_comun
        })

    condiciones_finales = {
        "temp_liquido": sum(p['temp_agua'] for p in promedios_ambientales_aforos) / 3,
        "temp_ambiente": sum(p['temp_amb'] for p in promedios_ambientales_aforos) / 3,
        "presion": sum(p['presion'] for p in promedios_ambientales_aforos) / 3,
        "humedad": sum(p['humedad'] for p in promedios_ambientales_aforos) / 3,
    }

    textos = generar_textos_reporte(entradas_generales, resultados_por_aforo, especificaciones_patrones, site_config)

    return {
        "aforos": resultados_por_aforo,
        "textos_reporte": textos,
        "condiciones_finales": condiciones_finales
    }
