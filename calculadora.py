import math
from scipy.stats import t

# --- LÓGICA CENTRAL REUTILIZABLE ---

def calcular_un_volumen_corregido(masa_g, factores):
    """
    Aplica la fórmula principal para convertir una única medición de masa (en g)
    a un volumen corregido (en µL).
    """
    masa_kg = masa_g / 1000.0
    
    # V_20 = m * (1/(ρ_w - ρ_a)) * (1 - ρ_a/ρ_p) * (1 - α(t_w - 20))
    volumen_m3 = masa_kg * factores['flotacion'] * factores['pesa'] * factores['dilatacion']
    
    # Convertir de m³ a µL (1 m³ = 1e9 µL) y redondear
    volumen_ul = round(volumen_m3 * 1e9, 4)
    return volumen_ul

def calcular_factores_de_correccion(promedios_ambientales, constantes):
    """
    Calcula los factores de corrección (P65, P70, P78) para un aforo específico,
    basado en sus condiciones ambientales promedio.
    """
    p_temp_agua = promedios_ambientales['temp_agua']
    p_temp_amb = promedios_ambientales['temp_amb']
    p_presion = promedios_ambientales['presion']
    p_humedad = promedios_ambientales['humedad']

    c = constantes
    # Fórmula de densidad del agua (Tanaka, M. et al. Metrologia 2001, 38, 301-309)
    # Corregida para coincidir con la estructura del Excel.
    # ρw = O37 * (1 - ( ((P21+O33)^2 * (P21+O34)) / (O35 * (P21+O36)) )) + O55
    numerador = (p_temp_agua + (-3.983035))**2 * (p_temp_agua + 301.797)
    denominador = 522528.9 * (p_temp_agua + 69.34881)
    rho_agua = 999.97495 * (1 - (numerador / denominador)) + 0

    # Formula CIPM-2007
    exp_term = math.exp(c['rho_aire_o53'] * p_temp_amb)
    rho_aire = ((c['rho_aire_o51'] * p_presion) - (c['rho_aire_o52'] * p_humedad * exp_term)) / (273.15 + p_temp_amb)
    
    factor_flotacion = 1 / (rho_agua - rho_aire) if (rho_agua - rho_aire) != 0 else 1
    factor_pesa = 1 - (rho_aire / c['rho_pesa_n74'])
    factor_dilatacion = 1 - (c['alpha_material_pp'] * (p_temp_agua - 20))
    
    return {
        'flotacion': factor_flotacion,
        'pesa': factor_pesa,
        'dilatacion': factor_dilatacion
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

    # 2. Aplicar la corrección cuadrática al promedio
    corr_t_agua = (constantes['a_temp_agua'] * promedio_temp_agua**2) + (constantes['b_temp_agua'] * promedio_temp_agua) + constantes['c_temp_agua']
    temp_agua_final = promedio_temp_agua + corr_t_agua

    corr_t_amb = (constantes['a_temp_amb'] * promedio_temp_amb**2) + (constantes['b_temp_amb'] * promedio_temp_amb) + constantes['c_temp_amb']
    temp_amb_final = promedio_temp_amb + corr_t_amb

    corr_presion = (constantes['a_presion'] * promedio_presion**2) + (constantes['b_presion'] * promedio_presion) + constantes['c_presion']
    presion_final = promedio_presion + corr_presion

    corr_humedad = (constantes['a_humedad'] * promedio_humedad**2) + (constantes['b_humedad'] * promedio_humedad) + constantes['c_humedad']
    humedad_final = promedio_humedad + corr_humedad

    return {
        'temp_agua': temp_agua_final,
        'temp_amb': temp_amb_final,
        'presion': presion_final,
        'humedad': humedad_final,
    }

def calcular_incertidumbre(aforo_data, factores, promedios_ambientales, espec_patron, constantes, volumenes_corregidos_ul):
    """
    Calcula la incertidumbre expandida para un aforo.
    """
    # --- 1. INCERTIDUMBRES ESTÁNDAR (u_i) ---

    # 1.1. Incertidumbre de la balanza (u_cal) en kg
    resolucion_kg = espec_patron.get('resolucion_g', 0) / 1000.0
    incert_max_kg = espec_patron.get('incertidumbre_max_g', 0) / 1000.0
    excentricidad_kg = espec_patron.get('excentricidad_max_g', 0) / 1000.0
    u_cal = math.sqrt((resolucion_kg / math.sqrt(12))**2 + (incert_max_kg / 2)**2 + (excentricidad_kg / math.sqrt(12))**2)

    # 1.2. Incertidumbre por repetibilidad (u_rep) en kg
    masas_kg = [m / 1000.0 for m in aforo_data['mediciones_masa']]
    if len(masas_kg) < 2:
        desv_est_masa = 0
    else:
        media_masa = sum(masas_kg) / len(masas_kg)
        desv_est_masa = math.sqrt(sum([(x - media_masa)**2 for x in masas_kg]) / (len(masas_kg) - 1))
    u_rep = desv_est_masa / math.sqrt(len(masas_kg)) if len(masas_kg) > 0 else 0

    # 1.3. Incertidumbre por resolución del instrumento (u_res) en m³
    resolucion_instrumento_ul = constantes.get('div_min_valor', 0)
    u_res_m3 = (resolucion_instrumento_ul / 1e9) / math.sqrt(12)

    # 1.4. Incertidumbre por temperatura del agua (u_temp_agua) en °C
    u_temp_agua_C = 0.1 / math.sqrt(3) # Asumiendo incertidumbre de termómetro de 0.1 °C

    # --- 2. COEFICIENTES DE SENSIBILIDAD (c_i) ---

    # Promedios necesarios para los coeficientes
    volumenes_corregidos_m3 = [v / 1e9 for v in volumenes_corregidos_ul]
    avg_vol_m3 = sum(volumenes_corregidos_m3) / len(volumenes_corregidos_m3) if volumenes_corregidos_m3 else 0
    avg_masa_kg = sum(masas_kg) / len(masas_kg) if masas_kg else 0

    # c_masa: Sensibilidad del volumen al cambio en masa (dV/dm). En Excel: -O103/O19
    # O103 es avg_vol_m3, O19 es avg_masa_kg.
    # El signo negativo es crucial y faltaba en implementaciones anteriores.
    c_masa = - (avg_vol_m3 / avg_masa_kg) if avg_masa_kg != 0 else 0

    # c_temp_agua: Sensibilidad del volumen al cambio en temp. del agua (dV/dTw).
    c_temp_agua = -avg_vol_m3 * constantes['alpha_material_pp']

    # --- 3. CONTRIBUCIONES A LA INCERTIDUMBRE COMBINADA (u_i(y) = c_i * u_i) en m³ ---
    u_y_cal = c_masa * u_cal
    u_y_rep = c_masa * u_rep
    u_y_res = u_res_m3 # La resolución ya está en m³, su coeficiente es 1.
    u_y_temp_agua = c_temp_agua * u_temp_agua_C

    # --- 4. INCERTIDUMBRE COMBINADA (u_c) en m³ ---
    u_c_m3 = math.sqrt(u_y_cal**2 + u_y_rep**2 + u_y_res**2 + u_y_temp_agua**2)

    # --- 5. GRADOS DE LIBERTAD EFECTIVOS (v_eff) ---
    # Fórmula de Welch-Satterthwaite: v_eff = u_c^4 / sum( u_i(y)^4 / v_i )
    v_cal = float('inf') # Asumimos que la incertidumbre del patrón es muy confiable
    v_rep = len(masas_kg) - 1 if len(masas_kg) > 1 else float('inf')
    v_res = float('inf')
    v_temp_agua = float('inf')

    denominador_v_eff = 0
    if v_cal != float('inf'): denominador_v_eff += (u_y_cal**4) / v_cal
    if v_rep != float('inf'): denominador_v_eff += (u_y_rep**4) / v_rep
    if v_res != float('inf'): denominador_v_eff += (u_y_res**4) / v_res
    if v_temp_agua != float('inf'): denominador_v_eff += (u_y_temp_agua**4) / v_temp_agua

    v_eff = (u_c_m3**4) / denominador_v_eff if denominador_v_eff > 0 else float('inf')

    # --- 6. FACTOR DE COBERTURA (k) ---
    # Usamos t.ppf para replicar DISTR.T.INV de Excel para un 95.45% de confianza (alpha=0.0455)
    df = max(1, round(v_eff)) # Grados de libertad no pueden ser menores a 1
    k = t.ppf(1 - 0.0455 / 2, df=df) if df != float('inf') else 2.0

    # --- 7. INCERTIDUMBRE EXPANDIDA (U) ---
    U_m3 = u_c_m3 * k
    U_ul = U_m3 * 1e9 # Convertir de m³ a µL

    return U_ul

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
        "unidades": eg.get('unidades', 'µL')
    }

def diagnosticar_incertidumbre(aforo_data, factores, promedios_ambientales, espec_patron, constantes, volumenes_corregidos_ul, canal_numero):
    """
    Función de diagnóstico que imprime paso a paso todos los cálculos de incertidumbre
    para comparar con Excel.
    """
    print(f"\n=== DIAGNÓSTICO INCERTIDUMBRE CANAL {canal_numero} ===")
    
    # --- 1. INCERTIDUMBRES ESTÁNDAR (u_i) ---
    print("\n1. INCERTIDUMBRES ESTÁNDAR:")
    
    # 1.1. Incertidumbre de la balanza (u_cal) en kg
    resolucion_kg = espec_patron.get('resolucion_g', 0) / 1000.0
    incert_max_kg = espec_patron.get('incertidumbre_max_g', 0) / 1000.0
    excentricidad_kg = espec_patron.get('excentricidad_max_g', 0) / 1000.0
    
    print(f"  Resolución balanza: {resolucion_kg:.6f} kg")
    print(f"  Incert. máx balanza: {incert_max_kg:.6f} kg")
    print(f"  Excentricidad balanza: {excentricidad_kg:.6f} kg")
    
    u_cal = math.sqrt((resolucion_kg / math.sqrt(12))**2 + (incert_max_kg / 2)**2 + (excentricidad_kg / math.sqrt(12))**2)
    print(f"  u_cal = {u_cal:.9f} kg")

    # 1.2. Incertidumbre por repetibilidad (u_rep) en kg
    masas_kg = [m / 1000.0 for m in aforo_data['mediciones_masa']]
    print(f"  Masas (kg): {[f'{m:.6f}' for m in masas_kg[:5]]}...") # Solo mostrar primeras 5
    
    if len(masas_kg) < 2:
        desv_est_masa = 0
    else:
        media_masa = sum(masas_kg) / len(masas_kg)
        varianza = sum([(x - media_masa)**2 for x in masas_kg]) / (len(masas_kg) - 1)
        desv_est_masa = math.sqrt(varianza)
        print(f"  Media masa: {media_masa:.6f} kg")
        print(f"  Desv. estándar: {desv_est_masa:.9f} kg")
    
    u_rep = desv_est_masa / math.sqrt(len(masas_kg)) if len(masas_kg) > 0 else 0
    print(f"  u_rep = {u_rep:.9f} kg")

    # 1.3. Incertidumbre por resolución del instrumento (u_res) en m³
    resolucion_instrumento_ul = constantes.get('div_min_valor', 0)
    print(f"  Resolución instrumento: {resolucion_instrumento_ul} µL")
    u_res_m3 = (resolucion_instrumento_ul / 1e9) / math.sqrt(12)
    print(f"  u_res = {u_res_m3:.12f} m³")

    # 1.4. Incertidumbre por temperatura del agua (u_temp_agua) en °C
    u_temp_agua_C = 0.1 / math.sqrt(3)
    print(f"  u_temp_agua = {u_temp_agua_C:.6f} °C")

    # --- 2. COEFICIENTES DE SENSIBILIDAD (c_i) ---
    print("\n2. COEFICIENTES DE SENSIBILIDAD:")
    
    volumenes_corregidos_m3 = [v / 1e9 for v in volumenes_corregidos_ul]
    avg_vol_m3 = sum(volumenes_corregidos_m3) / len(volumenes_corregidos_m3) if volumenes_corregidos_m3 else 0
    avg_masa_kg = sum(masas_kg) / len(masas_kg) if masas_kg else 0
    
    print(f"  Volumen promedio: {avg_vol_m3:.9f} m³")
    print(f"  Masa promedio: {avg_masa_kg:.6f} kg")
    print(f"  Alpha material: {constantes['alpha_material_pp']}")
    
    c_masa = - (avg_vol_m3 / avg_masa_kg) if avg_masa_kg != 0 else 0
    print(f"  c_masa = -{avg_vol_m3:.9f} / {avg_masa_kg:.6f} = {c_masa:.6f} m³/kg")
    
    c_temp_agua = -avg_vol_m3 * constantes['alpha_material_pp']
    print(f"  c_temp_agua = -{avg_vol_m3:.9f} * {constantes['alpha_material_pp']} = {c_temp_agua:.12f} m³/°C")

    # --- 3. CONTRIBUCIONES A LA INCERTIDUMBRE COMBINADA ---
    print("\n3. CONTRIBUCIONES:")
    
    u_y_cal = c_masa * u_cal
    u_y_rep = c_masa * u_rep
    u_y_res = u_res_m3
    u_y_temp_agua = c_temp_agua * u_temp_agua_C
    
    print(f"  u_y_cal = {c_masa:.6f} * {u_cal:.9f} = {u_y_cal:.12f} m³")
    print(f"  u_y_rep = {c_masa:.6f} * {u_rep:.9f} = {u_y_rep:.12f} m³")
    print(f"  u_y_res = {u_y_res:.12f} m³")
    print(f"  u_y_temp_agua = {c_temp_agua:.12f} * {u_temp_agua_C:.6f} = {u_y_temp_agua:.12f} m³")

    # El resto de la función de diagnóstico sigue la misma lógica que `calcular_incertidumbre`
    # y no necesita cambios para esta demostración.
    # ...

# --- FUNCIÓN PRINCIPAL ---

def procesar_todos_los_aforos(data):
    """
    Función principal que orquesta todo el proceso de cálculo.
    """
    constantes = data['constantes']
    entradas_generales = data['entradas_generales']
    especificaciones_patrones = data.get('especificaciones_patrones', {})
    debug_mode = entradas_generales.get('debug_mode', False)
    # Añadir la resolución del instrumento a las constantes para usarla en el cálculo de incertidumbre
    constantes['div_min_valor'] = entradas_generales.get('div_min_valor', 0)

    site_config = data.get('site_config', {})
    resultados_por_aforo = []

    promedios_ambientales_aforos = []
    # Obtener el valor nominal del último aforo, que se usará como divisor
    valor_nominal_canal_3 = data['aforo3']['valor_nominal']

    for i in range(1, 4):
        aforo_key = f'aforo{i}'
        aforo_data = data[aforo_key]
        
        promedios_ambientales = corregir_y_promediar_condiciones(
            aforo_data['mediciones_ambientales'],
            constantes
        )
        promedios_ambientales_aforos.append(promedios_ambientales)
        
        factores = calcular_factores_de_correccion(
            promedios_ambientales,
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
        
        if debug_mode:
            # Llamamos a la función de diagnóstico que imprimirá todo en la consola del servidor
            diagnosticar_incertidumbre(aforo_data, factores, promedios_ambientales, espec_patron, constantes, volumenes_corregidos_ul, i)

        incertidumbre = calcular_incertidumbre(aforo_data, factores, promedios_ambientales, espec_patron, constantes, volumenes_corregidos_ul)
        
        if not volumenes_corregidos_ul:
            promedio_volumen = 0
        else:
            promedio_volumen = sum(volumenes_corregidos_ul) / len(volumenes_corregidos_ul)
            
        error_medida = promedio_volumen - aforo_data['valor_nominal']
        
        # Calcular el error de medida en porcentaje
        error_porcentaje = 0
        if valor_nominal_canal_3 != 0: # Usar siempre el valor del canal 3 como divisor
            error_porcentaje = abs(error_medida / valor_nominal_canal_3) * 100

        resultados_por_aforo.append({
            "valor_nominal": aforo_data['valor_nominal'],
            "promedio_volumen_ul": promedio_volumen,
            "error_medida_ul": error_medida,
            "mediciones_volumen_ul": volumenes_corregidos_ul,
            "error_medida_porcentaje": error_porcentaje,
            "incertidumbre_expandida": incertidumbre,
            "emt": None # Placeholder para el cálculo futuro
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
