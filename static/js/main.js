// --- LÓGICA DE LA INTERFAZ ---

// --- CONFIGURACIÓN ---
const API_BASE_URL = 'http://127.0.0.1:5000';
let myChart = null;

// --- LÓGICA DE LA INTERFAZ ---

function changeTab(tabIndex) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
    document.getElementById(`tab-${tabIndex}`).classList.add('active');
    document.querySelector(`button[onclick="changeTab(${tabIndex})"]`).classList.add('active');
}

const testData = {
    header: {
        nombre_cliente: "Facultad de Química - UNAM",
        fecha_recepcion: "2025-09-24",
        fecha_calibracion: "2025-09-26",
        descripcion_instrumento: "PIPETA DE PISTÓN",
        clase_instrumento: "N.A.",
        tipo_instrumento: "ANALOGICO",
        marca_instrumento: "GILSON",
        vol_nominal: 20,
        tipo_volumen: "VARIABLE",
        t_descarga: "N.A.",
        modelo_instrumento: "PIPETMAN",
        unidades: "µL",
        tipo_calibracion: "TD",
        cuello_instrumento: "N.A.",
        serie_instrumento: "B-84-19726",
        div_min_valor: 0.02,
        div_min_unidad: "µL",
        puntas_valor: 20,
        puntas_unidad: "µL",
        id_instrumento: "S / ID",
        tolerancia: "N.A.",
        material: "PP",
        numero_servicio: "0046/2025/VOL",
        numero_certificado: "CAL-0216-2025/VOL",
        patron_seleccionado: "CAL-VO-002",
        auxiliar_ta: "CAL-VO-005",
        auxiliar_ca: "CAL-VO-051",
        limpieza: "OK",
        direccion_cliente_reporte: "Cto. Escolar S/N, C.U., Coyoacán",
        correo_cliente_reporte: "contacto@quimica.unam.mx",
        telefono_cliente_reporte: "5622-3696",
        contacto_reporte_directo: "Dr. J. de Jesús García",
        intervalo_min_reporte: 2,
        intervalo_max_reporte: 20,
        cotizacion: "COT-00500-01",
        observaciones: "Se realizó limpieza y lubricación del instrumento.",
        ajuste_realizado: "N",
    },
    condiciones_iniciales: {
        promedio1: 2.01,
        promedio2: 9.99,
        promedio3: 19.95,
    },
    aforos: [
        { punta: "20 µL", pasos: "1", mediciones: [
            { vacio: 0.0000, lleno: 0.001985, temp_agua: 19.0, temp_amb: 19.1, presion: 783.4, humedad: 53.1 },
            { vacio: 0.0000, lleno: 0.001982, temp_agua: 19.0, temp_amb: 19.1, presion: 783.4, humedad: 53.2 },
            { vacio: 0.0000, lleno: 0.002018, temp_agua: 19.0, temp_amb: 19.0, presion: 783.4, humedad: 53.3 },
            { vacio: 0.0000, lleno: 0.001990, temp_agua: 19.0, temp_amb: 19.0, presion: 783.4, humedad: 53.4 },
            { vacio: 0.0000, lleno: 0.002069, temp_agua: 19.0, temp_amb: 19.1, presion: 783.4, humedad: 53.5 },
            { vacio: 0.0000, lleno: 0.001941, temp_agua: 19.0, temp_amb: 19.1, presion: 783.4, humedad: 53.4 },
            { vacio: 0.0000, lleno: 0.002028, temp_agua: 19.0, temp_amb: 19.1, presion: 783.4, humedad: 53.2 },
            { vacio: 0.0000, lleno: 0.002036, temp_agua: 19.0, temp_amb: 19.1, presion: 783.4, humedad: 53.3 },
            { vacio: 0.0000, lleno: 0.002038, temp_agua: 19.0, temp_amb: 19.1, presion: 783.4, humedad: 53.4 },
            { vacio: 0.0000, lleno: 0.001942, temp_agua: 19.0, temp_amb: 19.1, presion: 783.4, humedad: 53.2 },
        ]},
        { punta: "20 µL", pasos: "1", mediciones: [
            { vacio: 0.0000, lleno: 0.009920, temp_agua: 19.0, temp_amb: 19.1, presion: 783.3, humedad: 53.5 },
            { vacio: 0.0000, lleno: 0.009931, temp_agua: 19.0, temp_amb: 19.1, presion: 783.3, humedad: 53.5 },
            { vacio: 0.0000, lleno: 0.010010, temp_agua: 19.1, temp_amb: 19.1, presion: 783.3, humedad: 53.6 },
            { vacio: 0.0000, lleno: 0.010019, temp_agua: 19.0, temp_amb: 19.1, presion: 783.3, humedad: 53.6 },
            { vacio: 0.0000, lleno: 0.009957, temp_agua: 19.1, temp_amb: 19.1, presion: 783.3, humedad: 53.7 },
            { vacio: 0.0000, lleno: 0.010059, temp_agua: 19.0, temp_amb: 19.1, presion: 783.2, humedad: 53.8 },
            { vacio: 0.0000, lleno: 0.010038, temp_agua: 19.0, temp_amb: 19.2, presion: 783.2, humedad: 53.8 },
            { vacio: 0.0000, lleno: 0.009977, temp_agua: 19.1, temp_amb: 19.1, presion: 783.2, humedad: 53.9 },
            { vacio: 0.0000, lleno: 0.009973, temp_agua: 19.0, temp_amb: 19.2, presion: 783.2, humedad: 53.9 },
            { vacio: 0.0000, lleno: 0.010015, temp_agua: 19.0, temp_amb: 19.1, presion: 783.2, humedad: 54.0 },
        ]},
        { punta: "20 µL", pasos: "1", mediciones: [
            { vacio: 0.0000, lleno: 0.020041, temp_agua: 19.1, temp_amb: 19.4, presion: 783.1, humedad: 54.0 },
            { vacio: 0.0000, lleno: 0.020001, temp_agua: 19.1, temp_amb: 19.4, presion: 783.1, humedad: 54.0 },
            { vacio: 0.0000, lleno: 0.019860, temp_agua: 19.1, temp_amb: 19.4, presion: 783.1, humedad: 54.1 },
            { vacio: 0.0000, lleno: 0.019826, temp_agua: 19.1, temp_amb: 19.3, presion: 783.1, humedad: 54.2 },
            { vacio: 0.0000, lleno: 0.019852, temp_agua: 19.1, temp_amb: 19.3, presion: 783.1, humedad: 54.2 },
            { vacio: 0.0000, lleno: 0.019860, temp_agua: 19.1, temp_amb: 19.3, presion: 783.1, humedad: 54.1 },
            { vacio: 0.0000, lleno: 0.019906, temp_agua: 19.1, temp_amb: 19.4, presion: 783.0, humedad: 54.2 },
            { vacio: 0.0000, lleno: 0.019905, temp_agua: 19.1, temp_amb: 19.4, presion: 783.0, humedad: 54.3 },
            { vacio: 0.0000, lleno: 0.019963, temp_agua: 19.1, temp_amb: 19.5, presion: 783.0, humedad: 54.4 },
            { vacio: 0.0000, lleno: 0.019954, temp_agua: 19.1, temp_amb: 19.4, presion: 783.0, humedad: 54.4 },
        ]}
    ]
};

function clearForm() {
    document.getElementById('main-form').reset();
    document.getElementById('results-container').classList.add('hidden');
    document.getElementById('certificate-container').classList.add('hidden');
    document.getElementById('status-message').textContent = '';
    changeTab(1);
    updateAforoHeaders();
    if (myChart) {
        myChart.destroy();
    }
    // Resetear fechas a valores por defecto
    document.getElementById('fecha_calibracion').valueAsDate = new Date();
    const fechaRecepcion = new Date();
    fechaRecepcion.setDate(fechaRecepcion.getDate() - 2);
    document.getElementById('fecha_recepcion').valueAsDate = fechaRecepcion;
    document.getElementById('div_min_valor').dispatchEvent(new Event('input'));
}

function autocompleteWithTestData() {
    // Autocompletar encabezado y otras secciones
    const headerData = testData.header;
    for (const key in headerData) {
        const el = document.getElementById(key);
        if (el) {
            el.value = headerData[key];
            el.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
    
    // Autocompletar mediciones de aforos
    for (let a = 1; a <= 3; a++) {
        const aforoData = testData.aforos[a-1];
        document.getElementById(`aforo${a}-punta`).value = aforoData.punta;
        document.getElementById(`aforo${a}-pasos`).value = aforoData.pasos;

        for (let i = 1; i <= 10; i++) {
            const med = aforoData.mediciones[i - 1];
            document.getElementById(`aforo${a}-vacio-${i}`).value = med.vacio.toFixed(4);
            document.getElementById(`aforo${a}-lleno-${i}`).value = med.lleno.toFixed(6);
            document.getElementById(`aforo${a}-lleno-${i}`).dispatchEvent(new Event('input'));

            document.getElementById(`aforo${a}-temp_agua-${i}`).value = med.temp_agua.toFixed(1);
            document.getElementById(`aforo${a}-temp_amb-${i}`).value = med.temp_amb.toFixed(1);
            document.getElementById(`aforo${a}-presion-${i}`).value = med.presion.toFixed(1);
            document.getElementById(`aforo${a}-humedad-${i}`).value = med.humedad.toFixed(1);
        }
    }
    
    // Autocompletar tabla de condiciones iniciales
    document.getElementById('inicial-promedio-1').value = testData.condiciones_iniciales.promedio1;
    document.getElementById('inicial-promedio-2').value = testData.condiciones_iniciales.promedio2;
    document.getElementById('inicial-promedio-3').value = testData.condiciones_iniciales.promedio3;
}

function updateAforoHeaders() {
    const volNominal = parseFloat(document.getElementById('vol_nominal').value) || 0;
    const aforo1_nom = (volNominal / 10).toFixed(2);
    const aforo2_nom = (volNominal / 2).toFixed(2);
    const aforo3_nom = volNominal.toFixed(2);
    
    document.getElementById('aforo1-vol_nom').value = aforo1_nom;
    document.getElementById('aforo2-vol_nom').value = aforo2_nom;
    document.getElementById('aforo3-vol_nom').value = aforo3_nom;
    
    document.getElementById('inicial-nominal-1-display').value = aforo1_nom;
    document.getElementById('inicial-nominal-2-display').value = aforo2_nom;
    document.getElementById('inicial-nominal-3-display').value = aforo3_nom;
}

function generateAforoContent(containerId, aforoIndex) {
    const container = document.getElementById(containerId);
    
    // Crear encabezado del aforo
    const headerHtml = `
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4 p-4 border rounded-md bg-gray-50">
            <div>
                <label for="aforo${aforoIndex}-vol_nom" class="block text-sm font-medium text-gray-700">VOL. NOM.</label>
                <input type="text" id="aforo${aforoIndex}-vol_nom" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm bg-gray-200 sm:text-sm" readonly>
            </div>
            <div>
                <label for="aforo${aforoIndex}-punta" class="block text-sm font-medium text-gray-700">PUNTA</label>
                <input type="text" id="aforo${aforoIndex}-punta" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm">
            </div>
            <div>
                <label for="aforo${aforoIndex}-pasos" class="block text-sm font-medium text-gray-700">PASOS</label>
                <input type="text" id="aforo${aforoIndex}-pasos" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm">
            </div>
        </div>
    `;

    // Crear tabla
    let tableHtml = `
        <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
                <tr>
                    <th class="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">No.</th>
                    <th class="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">VACÍO (g)</th>
                    <th class="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">LLENO (g)</th>
                    <th class="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">MASA (g)</th>
                    <th class="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">TEMP. AGUA (°C)</th>
                    <th class="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">TEMP. AMB. (°C)</th>
                    <th class="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">PRESIÓN (hPa)</th>
                    <th class="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">HUMEDAD (%)</th>
                </tr>
            </thead>
            <tbody id="aforo${aforoIndex}-mediciones" class="bg-white divide-y divide-gray-200">
    `;
    
    for (let i = 1; i <= 10; i++) {
        tableHtml += `
            <tr>
                <td class="px-2 py-1 whitespace-nowrap text-sm font-medium text-gray-900">${i}</td>
                <td class="px-2 py-1"><input type="number" step="0.0001" id="aforo${aforoIndex}-vacio-${i}" class="w-full rounded-md border-gray-300 shadow-sm text-sm"></td>
                <td class="px-2 py-1"><input type="number" step="0.000001" id="aforo${aforoIndex}-lleno-${i}" class="w-full rounded-md border-gray-300 shadow-sm text-sm"></td>
                <td class="px-2 py-1"><input type="number" step="0.0001" id="aforo${aforoIndex}-m-${i}" class="w-full rounded-md border-gray-300 shadow-sm bg-gray-100 text-sm" readonly></td>
                <td class="px-2 py-1"><input type="number" step="0.1" id="aforo${aforoIndex}-temp_agua-${i}" class="w-full rounded-md border-gray-300 shadow-sm text-sm"></td>
                <td class="px-2 py-1"><input type="number" step="0.1" id="aforo${aforoIndex}-temp_amb-${i}" class="w-full rounded-md border-gray-300 shadow-sm text-sm"></td>
                <td class="px-2 py-1"><input type="number" step="0.1" id="aforo${aforoIndex}-presion-${i}" class="w-full rounded-md border-gray-300 shadow-sm text-sm"></td>
                <td class="px-2 py-1"><input type="number" step="0.1" id="aforo${aforoIndex}-humedad-${i}" class="w-full rounded-md border-gray-300 shadow-sm text-sm"></td>
            </tr>
        `;
    }
    
    tableHtml += '</tbody></table>';
    container.innerHTML = headerHtml + tableHtml;

    // Añadir listeners para el cálculo automático de m = lleno - vacio
    for (let i = 1; i <= 10; i++) {
        const vacio_el = document.getElementById(`aforo${aforoIndex}-vacio-${i}`);
        const lleno_el = document.getElementById(`aforo${aforoIndex}-lleno-${i}`);
        const m_el = document.getElementById(`aforo${aforoIndex}-m-${i}`);
        
        const calculateM = () => {
            const vacio = parseFloat(vacio_el.value) || 0;
            const lleno = parseFloat(lleno_el.value) || 0;
            m_el.value = (lleno - vacio).toFixed(6);
        };
        
        vacio_el.addEventListener('input', calculateM);
        lleno_el.addEventListener('input', calculateM);
    }
}

// --- LÓGICA DE CÁLCULO (FASE 3) ---

function collectFormData() {
    const volNominal = parseFloat(document.getElementById('vol_nominal').value);
    const data = {
        constantes: {
            a_temp_agua: 0.0062, b_temp_agua: -0.2566, c_temp_agua: 2.8131,
            a_temp_amb: -0.03, b_temp_amb: 1.2487, c_temp_amb: -12.859,
            a_presion: -0.000003, b_presion: 0.0043, c_presion: -1.1253,
            a_humedad: 0.0045, b_humedad: -0.4757, c_humedad: 10.806,
            rho_agua_o37: 999.85308, rho_agua_o33: 16.887, rho_agua_o34: 282.5,
            rho_agua_o35: 522500, rho_agua_o36: 69.348, rho_agua_o55: 0,
            rho_aire_o51: 0.34848, rho_aire_o52: 0.009, rho_aire_o53: 0.061, rho_aire_o54: 0,
            alpha_material_pp: 0.00024, rho_pesa_n74: 8000,
        },
        entradas_generales: {
            descripcion_instrumento: document.getElementById('descripcion_instrumento').value,
            marca_instrumento: document.getElementById('marca_instrumento').value,
            modelo_instrumento: document.getElementById('modelo_instrumento').value,
            serie_instrumento: document.getElementById('serie_instrumento').value,
            id_instrumento: document.getElementById('id_instrumento').value,
            unidades: document.getElementById('unidades').value,
            tipo_instrumento: document.getElementById('tipo_instrumento').value,
            tipo_volumen: document.getElementById('tipo_volumen').value,
            tipo_calibracion: document.getElementById('tipo_calibracion').value,
            ajuste_realizado: document.getElementById('ajuste_realizado').value,
            patron_seleccionado: document.getElementById('patron_seleccionado').value,
            auxiliar_ta: document.getElementById('auxiliar_ta').value,
            auxiliar_ca: document.getElementById('auxiliar_ca').value,
            mantenimientos: Array.from(document.querySelectorAll('input[name="mantenimiento"]:checked')).map(el => el.value),
            condiciones_iniciales: {
                promedio1: parseFloat(document.getElementById('inicial-promedio-1').value),
                promedio2: parseFloat(document.getElementById('inicial-promedio-2').value),
                promedio3: parseFloat(document.getElementById('inicial-promedio-3').value),
            }
        }
    };

    for (let a = 1; a <= 3; a++) {
        const medicionesMasa = [];
        const medicionesAmbientales = [];
        for (let i = 1; i <= 10; i++) {
            // Ahora usamos la columna 'm' calculada
            medicionesMasa.push(parseFloat(document.getElementById(`aforo${a}-m-${i}`).value));
            medicionesAmbientales.push({
                temp_agua: parseFloat(document.getElementById(`aforo${a}-temp_agua-${i}`).value),
                temp_amb: parseFloat(document.getElementById(`aforo${a}-temp_amb-${i}`).value),
                presion: parseFloat(document.getElementById(`aforo${a}-presion-${i}`).value),
                humedad: parseFloat(document.getElementById(`aforo${a}-humedad-${i}`).value),
            });
        }
        let valor_nominal_aforo;
        if (a === 1) valor_nominal_aforo = volNominal / 10;
        else if (a === 2) valor_nominal_aforo = volNominal / 2;
        else valor_nominal_aforo = volNominal;
        
        data[`aforo${a}`] = {
            valor_nominal: valor_nominal_aforo,
            mediciones_masa: medicionesMasa,
            mediciones_ambientales: medicionesAmbientales,
        };
    }
    return data;
}

function validateForm() {
    const requiredFields = [];
    let firstInvalidTab = -1;

    // Limpiar estilos de error previos
    document.querySelectorAll('.border-red-500').forEach(el => el.classList.remove('border-red-500', 'border-2'));

    // Validar campos de mediciones en los aforos
    for (let a = 1; a <= 3; a++) {
        for (let i = 1; i <= 10; i++) {
            const fieldsToCheck = [
                `aforo${a}-vacio-${i}`, `aforo${a}-lleno-${i}`,
                `aforo${a}-temp_agua-${i}`, `aforo${a}-temp_amb-${i}`,
                `aforo${a}-presion-${i}`, `aforo${a}-humedad-${i}`
            ];
            fieldsToCheck.forEach(fieldId => {
                const el = document.getElementById(fieldId);
                if (el && el.value.trim() === '') {
                    requiredFields.push(el);
                    if (firstInvalidTab === -1) firstInvalidTab = a;
                }
            });
        }
    }

    if (requiredFields.length > 0) {
        const statusMsg = document.getElementById('status-message');
        statusMsg.textContent = `Error: Faltan ${requiredFields.length} datos obligatorios en las mediciones. Por favor, complete los campos resaltados.`;
        statusMsg.className = 'text-sm font-medium text-red-600';

        requiredFields.forEach(el => {
            el.classList.add('border-red-500', 'border-2');
        });

        // Cambiar a la primera pestaña con errores
        if (firstInvalidTab !== -1) changeTab(firstInvalidTab);
        return false; // Validación fallida
    }
    return true; // Validación exitosa
}

async function handleGenerateReport() {
    const btn = document.getElementById('generar-reporte-btn');
    const statusMsg = document.getElementById('status-message');
    const resultsContainer = document.getElementById('results-container');
    
    // Limpiar mensajes de estado previos
    statusMsg.textContent = '';
    statusMsg.className = 'text-sm font-medium';

    // Ejecutar la validación antes de continuar
    if (!validateForm()) {
        return; // Detener si la validación falla
    }

    btn.disabled = true;
    btn.querySelector('span').textContent = 'Calculando...';
    const loader = document.createElement('div');
    loader.id = 'loader';
    btn.prepend(loader);

    statusMsg.textContent = 'Calculando...';
    statusMsg.className = 'text-sm font-medium text-gray-600';
    resultsContainer.classList.add('hidden');
    document.getElementById('certificate-container').classList.add('hidden');

    try {
        const formData = collectFormData();
        const response = await fetch(`${API_BASE_URL}/calcular`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Error del servidor: ${response.status}`);
        }

        const results = await response.json();
        displayResults(results);
        statusMsg.textContent = 'Reporte generado con éxito.';
        statusMsg.classList.add('text-green-600');

    } catch (error) {
        console.error('Error al generar el reporte:', error);
        statusMsg.textContent = `Error: ${error.message}`;
        statusMsg.classList.add('text-red-600');
    } finally {
        btn.disabled = false;
        btn.querySelector('span').textContent = 'Generar Reporte';
        if (btn.querySelector('#loader')) {
            btn.querySelector('#loader').remove();
        }
    }
}

function displayResults(results) {
    const serviceReportContainer = document.getElementById('results-container');
    const certificateContainer = document.getElementById('certificate-container');
    const unidades = results.textos_reporte.unidades || 'µL';
    
    let html = `
        <section class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <h2 class="text-xl font-semibold mb-4 border-b pb-2">Reporte de Servicio</h2>
            
            <!-- Condiciones Ambientales -->
            <h3 class="text-lg font-semibold mt-6 mb-2">Condiciones ambientales</h3>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 text-center p-4 border rounded-lg bg-gray-50">
                <div>
                    <p class="text-sm font-medium text-gray-700">Temperatura del líquido de calibración</p>
                    <p class="text-xs italic text-gray-500">Calibration liquid temperature</p>
                    <p class="text-lg font-bold text-blue-600 mt-1">${results.condiciones_finales.temp_liquido.toFixed(2)} °C</p>
                </div>
                <div>
                    <p class="text-sm font-medium text-gray-700">Temperatura ambiente</p>
                    <p class="text-xs italic text-gray-500">Ambient temperature</p>
                    <p class="text-lg font-bold text-blue-600 mt-1">${results.condiciones_finales.temp_ambiente.toFixed(2)} °C</p>
                </div>
                <div>
                    <p class="text-sm font-medium text-gray-700">Presión atmosférica</p>
                    <p class="text-xs italic text-gray-500">Atmospheric pressure</p>
                    <p class="text-lg font-bold text-blue-600 mt-1">${results.condiciones_finales.presion.toFixed(2)} hPa</p>
                </div>
                <div>
                    <p class="text-sm font-medium text-gray-700">Humedad Relativa</p>
                    <p class="text-xs italic text-gray-500">Relative humidity</p>
                    <p class="text-lg font-bold text-blue-600 mt-1">${results.condiciones_finales.humedad.toFixed(2)} %</p>
                </div>
            </div>
            
            <!-- Instrumentos Utilizados -->
            <h3 class="text-lg font-semibold mt-6 mb-2">Instrumentos utilizados</h3>
            <div class="text-sm p-4 border rounded-lg bg-gray-50 space-y-2">
                <p>
                    <strong>Patrones de Referencia:</strong> ${results.textos_reporte.especificacion_principal}
                </p>
                <div>
                    <strong>Equipo Auxiliar:</strong>
                    <ul class="list-disc list-inside pl-4 mt-1">
                        <li>${results.textos_reporte.especificacion_ta}</li>
                        <li>${results.textos_reporte.especificacion_ca}</li>
                    </ul>
                </div>
                <p>
                    <strong>Lugar de Servicio:</strong> ${results.textos_reporte.lugar_servicio}
                </p>
            </div>

            ${
                (results.textos_reporte.mantenimientos && results.textos_reporte.mantenimientos.length > 0)
                ? (() => {
                    const todasLasTareas = ["Limpieza externa", "Revisión de empaques", "Limpieza interna", "Lubricación", "Revisión de resortes", "Ajuste"];
                    const tareasRealizadas = new Set(results.textos_reporte.mantenimientos);
                    
                    const checkboxesHtml = todasLasTareas.map(tarea => {
                        const isChecked = tareasRealizadas.has(tarea);
                        const checkmarkSvg = `<svg class="w-4 h-4 text-white" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>`;
                        
                        return `
                            <div class="flex items-center space-x-2">
                                <div class="w-5 h-5 flex items-center justify-center rounded border ${isChecked ? 'bg-green-500 border-green-500' : 'border-gray-300'}">
                                    ${isChecked ? checkmarkSvg : ''}
                                </div>
                                <span>${tarea}</span>
                            </div>`;
                    }).join('');

                    return `<!-- Mantenimiento Realizado -->
                            <h3 class="text-lg font-semibold mt-6 mb-2">Mantenimiento Realizado</h3>
                            <div class="text-sm p-4 border rounded-lg bg-gray-50">
                                <div class="grid grid-cols-2 sm:grid-cols-3 gap-x-4 gap-y-2">
                                    ${checkboxesHtml}
                                </div>
                            </div>`;
                })()
                : ''
            }

            <!-- Tabla de Resumen -->
            <h3 class="text-lg font-semibold mt-6 mb-2">Resultados del Servicio</h3>
            <p class="text-sm text-gray-600 mb-4 p-4 border-l-4 border-blue-500 bg-blue-50">
                ${results.textos_reporte.introduccion}
            </p>

            <!-- Tabla de Mediciones Individuales -->
            <div class="mb-6">
                <table class="min-w-full divide-y divide-gray-200 border">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">No.</th>
                            ${results.aforos.map(aforo => `<th class="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">${aforo.valor_nominal.toFixed(2)} ${unidades}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        ${[...Array(10).keys()].map(i => `
                            <tr>
                                <td class="px-4 py-2 text-sm font-medium">${i + 1}</td>
                                <td class="px-4 py-2 text-sm text-center">
                                    ${results.aforos[0].mediciones_volumen_ul[i] ? results.aforos[0].mediciones_volumen_ul[i].toFixed(2) : 'N/A'}
                                </td>
                                <td class="px-4 py-2 text-sm text-center">
                                    ${results.aforos[1].mediciones_volumen_ul[i] ? results.aforos[1].mediciones_volumen_ul[i].toFixed(2) : 'N/A'}
                                </td>
                                <td class="px-4 py-2 text-sm text-center">
                                    ${results.aforos[2].mediciones_volumen_ul[i] ? results.aforos[2].mediciones_volumen_ul[i].toFixed(2) : 'N/A'}
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>


            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">CANAL</th>
                        <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Valor Nominal (${unidades})</th>
                        <th class="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase">VOLUMEN DEL *IBC (V20 °C) (${unidades})</th>
                        <th class="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase">Error de Medida (${unidades})</th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
    `;
    results.aforos.forEach((aforo, index) => {
        html += `
            <tr>
                <td class="px-4 py-2 text-sm">${index + 1}</td>
                <td class="px-4 py-2 text-sm">${aforo.valor_nominal.toFixed(2)}</td>
                <td class="px-4 py-2 text-sm">${aforo.promedio_volumen_ul.toFixed(2)}</td>
                <td class="px-4 py-2 text-sm font-medium ${aforo.error_medida_ul >= 0 ? 'text-blue-600' : 'text-red-600'}">${aforo.error_medida_ul.toFixed(2)}</td>
            </tr>
        `;
    });
    html += `
                </tbody>
            </table>

            <!-- Gráfico -->
            <h3 class="text-lg font-semibold mt-6 mb-2">Gráfico de Errores</h3>
            <div class="p-4 border rounded-lg bg-gray-50">
                 <canvas id="errorChart"></canvas>
            </div>

            <!-- Observaciones -->
             <h3 class="text-lg font-semibold mt-6 mb-2">Observaciones</h3>
             <p class="text-sm p-4 border rounded-lg bg-gray-50">${results.textos_reporte.observaciones}</p>
        </section>
    `;

    serviceReportContainer.innerHTML = html;
    serviceReportContainer.classList.remove('hidden');

    // --- Generar el contenido del Certificado ---
    // Por ahora, solo un marcador de posición.
    let certificateHtml = `
        <section class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <h2 class="text-xl font-semibold mb-4 border-b pb-2">Certificado de Calibración</h2>
            
            <!-- Trazabilidad Metrológica -->
            <h3 class="text-lg font-semibold mt-6 mb-2">
                Trazabilidad Metrológica
                <span class="block text-sm font-normal italic text-gray-500">Metrological Traceability</span>
            </h3>

            <div class="text-sm p-4 border rounded-lg bg-gray-50 space-y-3">
                <div>
                    <p>
                        <strong>Patrones de Referencia:</strong><br>
                        <em class="italic text-gray-500">Standards Used</em>
                    </p>
                    <p class="pl-4">
                        ${results.textos_reporte.especificacion_principal}
                    </p>
                </div>
                <div>
                    <strong>Equipo auxiliar:</strong><br>
                    <em class="italic text-gray-500">Auxiliary equipment</em>
                    <ul class="list-disc list-inside pl-4 mt-1">
                        <li>${results.textos_reporte.especificacion_ta}</li>
                        <li>${results.textos_reporte.especificacion_ca}</li>
                    </ul>
                </div>
                <div>
                    <p>
                        <strong>Trazabilidad metrológica:</strong><br>
                        <em class="italic text-gray-500">Metrological Traceability</em>
                    </p>
                    <p class="pl-4">
                        ${results.textos_reporte.trazabilidad_nacional}
                    </p>
                </div>
                <div>
                    <p>
                        <strong>Procedimiento utilizado:</strong><br>
                        <em class="italic text-gray-500">Procedure used</em>
                    </p>
                    <p class="pl-4">
                        ${results.textos_reporte.procedimiento_utilizado}
                    </p>
                </div>
                <div>
                    <p>
                        <strong>Lugar de Calibración:</strong><br>
                        <em class="italic text-gray-500">Calibration Location</em>
                    </p>
                    <p class="pl-4">
                        ${results.textos_reporte.lugar_servicio}
                    </p>
                </div>
            </div>

            <!-- Resultados de la Calibración -->
            <h3 class="text-lg font-semibold mt-8 mb-2">
                Resultados de la Calibración
                <span class="block text-sm font-normal italic text-gray-500">Calibration Results</span>
            </h3>

            <p class="text-sm text-gray-600 mb-4 p-4 border-l-4 border-blue-500 bg-blue-50">
                ${results.textos_reporte.introduccion_certificado}
            </p>

            <!-- Tabla de Resultados del Certificado -->
            <div class="mb-6">
                <table class="min-w-full border text-center">
                    <thead class="bg-gray-50">
                        <tr class="divide-x divide-gray-200 text-xs font-medium text-gray-500 uppercase">
                            <th class="px-2 py-2">CANAL</th>
                            <th class="px-2 py-2">VALOR NOMINAL (${unidades})</th>
                            <th class="px-2 py-2">VOLUMEN DEL *IBC (V20 °C) (${unidades})</th>
                            <th class="px-2 py-2">ERROR DE MEDIDA (${unidades})</th>
                            <th class="px-2 py-2">ERROR DE MEDIDA (%)</th>
                            <th class="px-2 py-2">INCERTIDUMBRE EXPANDIDA (${unidades})</th>
                            <th class="px-2 py-2">EMT</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        ${results.aforos.map((aforo, index) => `
                            <tr class="divide-x divide-gray-200">
                                <td class="px-2 py-2 text-sm">${index + 1}</td>
                                <td class="px-2 py-2 text-sm">${aforo.valor_nominal.toFixed(2)}</td>
                                <td class="px-2 py-2 text-sm">${aforo.promedio_volumen_ul.toFixed(2)}</td>
                                <td class="px-2 py-2 text-sm font-medium ${aforo.error_medida_ul >= 0 ? 'text-blue-600' : 'text-red-600'}">
                                    ${aforo.error_medida_ul.toFixed(2)}
                                </td>
                                <td class="px-2 py-2 text-sm">
                                    ${aforo.error_medida_porcentaje !== null ? aforo.error_medida_porcentaje.toFixed(2) : 'N/A'}
                                </td>
                                <td class="px-2 py-2 text-sm">
                                    ${aforo.incertidumbre_expandida !== null ? aforo.incertidumbre_expandida.toFixed(3) : 'N/A'} 
                                </td>
                                <td class="px-2 py-2 text-sm">${aforo.emt !== null ? aforo.emt.toFixed(1) : 'N/A'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </section>
    `;

    certificateContainer.innerHTML = certificateHtml;
    certificateContainer.classList.remove('hidden');

    // Renderizar gráfico
    const ctx = document.getElementById('errorChart').getContext('2d');
    if(myChart) {
        myChart.destroy();
    }

    // Calcular el rango de los datos para añadir un "padding" a los ejes
    const xValues = results.aforos.map(a => a.promedio_volumen_ul);
    const yValues = results.aforos.map(a => a.error_medida_ul);

    const xMin = Math.min(...xValues);
    const xMax = Math.max(...xValues);
    const yMin = Math.min(...yValues);
    const yMax = Math.max(...yValues);

    const xRange = xMax - xMin;
    const yRange = yMax - yMin;

    // Añadir un 15% de espacio extra a cada lado de los ejes
    const xPadding = xRange > 0 ? xRange * 0.15 : 2;
    const yPadding = yRange > 0 ? yRange * 0.15 : 0.1;

    const suggestedXMax = xMax + xPadding;
    const suggestedYMax = yMax + yPadding;
    
    const scatterData = {
        datasets: [
            {
                label: 'Error de Medida',
                data: results.aforos.map(a => ({ x: a.promedio_volumen_ul, y: a.error_medida_ul })),
                backgroundColor: 'rgba(59, 130, 246, 0.8)',
                pointRadius: 6,
                pointHoverRadius: 8
            },
        ]
    };

    myChart = new Chart(ctx, {
        type: 'scatter',
        data: scatterData,
        options: {
            scales: {
                y: {
                    //beginAtZero: false, // Dejamos que Chart.js decida el mínimo o lo calculamos
                    max: suggestedYMax, // Establecer el máximo del eje Y con padding
                    title: { display: true, text: 'Error de medida µL' },
                    grace: '10%' // Alternativa: pedir a chart.js que añada un 10% de gracia
                },
                x: {
                    type: 'linear',
                    position: 'bottom',
                    max: suggestedXMax, // Establecer el máximo del eje X con padding
                    grace: '10%',
                    title: { display: true, text: 'VOLUMEN DEL *IBC (V20 °C)' }
                }
            },
            plugins: {
                legend: { 
                    display: false 
                },
                datalabels: {
                    display: true,
                    align: 'top',
                    offset: 5,
                    formatter: (value, context) => {
                        return value.x.toFixed(2); // Muestra el valor del eje X (Volumen) con 2 decimales
                    },
                    font: {
                        weight: 'bold'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return ` (Promedio: ${context.parsed.x.toFixed(4)} µL, Error: ${context.parsed.y.toFixed(4)} µL)`;
                        }
                    }
                }
            }
        }
    });
}

const syncFields = [ // CORREGIDO: IDs no existían, ahora se usan los correctos.
    { from: 'direccion_cliente_reporte', to: 'direccion_cliente' }, // Ejemplo, ajusta según tu necesidad
    { from: 'correo_cliente_reporte', to: 'correo_cliente' },
    { from: 'telefono_cliente_reporte', to: 'telefono_cliente' },
    { from: 'contacto_reporte_directo', to: 'contacto_reporte'},
];

document.addEventListener('DOMContentLoaded', () => {
    // Registrar el plugin de etiquetas de datos globalmente una sola vez.
    Chart.register(ChartDataLabels);

    generateAforoContent('tab-1', 1);
    generateAforoContent('tab-2', 2);
    generateAforoContent('tab-3', 3);
    
    document.getElementById('div_min_valor').addEventListener('input', (e) => {
        document.getElementById('resolucion').value = e.target.value;
    });

    document.getElementById('vol_nominal').addEventListener('input', updateAforoHeaders);

    document.getElementById('autocomplete-btn').addEventListener('click', autocompleteWithTestData);
    document.getElementById('generar-reporte-btn').addEventListener('click', handleGenerateReport);
    document.getElementById('clear-form-btn').addEventListener('click', clearForm);

    // Sincronizar campos entre secciones
    syncFields.forEach(pair => {
        const fromEl = document.getElementById(pair.from);
        const toEl = document.getElementById(pair.to);
        if(fromEl && toEl){
            fromEl.addEventListener('input', () => toEl.value = fromEl.value);
        }
    });
    
    // Carga inicial
    clearForm();
});