import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
// 🛑 IMPORTAMOS LA LIBRERÍA ESPECÍFICA
import { encode } from '@toon-format/toon'; 

// Helper para obtener el __dirname en módulos ES
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// --- Rutas de Archivos ---
const INPUT_DIR = path.join(__dirname, 'src', 'app', 'data');
const OUTPUT_DIR = INPUT_DIR; 

// 🛑 CAMBIAMOS LA EXTENSIÓN A .toon
const OUTPUT_EXT = '.toon'; 

/**
 * Función para transformar la data de un archivo individual ANTES de serializar.
 * @param {object} inputData - El objeto JSON leído del archivo.
 * @returns {object} El objeto que será serializado en formato TOON.
 */
function transformData(inputData) {
    // ------------------------------------------------------------------
    // AÑADE AQUÍ LA LÓGICA DE PRE-TRANSFORMACIÓN si es necesario.
    // Ej: Asegurar que el objeto raíz sea un mapa o un array específico.
    // Si quieres convertir todo el contenido del JSON sin cambiar su estructura, 
    // simplemente devuelve inputData:
    return inputData; 
    // ------------------------------------------------------------------
}

/**
 * Función principal que escanea el directorio y procesa los archivos.
 */
async function processAllFiles() {
    console.log(`[INFO] Scanning directory: ${INPUT_DIR}`);

    try {
        // ... (Verificación de directorio y lectura de archivos, igual que antes) ...
        const files = await fs.readdir(INPUT_DIR);
        const jsonFiles = files.filter(file => path.extname(file) === '.json');

        // ... (Manejo de archivos no encontrados, igual que antes) ...

        for (const fileName of jsonFiles) {
            const inputFile = path.join(INPUT_DIR, fileName);
            const baseName = path.parse(fileName).name; 
            const outputFileName = baseName + OUTPUT_EXT;
            const outputFile = path.join(OUTPUT_DIR, outputFileName);
            
            try {
                // Leer el JSON
                const rawData = await fs.readFile(inputFile, 'utf8');
                const inputData = JSON.parse(rawData);
                
                // 1. Pre-Transformar (si es necesario)
                const objectToEncode = transformData(inputData);

                // 2. 🛑 SERIALIZAR A FORMATO TOON usando la librería
                // El resultado 'toonData' suele ser un ArrayBuffer o Buffer
                const toonData = encode(objectToEncode); 
                
                // 3. Escribir el archivo binario/formato TOON
                // No usamos 'utf8' aquí, escribimos el buffer directamente
                await fs.writeFile(outputFile, toonData); 
                
                console.log(`\t✅ Processed: ${fileName} -> ${outputFileName}`);

            } catch (error) {
                console.error(`\t❌ ERROR processing ${fileName}: ${error.message}`);
            }
        }

        console.log('\n[SUCCESS] Conversion of all files completed.');

    } catch (error) {
        console.error(`[FATAL ERROR] Main operation failed: ${error.message}`);
        process.exit(1);
    }
}

processAllFiles();