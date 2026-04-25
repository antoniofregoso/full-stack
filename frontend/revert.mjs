import { promises as fs } from 'fs';
import path from 'path';
import fsSync from 'fs';
import { fileURLToPath } from 'url';
// 🛑 IMPORTAMOS LA FUNCIÓN DE DECODIFICACIÓN
import { decode } from '@toon-format/toon'; 

// Helper para obtener el __dirname en módulos ES
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// --- Rutas de Archivos ---
const INPUT_DIR = path.join(__dirname, 'src', 'app', 'data'); 
const OUTPUT_DIR = INPUT_DIR; // Guardamos en la misma carpeta 

const INPUT_EXT = '.toon';
const OUTPUT_EXT = '.json'; // Queremos una salida JSON

/**
 * Función que escanea el directorio y procesa los archivos .toon.
 */
async function processAllFilesToJson() {
    console.log(`[INFO] Scanning directory: ${INPUT_DIR} for files ${INPUT_EXT}`);

    try {
        // 1. Verificar directorio
        if (!fsSync.existsSync(INPUT_DIR)) {
            console.error(`[ERROR] Directory of input not found: ${INPUT_DIR}`);
            process.exit(1);
        }

        // 2. Leer y filtrar archivos .toon
        const files = await fs.readdir(INPUT_DIR);
        const toonFiles = files.filter(file => path.extname(file) === INPUT_EXT);

        if (toonFiles.length === 0) {
            console.warn(`[WARNING] No files ${INPUT_EXT} found to process.`);
            return;
        }

        console.log(`[INFO] Found ${toonFiles.length} files ${INPUT_EXT}. Starting conversion to JSON...`);
        for (const fileName of toonFiles) {
            const inputFile = path.join(INPUT_DIR, fileName);
            
            // Obtener el nombre base (ej. 'home' de 'home.toon')
            const baseName = path.parse(fileName).name; 
            
            // Crear el nombre del archivo de salida (ej. 'home.json')
            const outputFileName = baseName + OUTPUT_EXT;
            const outputFile = path.join(OUTPUT_DIR, outputFileName);
            
            try {
                // 1. Leer el archivo como CADENA DE TEXTO (utf8)
                // Esto es NECESARIO si la librería 'decode' espera un string para parsear TOML
                const toonDataString = await fs.readFile(inputFile, 'utf8'); 
                
                // 2. 🛑 DECODIFICAR
                // Pasamos el string, no el Buffer
                const decodedObject = decode(toonDataString); 
                
                // 3. Serializar de nuevo a JSON con formato legible (indentación de 2)
                const jsonString = JSON.stringify(decodedObject, null, 2); 
                
                // 4. Escribir el nuevo archivo JSON
                await fs.writeFile(outputFile, jsonString, 'utf8');
                
                console.log(`\t✅ Processed: ${fileName} -> ${outputFileName}`);

            } catch (error) {
                console.error(`\t❌ ERROR processing ${fileName}: ${error.message}`);
            }
        }

        console.log('\n[SUCCESS] Conversion of TOON to JSON completed.');
    } catch (error) {
        console.error(`[FATAL ERROR] Main operation failed: ${error.message}`);
        process.exit(1);
    }
}

processAllFilesToJson();